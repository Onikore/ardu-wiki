#!/usr/bin/env python3
"""Extract user-facing messages + param docs from ArduPilot source -> json."""
import os, re, sys, json, hashlib

ROOT = sys.argv[1]
OUT = sys.argv[2]
SKIP_DIRS = {"tests", "examples", "test", "SITL", "AP_HAL_SITL", "AP_HAL_Linux", "AP_HAL_QURT",
             "AP_HAL_ESP32", "AP_HAL_Empty", "hwdef", "Tools", "AP_Scripting", "AP_Periph"}
EXT = (".cpp", ".h", ".c")

CALLS = {
    "GCS_SEND_TEXT": "gcs",
    "send_text": "gcs",
    "send_textv": "gcs",
    "check_failed": "arm",
    "snprintf_fail": "fail",
}
call_re = re.compile(r"\b(GCS_SEND_TEXT|send_text|send_textv|check_failed|report_failure|"
                     r"set_failure_message|failure_msg_set|prearm_fail|fail_msg)\s*\(")
# generic snprintf into failure buffers
snp_re = re.compile(r"\b(?:hal\.util->snprintf|snprintf)\s*\(\s*(failure_msg|fail_msg|buffer|msg|failmsg|reason|error_msg|failure_message)\b")


def read(p):
    with open(p, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def scan_args(src, i):
    """src[i] == '(' ; return (list_of_args, end_index)."""
    depth = 0
    args = []
    cur = []
    j = i
    n = len(src)
    while j < n:
        c = src[j]
        if c == '"':
            k = j + 1
            while k < n and src[k] != '"':
                if src[k] == "\\":
                    k += 1
                k += 1
            cur.append(src[j:k + 1])
            j = k + 1
            continue
        if c == "'":
            k = j + 1
            while k < n and src[k] != "'":
                if src[k] == "\\":
                    k += 1
                k += 1
            cur.append(src[j:k + 1])
            j = k + 1
            continue
        if c == "/" and src[j:j + 2] == "//":
            k = src.find("\n", j)
            j = k if k != -1 else n
            continue
        if c == "/" and src[j:j + 2] == "/*":
            k = src.find("*/", j)
            j = k + 2 if k != -1 else n
            continue
        if c in "([{":
            depth += 1
            if depth > 1:
                cur.append(c)
        elif c in ")]}":
            depth -= 1
            if depth == 0:
                args.append("".join(cur).strip())
                return args, j
            cur.append(c)
        elif c == "," and depth == 1:
            args.append("".join(cur).strip())
            cur = []
        else:
            cur.append(c)
        j += 1
    return args, n


def literal(arg):
    """Concatenate adjacent string literals; return None if arg isn't one (allows macros)."""
    parts = re.findall(r'"((?:[^"\\]|\\.)*)"', arg)
    if not parts:
        return None
    rest = re.sub(r'"(?:[^"\\]|\\.)*"', "", arg)
    rest = re.sub(r"\bPSTR\b|\bFSTR\b|[\s()]", "", rest)
    if rest:
        # something other than literals (e.g. a macro / variable) -> mark partial
        pass
    s = "".join(parts)
    s = s.replace('\\"', '"').replace("\\n", " ").replace("\\t", " ").replace("\\\\", "\\")
    return s


def build_line_index(src):
    idx = [0]
    for m in re.finditer("\n", src):
        idx.append(m.end())
    return idx


def line_of(idx, pos):
    import bisect
    return bisect.bisect_right(idx, pos)


func_re = re.compile(r"^[A-Za-z_][\w:<>\*&\s,]*?\b((?:\w+::)*~?\w+)\s*\([^;{}]*\)\s*(?:const)?\s*(?:override)?\s*$")


def enclosing_func(lines, ln):
    for k in range(ln - 1, max(0, ln - 400), -1):
        L = lines[k]
        if L.startswith("{") or L.startswith("}"):
            if L.startswith("}"):
                return ""
            # find signature above
            for q in range(k - 1, max(0, k - 6), -1):
                s = lines[q].strip()
                m = re.search(r"((?:\w+::)+\w+|\w+)\s*\(", s)
                if m and not s.startswith(("//", "#")) and not s.endswith(";"):
                    return m.group(1)
    return ""


def severity_of(arg):
    m = re.search(r"MAV_SEVERITY_(\w+)", arg)
    return m.group(1) if m else None


PARAM_TOKEN = re.compile(r"\b([A-Z][A-Z0-9]{1,}(?:_[A-Z0-9]+)+|[A-Z]{2,}[0-9]*_[A-Z0-9_]+|%s_[A-Z0-9_]+)\b")
BLACK = {"MAV_SEVERITY", "RC_CHANNEL", "AP_HAL", "LOG_BITMASK"}


def main():
    msgs = {}
    for dp, dn, fn in os.walk(ROOT):
        dn[:] = [d for d in dn if d not in SKIP_DIRS and not d.startswith(".")]
        for f in fn:
            if not f.endswith(EXT):
                continue
            p = os.path.join(dp, f)
            rel = os.path.relpath(p, ROOT).replace("\\", "/")
            if rel.startswith("libraries/") and any(x in rel for x in ("/examples/", "/tests/", "AP_HAL_")):
                continue
            src = read(p)
            if not re.search(r"GCS_SEND_TEXT|send_text|check_failed|failure_msg|fail_msg|report_failure", src):
                continue
            idx = build_line_index(src)
            lines = src.split("\n")
            for m in call_re.finditer(src):
                name = m.group(1)
                op = src.find("(", m.end() - 1)
                args, end = scan_args(src, op)
                if not args:
                    continue
                sev = None
                fmt = None
                prefix = ""
                if name in ("GCS_SEND_TEXT", "send_text", "send_textv"):
                    sev = severity_of(args[0])
                    if len(args) < 2:
                        continue
                    fmt = literal(args[1])
                elif name == "check_failed":
                    sev = "CRITICAL"
                    # (check, report, fmt, ...) or (report, fmt, ...)
                    for a in args[:3]:
                        if '"' in a:
                            fmt = literal(a)
                            break
                    prefix = "PreArm: "
                else:
                    for a in args:
                        if '"' in a:
                            fmt = literal(a)
                            break
                    prefix = ""
                if not fmt or len(fmt.strip()) < 3:
                    continue
                ln = line_of(idx, m.start())
                # skip declarations/definitions of the function itself
                if "const char *fmt" in src[m.start():end + 1]:
                    continue
                ctxs = max(0, ln - 9)
                ctx = "\n".join(l.rstrip() for l in lines[ctxs:min(len(lines), ln + 2)])
                ctx = re.sub(r"\n{2,}", "\n", ctx)
                entry = dict(text=prefix + fmt, sev=sev or "", file=rel, line=ln,
                             func=enclosing_func(lines, ln), ctx=ctx[:900], kind=("arm" if prefix else "gcs"))
                key = (entry["text"], rel)
                if key in msgs:
                    msgs[key].setdefault("alts", []).append(ln)
                else:
                    msgs[key] = entry
            # snprintf into failure buffers
            for m in snp_re.finditer(src):
                op = src.find("(", m.start())
                args, end = scan_args(src, op)
                fmt = None
                for a in args[1:3]:
                    if '"' in a:
                        fmt = literal(a)
                        break
                if not fmt or len(fmt.strip()) < 3:
                    continue
                ln = line_of(idx, m.start())
                ctxs = max(0, ln - 9)
                ctx = "\n".join(l.rstrip() for l in lines[ctxs:min(len(lines), ln + 2)])
                entry = dict(text=fmt, sev="CRITICAL", file=rel, line=ln, func=enclosing_func(lines, ln),
                             ctx=ctx[:900], kind="fail")
                key = (fmt, rel)
                if key not in msgs:
                    msgs[key] = entry

    # --- param docs
    params = {}
    pblock = re.compile(r"//\s*@Param(?:\(([^)]*)\))?:\s*(\S+)\s*\n((?:\s*//\s*@.*\n|\s*//\s{1,}\S.*\n)*)")
    for dp, dn, fn in os.walk(ROOT):
        dn[:] = [d for d in dn if not d.startswith(".") and d not in ("tests", "examples")]
        for f in fn:
            if not f.endswith((".cpp", ".h")):
                continue
            p = os.path.join(dp, f)
            rel = os.path.relpath(p, ROOT).replace("\\", "/")
            if not (rel.startswith("ArduCopter/") or rel.startswith("libraries/")):
                continue
            src = read(p)
            if "@Param" not in src:
                continue
            for m in pblock.finditer(src):
                pname = m.group(2)
                body = m.group(3)
                d = {}
                for tag in ("DisplayName", "Description", "Range", "Units", "Values", "Bitmask", "Default", "User"):
                    mm = re.search(r"//\s*@" + tag + r":\s*(.*)", body)
                    if mm:
                        d[tag] = mm.group(1).strip()
                # multi-line Values/Bitmask: collect
                params.setdefault(pname, []).append(dict(file=rel, **d))

    # --- link params
    allp = {k: v for k, v in params.items()}
    out = []
    for (txt, rel), e in sorted(msgs.items(), key=lambda kv: (kv[1]["file"], kv[1]["line"])):
        toks = set()
        for t in PARAM_TOKEN.findall(e["text"] + "\n" + e["ctx"][-300:]):
            if t.startswith("%s_"):
                t = t[3:]
            if len(t) >= 4 and t not in BLACK:
                toks.add(t)
        linked = []
        lib = rel.split("/")[1] if rel.startswith("libraries/") else ""
        for t in sorted(toks):
            cand = None
            if t in allp:
                cand = (t, allp[t][0])
            else:
                for pn, lst in allp.items():
                    if len(pn) >= 4 and t.endswith("_" + pn):
                        for it in lst:
                            if lib and lib in it["file"]:
                                cand = (t, it)
                                break
                    if cand:
                        break
            if cand:
                linked.append(dict(name=cand[0], display=cand[1].get("DisplayName", ""),
                                   desc=cand[1].get("Description", ""), range=cand[1].get("Range", ""),
                                   values=cand[1].get("Values", ""), units=cand[1].get("Units", ""),
                                   default=cand[1].get("Default", "")))
        e["params"] = linked[:6]
        e["id"] = hashlib.md5((e["text"] + e["file"]).encode()).hexdigest()[:10]
        out.append(e)

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False)
    with open(OUT + ".params", "w", encoding="utf-8") as f:
        json.dump(params, f, ensure_ascii=False)
    print("messages:", len(out), "params:", len(params))


main()

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
snp_re = re.compile(r"\b(?:hal\.util->snprintf|snprintf)\s*\(\s*(failure_msg|fail_msg|buffer|msg|failmsg|reason|error_msg|failure_message|prearm_fail_string|temp_buffer)\b")


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



NL = chr(10)
SPEC_RE = re.compile(r"%[-+ #0-9.]*(?:l|h|ll|z)?[a-zA-Z%]")


def local_strings(lines, ln, back=80):
    """const char *name = "literal"; в пределах функции выше строки ln (1-based)."""
    out = {}
    for k in range(ln - 1, max(0, ln - back), -1):
        L = lines[k]
        if L.startswith("}") or re.match(r"^\w.*\)\s*(const)?\s*$", L):
            break
        m = re.search(r'const\s+char\s*\*\s*(\w+)\s*=\s*"((?:[^"\\]|\\.)*)"\s*;', L)
        if m:
            # при #if HELI / #else берём вариант для мультикоптера
            if m.group(1) not in out or out[m.group(1)] == "Collective":
                out[m.group(1)] = m.group(2)
    return out


def subst(fmt, rest_args, consts):
    """подставляет константные строки в %s, если аргумент - литерал или известная const char*."""
    res, ai, pos = [], 0, 0
    for m in SPEC_RE.finditer(fmt):
        res.append(fmt[pos:m.start()])
        spec = m.group(0)
        pos = m.end()
        if spec == "%%":
            res.append("%")
            continue
        arg = rest_args[ai].strip() if ai < len(rest_args) else ""
        ai += 1
        if spec.endswith("s"):
            lit = literal(arg) if arg.startswith('"') else None
            if lit is None and re.fullmatch(r"\w+", arg) and arg in consts:
                lit = consts[arg]
            res.append(lit if lit is not None else spec)
        else:
            res.append(spec)
    res.append(fmt[pos:])
    return "".join(res)


def condition_of(lines, ln):
    """ближайшее управляющее условие (if/else if/else/case) над строкой ln (1-based)."""
    call_ind = len(lines[ln - 1]) - len(lines[ln - 1].lstrip())
    for k in range(ln - 2, max(0, ln - 40), -1):
        L = lines[k]
        st = L.strip()
        if not st or st.startswith("//") or st.startswith("#"):
            continue
        ind = len(L) - len(L.lstrip())
        if ind >= call_ind:
            continue
        if re.match(r"(\}\s*)?(else\s+)?if\s*\(", st) or re.match(r"(\}\s*)?else\b", st) or st.startswith(("case ", "default:", "while", "for")):
            # собрать многострочное условие
            text = st
            depth = text.count("(") - text.count(")")
            q = k + 1
            while depth > 0 and q < len(lines) and q < k + 8:
                nxt = lines[q].strip()
                text += " " + nxt
                depth += nxt.count("(") - nxt.count(")")
                q += 1
            text = re.sub(r"\s*\{\s*$", "", text)
            if re.match(r"(\}\s*)?else\s*$", text):
                # найти парный if выше
                for k2 in range(k - 1, max(0, k - 60), -1):
                    L2 = lines[k2]
                    if len(L2) - len(L2.lstrip()) == ind and re.match(r"\s*(\}\s*)?(else\s+)?if\s*\(", L2):
                        return "else  (т.е. НЕ выполнено: " + re.sub(r"\s*\{\s*$", "", L2.strip()) + ")"
            return text
        if re.match(r"[\w:<>~\s\*&]+\([^;]*\)\s*(const)?\s*(override)?\s*\{?$", st) and ind == 0:
            break
    return ""


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
            if not re.search(r"GCS_SEND_TEXT|send_text|check_failed|failure_msg|fail_msg|report_failure|prearm_fail_string|temp_buffer|update_check|announce_failsafe", src):
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
                chk = ""
                if name in ("GCS_SEND_TEXT", "send_text", "send_textv"):
                    sev = severity_of(args[0])
                    if len(args) < 2:
                        continue
                    fmt = literal(args[1])
                    rest = args[2:]
                elif name == "check_failed":
                    sev = "CRITICAL"
                    mchk = re.search(r"ARMING_CHECK_(\w+)", args[0]) if args else None
                    chk = mchk.group(1) if mchk else ""
                    # (check, report, fmt, ...) or (report, fmt, ...)
                    rest = []
                    for ia, a in enumerate(args[:3]):
                        if '"' in a:
                            fmt = literal(a)
                            rest = args[ia + 1:]
                            break
                    prefix = "PreArm: "
                else:
                    rest = []
                    for ia, a in enumerate(args):
                        if '"' in a:
                            fmt = literal(a)
                            rest = args[ia + 1:]
                            break
                    prefix = ""
                if not fmt or len(fmt.strip()) < 3:
                    continue
                ln = line_of(idx, m.start())
                # skip declarations/definitions of the function itself
                if "const char *fmt" in src[m.start():end + 1]:
                    continue
                # "%s" + failure_msg: сам текст придёт из библиотеки, такие вызовы не нужны как отдельные записи
                if fmt.strip() == "%s":
                    continue
                fmt = subst(fmt, rest, local_strings(lines, ln))
                ctxs = max(0, ln - 9)
                ctx = "\n".join(l.rstrip() for l in lines[ctxs:min(len(lines), ln + 2)])
                ctx = re.sub(r"\n{2,}", "\n", ctx)
                entry = dict(text=prefix + fmt, sev=sev or "", file=rel, line=ln,
                             func=enclosing_func(lines, ln), ctx=ctx[:900], kind=("arm" if prefix else "gcs"),
                             chk=(chk if name == "check_failed" else ""), cond=condition_of(lines, ln))
                key = (entry["text"], rel)
                if key in msgs:
                    msgs[key].setdefault("alts", []).append(ln)
                else:
                    msgs[key] = entry
            # announce_failsafe("Radio", "Continuing Landing") -> реальные тексты
            for m in re.finditer(r'announce_failsafe\(\s*"([^"]+)"\s*(?:,\s*"([^"]+)")?\s*\)', src):
                ln = line_of(idx, m.start())
                t = m.group(1) + " Failsafe" + (" - " + m.group(2) if m.group(2) else "")
                ctxs = max(0, ln - 9)
                ctx = NL.join(l.rstrip() for l in lines[ctxs:min(len(lines), ln + 2)])
                key = (t, rel)
                if key not in msgs:
                    msgs[key] = dict(text=t, sev="WARNING", file=rel, line=ln, func=enclosing_func(lines, ln),
                                     ctx=ctx[:900], kind="gcs", cond=condition_of(lines, ln))
            # AP_BattMonitor: update_check(..., "below minimum arming voltage") -> "Battery %d <msg>"
            if rel.endswith("AP_BattMonitor_Backend.cpp"):
                for m in re.finditer(r'update_check\([^;]*?"([^"]+)"\s*\)', src):
                    ln = line_of(idx, m.start())
                    t = "Battery %d " + m.group(1)
                    ctxs = max(0, ln - 9)
                    ctx = NL.join(l.rstrip() for l in lines[ctxs:min(len(lines), ln + 2)])
                    msgs[(t, rel)] = dict(text=t, sev="CRITICAL", file=rel, line=ln, func=enclosing_func(lines, ln),
                                          ctx=ctx[:900], kind="fail", cond="update_check(..., failed) - флаг вычислен выше в arming_checks()")
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
                rest = []
                for ia, a in enumerate(args):
                    if '"' in a:
                        rest = args[ia + 1:]
                        break
                fmt = subst(fmt, rest, local_strings(lines, ln))
                entry = dict(text=fmt, sev="CRITICAL", file=rel, line=ln, func=enclosing_func(lines, ln),
                             ctx=ctx[:900], kind="fail", cond=condition_of(lines, ln), buf=m.group(1))
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

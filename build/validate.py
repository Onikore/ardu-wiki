# -*- coding: utf-8 -*-
"""Проверка: все имена параметров, упомянутые в kb_verified, существуют в Copter-4.6.3 (apm.pdef.json)
и не помечены как переименованные. Шаблоны вида RCx_/SERVOx_/…n_ проверяются подстановкой 1."""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from kb_verified import VERIFIED  # noqa


def load_pdef(path):
    d = json.load(open(path, encoding="utf-8"))
    out = {}
    for grp, v in d.items():
        if isinstance(v, dict):
            for k, x in v.items():
                if isinstance(x, dict):
                    out[k] = x
    return out


TOK = re.compile(r"\b[A-Z][A-Z0-9]*(?:_[A-Z0-9*]+)+\b")
NOT_PARAMS = {"MAV_SEVERITY", "GPS_OK_FIX_3D", "ARMING_CHECK_RC", "PREARM_MAX_ALT_DISPARITY_CM", "AP_COMPASS_OFFSETS_MAX_DEFAULT", "AP_ARMING_ACCEL_ERROR_THRESHOLD",
              "AP_ARMING_AHRS_GPS_ERROR_MAX", "AP_ARMING_BOARD_VOLTAGE_MAX", "AP_ARMING_COMPASS_MAGFIELD_MIN", "AP_ARMING_COMPASS_MAGFIELD_MAX", "RC_CALIB_MIN_LIMIT_PWM",
              "RC_CALIB_MAX_LIMIT_PWM", "SAFETY_DISARMED", "ARMING_SKIP_CHECK_RPY", "ARMING_CHECK_THROTTLE", "AID_NONE", "CRASH_CHECK_TRIGGER_SEC",
              "THRUST_LOSS_CHECK_TRIGGER_SEC", "YAW_IMBALANCE_IMAX_THRESHOLD", "EKF_CHECK_ITERATIONS_MAX", "FS_EKF_THRESHOLD_DEFAULT", "GPS_HDOP_GOOD_DEFAULT",
              "AP_COMPASS_MAX_XY_ANG_DIFF", "AUTOTUNE_LEVEL_TIMEOUT", "COMPASS_MIN", "MAX_SCALE_FACTOR", "PITCH_270", "PITCH_90", "DO_LAND_START", "ROTATION_PITCH_270",
              "CRASH_CHECK_", "THRUST_LOSS_CHECK_", "POSCONTROL_", "INS_TCALn_ENABLE"}


def candidates(tok):
    t = tok.rstrip("_*")
    t = re.sub(r"(?<=[A-Z])(x|n)(?=_)", "1", tok)   # RCx_ -> RC1_, PRIOn -> PRIO1
    t = t.replace("_*_", "_RLL_")
    out = [t]
    m = re.match(r"^(.*)_(X|Y|Z)$", t)
    if m:
        out.append(m.group(1) + "_X")
    return out


def main(pdef_path):
    P = load_pdef(pdef_path)
    bad, renamed, seen = [], [], set()
    for key, e in VERIFIED.items():
        blob = " ".join([e["t"], e["c"], " ".join(e["f"]), " ".join(e["more"]), " ".join(e["diag"]), e["ignore"], " ".join(e["p"])])
        for tok in set(TOK.findall(blob)) | set(e["p"]):
            if tok in seen or any(tok.startswith(n) for n in NOT_PARAMS) or "." in tok:
                continue
            seen.add(tok)
            if tok.isupper() and len(tok) < 4:
                continue
            ok = None
            for c in candidates(tok):
                if c in P:
                    ok = c
                    break
            if ok is None:
                bad.append(tok)
            else:
                desc = (P[ok].get("Description", "") + P[ok].get("DisplayName", ""))
                if re.search(r"[Rr]enamed in|[Dd]eprecated|no longer used", desc):
                    renamed.append((tok, desc[:120]))
    from kb_ops import OPS
    for key, e in OPS.items():
        blob = e["title"] + " " + e["what"] + " " + " ".join(c["c"] + " " + c["chk"] + " " + c["fix"] for c in e["causes"])
        for tok in set(TOK.findall(blob)):
            if tok in seen or any(tok.startswith(n) for n in NOT_PARAMS):
                continue
            seen.add(tok)
            if not any(c in P for c in candidates(tok)):
                bad.append(tok)
    print("UNKNOWN:", sorted(bad))
    print("RENAMED/DEPRECATED:")
    for r in renamed:
        print("  ", r)
    return bad, renamed


if __name__ == "__main__":
    main(sys.argv[1])

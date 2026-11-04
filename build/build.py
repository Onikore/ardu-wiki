# -*- coding: utf-8 -*-
"""build.py <src_dir> <site_dir>
1) extract.py -> raw.json (+.params)
2) привязка правил из kb.py
3) пишет site/data.js
"""
import json, os, re, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import kb  # noqa  (только DOCS и таблицы кодов лога / internal errors — они взяты из enum'ов исходников)
from kb_verified import VERIFIED  # noqa
from kb_ops import OPS  # noqa
import validate  # noqa
CHK_BIT = {'BARO':(1,'Барометр'),'COMPASS':(2,'Компас'),'GPS':(3,'GPS-фикс'),'INS':(4,'IMU'),'PARAMETERS':(5,'Параметры'),'RC':(6,'Каналы RC'),'VOLTAGE':(7,'Напряжение платы'),'BATTERY':(8,'Уровень батареи'),'AIRSPEED':(9,'Airspeed'),'LOGGING':(10,'Логирование'),'SWITCH':(11,'Safety switch'),'GPS_CONFIG':(12,'Конфигурация GPS'),'SYSTEM':(13,'Система'),'MISSION':(14,'Миссия'),'RANGEFINDER':(15,'Дальномер'),'CAMERA':(16,'Камера'),'AUX_AUTH':(17,'Aux-авторизация'),'VISION':(18,'Visual Odometry'),'FFT':(19,'FFT'),'OSD':(20,'OSD')}


SRC = sys.argv[1]
SITE = sys.argv[2]
TAG = "Copter-4.6.3"

tmp = os.path.join(tempfile.gettempdir(), "ardu_wiki_raw.json")
subprocess.check_call([sys.executable, "-I", os.path.join(HERE, "extract.py"), SRC, tmp])
raw = json.load(open(tmp, encoding="utf-8"))
PDEF_PATH = os.path.join(SRC, "apm.pdef.json")  # Tools/autotest/param_metadata/param_parse.py --vehicle ArduCopter --format json
PDEF = validate.load_pdef(PDEF_PATH)
bad, renamed = validate.main(PDEF_PATH)
renamed = [r for r in renamed if not r[0].startswith(("GPS1_", "GPS2_"))]
if bad and set(bad) - {"AP_AHRS", "AP_GPS", "ATC_RAT_RLL", "EK3_SRC", "FLTMODE_GCSBLOCK", "GPS_GLITCH", "FENCE_POINT", "FWD_THR", "INS_MAX_INSTANCES", "H_RUNUP_TIME", "PAYLOAD_PLACE"}:
    sys.exit("kb_verified ссылается на несуществующие параметры: %s" % bad)
if renamed:
    sys.exit("kb_verified использует переименованные параметры: %s" % renamed)

LIB_RU = {
    "ArduCopter": "Copter (ядро)", "AP_Arming": "Пре-арм проверки", "AP_Compass": "Компас", "CompassCalibrator": "Компас",
    "AP_GPS": "GPS", "AP_NavEKF3": "EKF", "AP_NavEKF2": "EKF", "AP_NavEKF": "EKF", "AP_AHRS": "AHRS/EKF",
    "AP_BattMonitor": "Батарея", "AP_InertialSensor": "IMU", "AP_Baro": "Барометр", "AC_Fence": "Geofence",
    "AP_RangeFinder": "Дальномер", "AP_OpticalFlow": "Optical Flow", "AP_Logger": "Логи/SD", "AP_Motors": "Моторы",
    "AC_AttitudeControl": "Управление/PID", "AC_AutoTune": "AutoTune", "AP_Proximity": "Proximity", "AC_PrecLand": "Precision Landing",
    "AP_Terrain": "Terrain", "AP_SmartRTL": "SmartRTL", "AC_Avoidance": "Object Avoidance", "AP_Mission": "Миссия",
    "GCS_MAVLink": "MAVLink/GCS", "RC_Channel": "Пульт/RC", "AP_Vehicle": "Система", "AP_Scheduler": "Система",
    "AP_Mount": "Подвес", "AP_Camera": "Камера", "AP_ADSB": "ADS-B", "AP_Parachute": "Парашют", "AP_VisualOdom": "Visual Odometry",
    "AP_DroneCAN": "DroneCAN", "AP_CANManager": "DroneCAN", "AP_KDECAN": "DroneCAN", "AP_Notify": "Индикация", "AP_OSD": "OSD",
    "AP_GyroFFT": "Гармонический фильтр", "AP_Airspeed": "Датчик скорости", "AP_Generator": "Генератор", "AP_Winch": "Лебёдка",
    "AP_Gripper": "Захват", "AP_ExternalAHRS": "Внешний AHRS", "AP_Networking": "Сеть", "AP_DDS": "DDS/ROS2", "AP_Quicktune": "Quicktune",
    "AP_AdvancedFailsafe": "Advanced Failsafe", "AP_FETtecOneWire": "ESC FETtec", "AP_BLHeli": "ESC BLHeli", "AP_Torqeedo": "Torqeedo",
    "AP_RCTelemetry": "Телеметрия", "AP_Frsky_Telem": "Телеметрия", "AP_Filesystem": "Файловая система", "StorageManager": "Хранилище",
    "AP_SerialManager": "Serial", "AP_BoardConfig": "Плата", "AP_Landing": "Посадка (Plane)", "AP_ICEngine": "ДВС", "AP_Soaring": "Планер",
    "AC_CustomControl": "Custom control", "AC_Autorotation": "Вертолёт", "AP_MotorsHeli": "Вертолёт", "AC_InputManager": "Вертолёт",
    "AP_Follow": "Follow", "AP_LandingGear": "Шасси", "AP_OpenDroneID": "OpenDroneID", "AP_WindVane": "Ветер", "AC_PosControl": "Управление/PID",
    "AP_CheckFirmware": "Прошивка", "AP_HAL": "HAL", "AP_Relay": "Реле", "APM_Control": "Plane control", "AR_Motors": "Rover",
    "AP_RPM": "RPM", "AP_Tuning": "Тюнинг", "AP_Button": "Кнопки", "AP_EFI": "EFI", "AP_WheelEncoder": "Энкодер", "AP_TemperatureSensor": "Температура",
}
# приоритет релевантности для Copter (чем ниже тем важнее)
LOW = {"AP_Networking", "AP_DDS", "AP_Torqeedo", "AP_Landing", "AP_ICEngine", "AP_Soaring", "AR_Motors", "APM_Control", "AP_WindVane",
       "AP_Winch", "AP_ExternalAHRS", "AP_Quicktune", "AP_FETtecOneWire", "AP_KDECAN", "AP_Generator", "AP_EFI", "AP_WheelEncoder",
       "AP_Button", "AP_Frsky_Telem", "AP_RCTelemetry", "AP_Mount", "AP_OpenDroneID", "AP_ADSB", "AP_GyroFFT", "AP_Camera",
       "AP_Gripper", "AP_ONVIF", "AP_Airspeed", "AP_AdvancedFailsafe"}


def sub_of(e):
    f = e["file"]
    if f.startswith("ArduCopter/"):
        b = os.path.basename(f)
        if b.startswith("mode_"):
            return "Режимы полёта"
        if b in ("AP_Arming.cpp",):
            return "Пре-арм проверки"
        if b in ("events.cpp", "failsafe.cpp", "crash_check.cpp", "ekf_check.cpp"):
            return "Failsafe/Crash"
        if b.startswith("motor") or b in ("esc_calibration.cpp", "takeoff_check.cpp"):
            return "Моторы"
        return LIB_RU["ArduCopter"]
    if f.startswith("libraries/"):
        lib = f.split("/")[1]
        for k, v in LIB_RU.items():
            if lib == k or lib.startswith(k):
                return v
        return lib
    return "Прочее"


# Префикс, с которым AP_Arming показывает текст из failure_msg библиотеки (проверено по AP_Arming.cpp / ArduCopter/AP_Arming.cpp)
FAIL_PREFIX = {
    "AP_Baro": "PreArm: Baro: ", "AP_InertialSensor": "PreArm: ", "AP_Compass": "PreArm: ", "AP_GPS": "PreArm: ",
    "AP_BattMonitor": "PreArm: ", "AP_RangeFinder": "PreArm: ", "AP_Motors": "PreArm: Motors: ",
    "AC_AttitudeControl": "PreArm: Bad parameter: ", "AP_AHRS": "PreArm: AHRS: ", "AP_NavEKF3": "PreArm: AHRS: ",
    "AP_NavEKF2": "PreArm: AHRS: ", "AP_NavEKF": "PreArm: AHRS: ", "AP_VisualOdom": "PreArm: VisOdom: ",
    "AP_DroneCAN": "PreArm: DroneCAN: ", "AP_Mount": "PreArm: Mount: ", "AP_Generator": "PreArm: Generator: ",
    "AP_OpenDroneID": "PreArm: OpenDroneID: ", "AP_FETtecOneWire": "PreArm: FETtec: ",
}
SKIP_TEXT = {"%s Failsafe", "%s Failsafe - %s"}


def fix_fail_text(e):
    if e["kind"] != "fail" or not e["file"].startswith("libraries/"):
        return e["text"], ""
    lib = e["file"].split("/")[1]
    fn = (e.get("func") or "").lower()
    buf = e.get("buf", "failure_msg")
    is_prearm = buf in ("failure_msg", "fail_msg", "prearm_fail_string", "temp_buffer") or "arm" in fn or "check" in fn
    if not is_prearm:
        return e["text"], ""
    pre = FAIL_PREFIX.get(lib)
    if pre is None:
        return e["text"], ""
    t = e["text"]
    if lib == "AC_AttitudeControl":
        t = re.sub(r"^%s_", "PSC_" if "PosControl" in e["file"] else "ATC_", t)
    if lib == "AP_BattMonitor" and not t.startswith("Battery"):
        t = "Battery %d " + t
    if lib == "AP_Motors":
        t = t.replace("%sSPIN", "MOT_SPIN").replace("%sPWM", "MOT_PWM")
    if t.startswith(pre.strip()):
        return t, pre
    return pre + t, pre




def fmt_map(m, prefix=""):
    if not isinstance(m, dict):
        return m or ""
    def key(k):
        try:
            return float(k)
        except ValueError:
            return 1e9
    return ", ".join(prefix + k + ": " + str(v) for k, v in sorted(m.items(), key=lambda kv: key(kv[0])))


def pinfo(name):
    d = dict(name=name)
    x = PDEF.get(name)
    if x is None:
        m = re.match(r"^(.*)_(X|Y|Z)$", name)
        if m and (m.group(1) + "_X") in PDEF:
            x = PDEF[m.group(1) + "_X"]
    if x:
        rng = x.get("Range")
        if isinstance(rng, dict):
            rng = "%s … %s" % (rng.get("low"), rng.get("high"))
        d.update(display=x.get("DisplayName", ""), desc=x.get("Description", ""), range=rng or "",
                 values=fmt_map(x.get("Values")) or fmt_map(x.get("Bitmask"), "бит "), units=x.get("Units", ""))
    return d


NO_SIMPLE = set()
PTOK = re.compile(r"\b[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+\b")

out = []
for e in raw:
    if e["text"] in SKIP_TEXT:
        continue
    e["text"], _pre = fix_fail_text(e)
    lib = e["file"].split("/")[1] if e["file"].startswith("libraries/") else "ArduCopter"
    row = dict(
        id=e["id"], text=e["text"], sev=e["sev"] or "INFO", sub=sub_of(e), file=e["file"], line=e["line"],
        func=e["func"], ctx=e["ctx"], kind=e["kind"], cond=e.get("cond", ""),
        via=("Текст формируется в библиотеке и выводится проверкой AP_Arming с префиксом «" + _pre.strip() + "»." if _pre else ""),
        rank=(2 if lib in LOW else (0 if lib in ("ArduCopter", "AP_Arming") else 1)),
        gh=f"https://github.com/ArduPilot/ardupilot/blob/{TAG}/{e['file']}#L{e['line']}",
    )
    v = VERIFIED.get(e["text"])
    pnames = []
    if v:
        row.update(t=v["t"], c=v["c"], f=v["f"], causes=v["causes"], diag=v["diag"], more=v["more"], ignore=v["ignore"],
                   d=[kb.DOCS[k] for k in v["d"] if k in kb.DOCS], cur=1, src=v["code"])
        op = OPS.get(v["t"])
        if op:
            row.update(ops=op)
        else:
            NO_SIMPLE.add(v["t"])
        pnames = list(dict.fromkeys(v["p"]))
    else:
        row.update(t="", c="", f=[], d=[], cur=0)
    # параметры, названные прямо в тексте сообщения
    for t in PTOK.findall(e["text"]):
        if t in PDEF and t not in pnames:
            pnames.append(t)
    row["p"] = [pinfo(n) for n in pnames[:10]]
    ck = e.get("chk", "")
    if ck:
        bit, ru = CHK_BIT.get(ck, (0, ck))
        row["chk"] = dict(name="ARMING_CHECK_" + ck, ru=ru, bit=bit)
    out.append(row)

if NO_SIMPLE:
    print("WARNING: нет простого текста для:", sorted(NO_SIMPLE))
extra = sorted(set(OPS) - {e["t"] for e in VERIFIED.values()})
if extra:
    print("WARNING: простые тексты без разбора:", extra)
# одинаковые тексты (EKF2/EKF3 и т.п.) — одна карточка; предпочитаем EKF3/ArduCopter
out.sort(key=lambda r: ("NavEKF2" in r["file"], r["rank"]))
_seen = set()
out = [r for r in out if not (r["text"] in _seen or _seen.add(r["text"]))]
missing = sorted(set(VERIFIED) - {r["text"] for r in out})
if missing:
    print("WARNING: проверенные ключи без сообщения в коде:", missing)
out.sort(key=lambda r: (-r["cur"], r["rank"], r["sub"], r["text"]))

errs = [dict(sub=k, name=kb.ERR_SUBSYS[k], ru=kb.ERR_SUBSYS_RU[k]) for k in sorted(kb.ERR_SUBSYS)]
data = dict(tag=TAG, msgs=out, errSub=errs, errCodes=[dict(code=a, name=b, ru=c) for a, b, c in kb.ERR_CODES],
            internal=[dict(bit=a, name=b, ru=c) for a, b, c in kb.INTERNAL_ERRORS])
os.makedirs(SITE, exist_ok=True)
with open(os.path.join(SITE, "data.js"), "w", encoding="utf-8") as f:
    f.write("window.WIKI=" + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";")
n_cur = sum(r["cur"] for r in out)
cop = [r for r in out if r["rank"] < 2 and r["sev"] in ("CRITICAL", "ERROR", "WARNING", "ALERT", "EMERGENCY")]
print(f"entries={len(out)} verified={n_cur}; copter warnings/errors verified {sum(r['cur'] for r in cop)}/{len(cop)}; size={os.path.getsize(os.path.join(SITE,'data.js'))//1024}KB")

# -*- coding: utf-8 -*-
"""build.py <src_dir> <site_dir>
1) extract.py -> raw.json (+.params)
2) привязка правил из kb.py
3) пишет site/data.js
"""
import json, os, re, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import kb  # noqa
from kb_deep import DEEP  # noqa
from kb_deep2 import DEEP2  # noqa
for _k, _v in DEEP2.items():
    DEEP.setdefault(_k, _v)
USED_DEEP = set()
CHK_BIT = {'BARO':(1,'Барометр'),'COMPASS':(2,'Компас'),'GPS':(3,'GPS-фикс'),'INS':(4,'IMU'),'PARAMETERS':(5,'Параметры'),'RC':(6,'Каналы RC'),'VOLTAGE':(7,'Напряжение платы'),'BATTERY':(8,'Уровень батареи'),'AIRSPEED':(9,'Airspeed'),'LOGGING':(10,'Логирование'),'SWITCH':(11,'Safety switch'),'GPS_CONFIG':(12,'Конфигурация GPS'),'SYSTEM':(13,'Система'),'MISSION':(14,'Миссия'),'RANGEFINDER':(15,'Дальномер'),'CAMERA':(16,'Камера'),'AUX_AUTH':(17,'Aux-авторизация'),'VISION':(18,'Visual Odometry'),'FFT':(19,'FFT'),'OSD':(20,'OSD')}


SRC = sys.argv[1]
SITE = sys.argv[2]
TAG = "Copter-4.6.3"

tmp = os.path.join(tempfile.gettempdir(), "ardu_wiki_raw.json")
subprocess.check_call([sys.executable, "-I", os.path.join(HERE, "extract.py"), SRC, tmp])
raw = json.load(open(tmp, encoding="utf-8"))
pdb = json.load(open(tmp + ".params", encoding="utf-8"))

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


PREFIX_LIB = {"COMPASS": "AP_Compass", "BATT": "AP_BattMonitor", "MOT": "AP_Motors", "GPS": "AP_GPS", "EK3": "AP_NavEKF3",
              "EK2": "AP_NavEKF2", "INS": "AP_InertialSensor", "ARMING": "AP_Arming", "FENCE": "AC_Fence", "RNGFND1": "AP_RangeFinder",
              "BARO": "AP_Baro", "ATC": "AC_AttitudeControl", "PSC": "AC_PosControl", "FLOW": "AP_OpticalFlow", "PRX1": "AP_Proximity",
              "TERRAIN": "AP_Terrain", "LOG": "AP_Logger", "SERVO1": "SRV_Channel", "BRD": "AP_BoardConfig", "SRTL": "AP_SmartRTL",
              "OA": "AC_Avoidance", "PLND": "AC_PrecLand", "SCHED": "AP_Scheduler", "CHUTE": "AP_Parachute", "ADSB": "AP_ADSB",
              "RC1": "RC_Channel", "RC7": "RC_Channel", "RC8": "RC_Channel", "SERIAL1": "AP_SerialManager", "AHRS": "AP_AHRS",
              "SERVO": "SRV_Channel", "EK3_SRC1": "AP_NavEKF", "RALLY": "AP_Rally", "H": "AP_Motors", "RC": "RC_Channel"}


def lookup_param(name):
    if name in pdb:
        it = pdb[name][0]
        return it
    mm = re.match(r"^(RC|SERVO)\d+_(\w+)$", name)
    if mm:
        lib = "RC_Channel" if mm.group(1) == "RC" else "SRV_Channel"
        for cand in (mm.group(2), "_" + mm.group(2)):
            for it in pdb.get(cand, []):
                if lib in it["file"]:
                    return it
    best = None
    for pfx, lib in PREFIX_LIB.items():
        if name.startswith(pfx + "_") or name == pfx:
            rest = name[len(pfx):]
            for cand in (rest, rest.lstrip("_")):
                if cand in pdb:
                    for it in pdb[cand]:
                        if lib in it["file"]:
                            return it
            for k in pdb:
                if rest and k == rest:
                    for it in pdb[k]:
                        if lib in it["file"]:
                            return it
    return best


def pinfo(name):
    it = lookup_param(name)
    d = dict(name=name)
    if it:
        d.update(display=it.get("DisplayName", ""), desc=it.get("Description", ""), range=it.get("Range", ""),
                 values=it.get("Values", ""), units=it.get("Units", ""), default=it.get("Default", ""))
    return d


compiled = [(re.compile(r["rx"], re.I), r) for r in kb.RULES]


def match_rule(text):
    """Выбирает самое специфичное правило: наибольшая длина совпавшего текста (широкие .* штрафуются)."""
    probe = re.sub(r"%[-+ #0-9.]*(?:l|h|ll|z)?s", "X", text)
    probe = re.sub(r"%[-+ #0-9.]*(?:l|h|ll|z)?[a-zA-Z]", "1", probe)
    best, bs = None, -1
    for order, (rx, r) in enumerate(compiled):
        for t in (text, probe):
            m = rx.search(t)
            if not m:
                continue
            span = m.end() - m.start()
            if ".*" in r["rx"]:
                span = span * 0.5
            if r.get("src"):
                span += 3  # правила по коду предпочтительнее при равенстве
            if span > bs:
                best, bs = r, span
    return best


GENERIC = ("Для этого сообщения готового разбора пока нет. Ниже показано условие в исходниках (где и когда оно выводится) "
           "и связанные параметры: сначала проверь, какое условие истинно, потом смотри лог (Mission Planner → Review a Log).")

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


out = []
seen_text = {}
for e in raw:
    if e["text"] in SKIP_TEXT:
        continue
    e["text"], _pre = fix_fail_text(e)
    r = match_rule(e["text"])
    base = os.path.basename(e["file"])
    lib = e["file"].split("/")[1] if e["file"].startswith("libraries/") else "ArduCopter"
    row = dict(
        id=e["id"], text=e["text"], sev=e["sev"] or "INFO", sub=sub_of(e), file=e["file"], line=e["line"],
        func=e["func"], ctx=e["ctx"], kind=e["kind"], cond=e.get("cond", ""),
        via=("Текст формируется в библиотеке и выводится проверкой AP_Arming с префиксом «" + _pre.strip() + "»." if _pre else ""),
        rank=(2 if lib in LOW else (0 if lib in ("ArduCopter", "AP_Arming") else 1)),
        gh=f"https://github.com/ArduPilot/ardupilot/blob/{TAG}/{e['file']}#L{e['line']}",
    )
    if r:
        row.update(t=r["t"], c=r["c"], f=r["f"], d=[kb.DOCS[k] for k in r["d"] if k in kb.DOCS], cur=1)
        pnames = list(dict.fromkeys(r["p"]))
        dp = r.get("deep") or DEEP.get(r["t"])
        if dp:
            USED_DEEP.add(r["t"])
            row.update(causes=dp.get("causes", []), diag=dp.get("diag", []), f=dp.get("steps") or r["f"], more=dp.get("more", []), ignore=dp.get("ignore", ""), deep=1)
        row["src"] = r.get("src", "")
    else:
        h = kb.SUB_HINTS.get(row["sub"])
        if h:
            row.update(t="", c=GENERIC + " Общий контекст: " + h[0], f=h[1], d=[kb.DOCS[k] for k in h[2] if k in kb.DOCS], cur=0)
        else:
            row.update(t="", c=GENERIC, f=[], d=[], cur=0)
        pnames = []
    # параметры из текста сообщения
    for p in e.get("params", []):
        if p["name"] not in pnames:
            pnames.append(p["name"])
    row["p"] = [pinfo(n) for n in pnames[:10]]
    ck = e.get("chk", "")
    if ck:
        bit, ru = CHK_BIT.get(ck, (0, ck))
        row["chk"] = dict(name="ARMING_CHECK_" + ck, ru=ru, bit=bit, val=(1 << bit) if bit else 1)
    out.append(row)

# Виртуальные записи
for i, (text, sev, sub, where) in enumerate([]):  # виртуальные записи убраны: всё берётся из кода
    r = match_rule(text)
    row = dict(id="x%03d" % i, text=text, sev=sev, sub=sub, file=where, line=0, func="", ctx="", kind="virtual", rank=0, gh="",
               t="", c=GENERIC, f=[], d=[], cur=0, p=[])
    if r:
        row.update(t=r["t"], c=r["c"], f=r["f"], d=[kb.DOCS[k] for k in r["d"] if k in kb.DOCS], cur=1,
                   p=[pinfo(n) for n in r["p"][:10]])
        dp = DEEP.get(r["t"])
        if dp:
            USED_DEEP.add(r["t"])
            row.update(causes=dp.get("causes", []), diag=dp.get("diag", []), f=dp.get("steps") or r["f"], more=dp.get("more", []), ignore=dp.get("ignore", ""), deep=1)
    row["note"] = "Сообщение собирается из нескольких частей/форматов, поэтому в исходниках целиком не встречается."
    out.append(row)

for k in DEEP:
    if k not in USED_DEEP:
        print("DEEP key unused:", k)
out.sort(key=lambda r: (-r["cur"], r["rank"], r["sub"], r["text"]))

errs = [dict(sub=k, name=kb.ERR_SUBSYS[k], ru=kb.ERR_SUBSYS_RU[k]) for k in sorted(kb.ERR_SUBSYS)]
data = dict(tag=TAG, msgs=out, errSub=errs, errCodes=[dict(code=a, name=b, ru=c) for a, b, c in kb.ERR_CODES],
            internal=[dict(bit=a, name=b, ru=c) for a, b, c in kb.INTERNAL_ERRORS])
os.makedirs(SITE, exist_ok=True)
with open(os.path.join(SITE, "data.js"), "w", encoding="utf-8") as f:
    f.write("window.WIKI=" + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";")
n_cur = sum(r["cur"] for r in out)
print(f"entries={len(out)} curated={n_cur} ({100*n_cur//len(out)}%) size={os.path.getsize(os.path.join(SITE,'data.js'))//1024}KB")

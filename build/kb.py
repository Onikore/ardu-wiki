# -*- coding: utf-8 -*-
"""Курируемая база знаний: правила (regex по тексту сообщения) -> причина и решение.
Сообщения берутся из исходников ArduCopter-4.6.3 экстрактором (extract.py), правила
привязываются по regex. Первое совпавшее правило побеждает.
"""

DOCS = {
    "prearm": ("Pre-arm safety checks", "https://ardupilot.org/copter/docs/prearm_safety_check.html"),
    "compcal": ("Калибровка компаса", "https://ardupilot.org/copter/docs/common-compass-calibration-in-mission-planner.html"),
    "acccal": ("Калибровка акселерометра", "https://ardupilot.org/copter/docs/common-accelerometer-calibration.html"),
    "fs": ("Failsafe: обзор", "https://ardupilot.org/copter/docs/failsafe-landing-page.html"),
    "fsradio": ("Radio failsafe", "https://ardupilot.org/copter/docs/radio-failsafe.html"),
    "fsbatt": ("Battery failsafe", "https://ardupilot.org/copter/docs/battery-failsafe.html"),
    "fsgcs": ("GCS failsafe", "https://ardupilot.org/copter/docs/gcs-failsafe.html"),
    "fsekf": ("EKF/DCM failsafe", "https://ardupilot.org/copter/docs/ekf-inav-failsafe.html"),
    "fscrash": ("Crash check", "https://ardupilot.org/copter/docs/crash_check.html"),
    "fence": ("Geofence", "https://ardupilot.org/copter/docs/ac2_simplegeofence.html"),
    "logs": ("Диагностика по логам", "https://ardupilot.org/copter/docs/common-diagnosing-problems-using-logs.html"),
    "vibe": ("Вибрации", "https://ardupilot.org/copter/docs/common-measuring-vibration.html"),
    "rc": ("Калибровка пульта", "https://ardupilot.org/copter/docs/common-radio-control-calibration.html"),
    "rngf": ("Дальномеры", "https://ardupilot.org/copter/docs/common-rangefinder-landingpage.html"),
    "ekf": ("EKF (навигация)", "https://ardupilot.org/copter/docs/common-apm-navigation-extended-kalman-filter-overview.html"),
    "gps": ("GPS", "https://ardupilot.org/copter/docs/common-positioning-landing-page.html"),
    "batt": ("Монитор батареи", "https://ardupilot.org/copter/docs/common-powermodule-landingpage.html"),
    "tune": ("Автотюн и настройка", "https://ardupilot.org/copter/docs/tuning.html"),
    "autotune": ("AutoTune", "https://ardupilot.org/copter/docs/autotune.html"),
    "terrain": ("Terrain following", "https://ardupilot.org/copter/docs/terrain-following.html"),
    "srtl": ("SmartRTL", "https://ardupilot.org/copter/docs/smartrtl-mode.html"),
    "motors": ("Моторы/ESC", "https://ardupilot.org/copter/docs/connect-escs-and-motors.html"),
    "frame": ("Тип рамы (FRAME_CLASS/TYPE)", "https://ardupilot.org/copter/docs/connect-escs-and-motors.html"),
    "flow": ("Optical Flow", "https://ardupilot.org/copter/docs/common-optical-flow-sensor-landingpage.html"),
    "dronecan": ("DroneCAN", "https://ardupilot.org/copter/docs/common-uavcan-setup-advanced.html"),
    "sd": ("Логи / SD-карта", "https://ardupilot.org/copter/docs/common-logs.html"),
    "params": ("Все параметры Copter", "https://ardupilot.org/copter/docs/parameters.html"),
    "safety": ("Safety switch", "https://ardupilot.org/copter/docs/common-safety-switch-pixhawk.html"),
    "oa": ("Object Avoidance", "https://ardupilot.org/copter/docs/common-object-avoidance-landing-page.html"),
    "prec": ("Precision Landing", "https://ardupilot.org/copter/docs/precision-landing-with-irlock.html"),
    "ekf3src": ("EKF Source Selection", "https://ardupilot.org/copter/docs/common-ekf-sources.html"),
    "mission": ("Миссии Auto", "https://ardupilot.org/copter/docs/auto-mode.html"),
    "modes": ("Режимы полёта", "https://ardupilot.org/copter/docs/flight-modes.html"),
    "mdisc": ("Мотор-тест", "https://ardupilot.org/copter/docs/code-overview-motors.html"),
    "compassmot": ("CompassMot", "https://ardupilot.org/copter/docs/common-compass-power-compensation.html"),
    "dfu": ("Прошивка / bootloader", "https://ardupilot.org/copter/docs/common-loading-firmware-onto-pixhawk.html"),
}

# Каждое правило: rx, t(заголовок), c(причина), f(шаги), p(параметры), d(docs)
RULES = []


def R(rx, t, c, f, p=(), d=()):
    RULES.append(dict(rx=rx, t=t, c=c, f=list(f), p=list(p), d=list(d)))


# ----------------------------------------------------------------- ARMING (общие)
R(r"PreArm: System not initiali[sz]ed", "Система ещё не инициализирована",
  "Автопилот не закончил загрузку (старт IMU/EKF/периферии) либо инициализация упала.",
  ["Подожди 20–30 секунд после подачи питания, не двигай коптер.",
   "Если не проходит — проверь, нет ли других красных сообщений выше (они указывают реальную причину).",
   "Перезагрузи автопилот; проверь питание (5V, просадки при подключении USB/БП)."], [], ["prearm"])
R(r"PreArm: Interlock/E-Stop Conflict", "Конфликт Motor Interlock и E-Stop",
  "На одном пульте настроены и Motor E-Stop (RCx_OPTION=31), и Motor Interlock (32) и они в противоречивом положении.",
  ["Оставь только одну из функций или установи тумблеры так, чтобы E-Stop был выключен, а Interlock включён/отключён согласованно.",
   "Проверь RCx_OPTION для всех каналов в Mission Planner → Радио/Aux Function."], ["RC7_OPTION", "RC8_OPTION"], ["prearm"])
R(r"PreArm: Motor Interlock Enabled", "Motor Interlock включён при арминге",
  "Тумблер Motor Interlock (RCx_OPTION=32) находится в положении «включено» при попытке arm. Для мультикоптера на Interlock мотор не должен быть разрешён до arm.",
  ["Переключи тумблер Interlock в выключенное положение, затем arm, затем включи.",
   "Если Interlock не нужен — установи RCx_OPTION в 0 для этого канала."], ["RC7_OPTION"], ["prearm"])
R(r"PreArm: Motor Emergency Stop|Motors Emergency Stopped", "Моторы остановлены E-Stop",
  "Включён Motor Emergency Stop (аукс-функция 31 / 165 или сигнал по MAVLink).",
  ["Выключи тумблер E-Stop на пульте.", "Проверь RCx_OPTION=31 и что тумблер не «залип» в калибровке (RCx_MIN/MAX)."], [], ["prearm"])
R(r"^PreArm: Motors: ", "Ошибка конфигурации моторов",
  "Проверка AP_Motors не прошла: часть после «Motors:» — точная причина (нет рамы, не назначены SERVOx_FUNCTION, SPIN_ARM > SPIN_MIN, неверные PWM_MIN/MAX и т.д.).",
  ["Если «Check frame class and type» — задай FRAME_CLASS и FRAME_TYPE, перезагрузи.",
   "«no SERVOx_FUNCTION set to MotorN» — назначь SERVOx_FUNCTION=33..40 (Motor1..8) на выходы, куда подключены ESC.",
   "«MOT_SPIN_ARM > MOT_SPIN_MIN» — уменьши MOT_SPIN_ARM (0.10) или увеличь MOT_SPIN_MIN (0.15).",
   "«MOT_SPIN_MIN too high» — должно быть ≤ 0.3.",
   "«Check MOT_PWM_MIN and MOT_PWM_MAX» — либо оба 0 (авто для DShot), либо MIN<MAX в диапазоне 1000–2000."],
  ["FRAME_CLASS", "FRAME_TYPE", "MOT_SPIN_ARM", "MOT_SPIN_MIN", "MOT_PWM_MIN", "MOT_PWM_MAX", "MOT_PWM_TYPE"], ["frame", "motors"])
R(r"PreArm: RC not found", "Нет сигнала от пульта",
  "Автопилот не получает кадры RC (приёмник не привязан, не тот протокол/порт, провод).",
  ["Включи пульт, проверь привязку (bind) и индикацию приёмника.",
   "SBUS/CRSF/IBUS: проверь, что порт назначен (SERIALn_PROTOCOL=23 RCIN) и RC_PROTOCOLS включает нужный протокол.",
   "Для CRSF/ELRS по UART: SERIALn_PROTOCOL=23, SERIALn_OPTIONS по необходимости, RC_OPTIONS.",
   "Mission Planner → Setup → Radio Calibration: двигай стики и убедись, что полоски двигаются.",
   "Для тестов без пульта: FS_THR_ENABLE=0 и ARMING_CHECK без RC (небезопасно!)."], ["RC_PROTOCOLS", "RC_OPTIONS", "FS_THR_ENABLE", "ARMING_CHECK"], ["rc", "prearm"])
R(r"PreArm: .* below failsafe", "Газ (RC3) ниже порога радио-failsafe",
  "Значение канала газа ниже FS_THR_VALUE — автопилот считает, что пульт потерян.",
  ["Подними стик газа; если ниже порога при минимуме — перекалибруй пульт (RC3_MIN).",
   "Проверь FS_THR_VALUE (по умолчанию 975) и что в пульте failsafe сконфигурирован на значение ниже этого порога.",
   "Проверь реверс канала газа и триммеры."], ["FS_THR_VALUE", "FS_THR_ENABLE", "RC3_MIN"], ["fsradio", "rc"])
R(r"PreArm: Altitude disparity", "Рассогласование высоты баро ↔ инерциалка",
  "Высота по барометру и по инерциальной навигации расходятся более чем на 1 м.",
  ["Не трогай коптер ~30 с, дай EKF сойтись; перезагрузи, если не проходит.",
   "Закрой барометр кусочком поролона (свет, ветер от пропов и сквозняк влияют на показания).",
   "Проверь вибрации (логи VIBE) и чтобы баро не был рядом с обдувом моторов.",
   "Откалибруй акселерометр."], ["EK3_ALT_SOURCE", "GND_ABS_PRESS"], ["prearm", "vibe"])
R(r"PreArm: EKF attitude is bad", "Ориентация EKF плохая",
  "EKF не уверен в крене/тангаже: идёт выравнивание, плохая калибровка акселя/компаса или большие вибрации.",
  ["Положи коптер на ровную поверхность, не двигай и подожди.", "Сделай калибровку акселя (level) и компаса.", "Проверь вибрации."], [], ["ekf", "acccal"])
R(r"PreArm: Battery failsafe", "Активен battery failsafe",
  "Напряжение/ёмкость ниже BATT_LOW_* / BATT_CRT_* — arm запрещён.",
  ["Зарядить/заменить батарею.", "Проверь калибровку датчика напряжения (BATT_VOLT_MULT) — реальное напряжение мультиметром.",
   "Проверь BATT_LOW_VOLT, BATT_CRT_VOLT, BATT_LOW_MAH и количество ячеек."], ["BATT_LOW_VOLT", "BATT_CRT_VOLT", "BATT_VOLT_MULT", "BATT_MONITOR", "BATT_ARM_VOLT"], ["fsbatt", "batt"])
R(r"PreArm: Check FS_THR_VALUE", "Некорректный FS_THR_VALUE",
  "FS_THR_VALUE меньше 910 или не ниже RC3_MIN.", ["Установи FS_THR_VALUE между 910 и RC3_MIN (обычно 975)."], ["FS_THR_VALUE", "RC3_MIN"], ["fsradio"])
R(r"PreArm: FS_GCS_ENABLE=2 removed", "FS_GCS_ENABLE=2 устарел",
  "Значение 2 удалено; теперь используется FS_OPTIONS.", ["Установи FS_GCS_ENABLE=1 (RTL) или 5 (SmartRTL/Land), а режим Auto-продолжения — через FS_OPTIONS."], ["FS_GCS_ENABLE", "FS_OPTIONS"], ["fsgcs"])
R(r"PreArm: Check ANGLE_MAX", "ANGLE_MAX вне диапазона", "ANGLE_MAX должен быть 1000–8000 (10°–80°).", ["Задай ANGLE_MAX = 3000 (по умолчанию)."], ["ANGLE_MAX"], ["params"])
R(r"PreArm: Check ACRO_BAL", "ACRO_BAL_ROLL/PITCH вне диапазона", "Значения должны быть меньше ATC_ANGLE_P (ACRO_BAL_* ≤ ATC_ANG_*_P).", ["Уменьши ACRO_BAL_ROLL/PITCH или верни ATC_ANG_RLL_P/PIT_P на стандартные."], ["ACRO_BAL_ROLL", "ACRO_BAL_PITCH"], [])
R(r"PreArm: Check PILOT_SPEED_UP", "PILOT_SPEED_UP ≤ 0", "Скорость набора высоты пилотом должна быть > 0.", ["Установи PILOT_SPEED_UP = 250 (см/с)."], ["PILOT_SPEED_UP"], [])
R(r"PreArm: Invalid MultiCopter FRAME_CLASS", "Неверный FRAME_CLASS для мультикоптера",
  "FRAME_CLASS не относится к мультикоптеру (например, 0 или значение для хели/Sub).",
  ["Mission Planner → Setup → Mandatory Hardware → Frame Type, либо задай FRAME_CLASS (1 Quad, 2 Hexa, 3 Octa …) и FRAME_TYPE (1 X), перезагрузи."], ["FRAME_CLASS", "FRAME_TYPE"], ["frame"])
R(r"PreArm: ADSB threat", "ADS-B угроза", "Рядом обнаружен воздушный борт по ADS-B.", ["Дождись пока угроза исчезнет или отключи ADSB (ADSB_TYPE=0), если не нужен."], ["ADSB_TYPE"], [])
R(r"PreArm: Bad parameter", "Неверное значение параметра",
  "Проверка параметров (PID, фильтры) нашла недопустимое значение. После двоеточия указано, какой именно.",
  ["Исправь указанный параметр (подробности в тексте, например ATC_RAT_RLL_P > 0).", "При сомнениях верни PID к стандартным значениям."], ["ATC_RAT_RLL_P", "ATC_RAT_PIT_P", "ATC_RAT_YAW_P"], [])
R(r"PreArm: High GPS HDOP", "Высокий HDOP GPS",
  "HDOP больше GPS_HDOP_GOOD (по умолчанию 140 = 1.4).",
  ["Выйди на открытое пространство, подожди набора спутников.", "Проверь расположение GPS (подальше от силовых проводов, видеопередатчика, USB3).",
   "Крайняя мера: увеличить GPS_HDOP_GOOD (хуже точность)."], ["GPS_HDOP_GOOD", "ARMING_CHECK"], ["gps"])
R(r"PreArm: Proximity .* \(want", "Препятствие слишком близко (Proximity)", "Датчик proximity видит объект ближе допустимого PRX_MIN/пре-арм порога.", ["Отодвинь коптер от объектов; проверь угол и PRX_ORIENT."], ["PRX1_TYPE"], ["oa"])
R(r"PreArm: AHRS: ", "AHRS/EKF не готов (подробности после «AHRS:»)",
  "Фильтр навигации не готов к полёту. После «AHRS:» указана причина: ожидание GPS-конфигурации, ошибки yaw, EKF3 vel error, неверные EK3_SRC и т.д.",
  ["Подожди 1–2 минуты на открытом месте.", "«EKF3 waiting for GPS config data» — GPS ещё конфигурируется (проверь GPS_TYPE, скорость, кабель).",
   "«Yaw inconsistent … Wait or reboot» — дождись/перезагрузись, проверь компас.", "«Check EK3_SRCn_*» — источники EKF настроены противоречиво (см. раздел «EKF source»).",
   "«EKF3[n] vel error» — на земле скорость GPS расходится с инерциалкой: не двигай коптер, проверь вибрации."], ["EK3_SRC1_POSXY", "EK3_SRC1_VELXY", "EK3_SRC1_YAW", "AHRS_EKF_TYPE"], ["ekf", "ekf3src"])
R(r"PreArm: Need Position Estimate|Fence enabled, need position|Need Alt Estimate", "Нет оценки позиции/высоты",
  "Выбранный режим (Loiter/Auto/RTL, включённый Fence) требует позицию, а EKF не имеет GPS-позиции/origin.",
  ["Выйди под открытое небо, дождись 3D fix и «EKF3 IMU0 origin set».", "В помещении используй Stabilize/AltHold или настрой optical flow/rangefinder/VIO (EK3_SRC*).",
   "Если нужна проверка отключения: ARMING_CHECK — только для теста."], ["ARMING_CHECK", "FENCE_ENABLE", "EK3_SRC1_POSXY"], ["gps", "ekf"])
R(r"PreArm: GPS glitching", "GPS глитчит", "Включён флаг GPS glitch: скачки позиции относительно инерциалки.", ["Проверь помехи (видеопередатчик, USB3, ESC), антенну, расположение GPS.", "Подожди; если не уходит — смотри лог GPS и XKF."], ["GPS_TYPE"], ["gps"])
R(r"PreArm: EKF (compass|position|velocity|height) variance", "Дисперсия EKF слишком большая",
  "Соответствующая дисперсия (compass/position/velocity/height) выше порога — фильтр не доверяет сенсору.",
  ["Compass variance: откалибруй компас, убери помехи (провода ESC под GPS-модулем), проверь COMPASS_ORIENT.",
   "Position/Velocity: плохой GPS (HDOP, спутники), вибрации, подожди.", "Height variance: вибрации/баро: закрой баро, проверь VIBE и CLIP.",
   "Открой лог → XKF4 / XKF3 и смотри SV/SP/SH/SM."], ["EK3_MAG_CAL", "EK3_POS_I_GATE", "EK3_VEL_I_GATE"], ["ekf", "vibe", "compcal"])
R(r"PreArm: GCS failsafe on", "Активен GCS failsafe", "GCS был подключён, а затем потерян (FS_GCS_ENABLE ≠ 0).", ["Подключи GCS/телеметрию или FS_GCS_ENABLE=0 если GCS не нужен."], ["FS_GCS_ENABLE", "SYSID_MYGCS"], ["fsgcs"])
R(r"PreArm: (AHRS|Compass) not healthy", "AHRS/компас нездоров", "Датчик/фильтр не отдаёт данные.", ["Проверь шлейф/пайку/I2C, перезагрузи, посмотри другие сообщения.", "Для компаса: COMPASS_USE/ENABLE, внешний компас по I2C/CAN подключён."], ["COMPASS_USE", "COMPASS_USE2", "COMPASS_USE3"], ["compcal"])
R(r"PreArm: .* mode not armable", "Режим нельзя armить", "Текущий режим в данной конфигурации недоступен для arm (нет GPS, миссии и пр.).", ["Переключись в Stabilize/AltHold и arm, либо выполни требования режима."], ["ARMING_CHECK"], ["modes"])
R(r"PreArm: Leaning", "Коптер наклонён", "Угол наклона слишком большой для arm.", ["Поставь коптер ровно, перекалибруй акселерометр (level).", "AHRS_TRIM_X/Y при необходимости."], ["AHRS_TRIM_X", "AHRS_TRIM_Y"], ["acccal"])
R(r"PreArm: (X|%s|\w+ \(RC\d+\)) too high", "Стик/канал слишком высоко", "Стик газа или другой канал находится выше разрешённого.", ["Опусти стик газа до нуля.", "Проверь калибровку пульта."], ["RC3_MIN"], ["rc"])
R(r"PreArm: (Hardware )?[Ss]afety [Ss]witch", "Не нажат safety switch", "Аппаратный выключатель безопасности не подтверждён (быстро мигающий красный светодиод).", ["Нажми и удерживай кнопку safety на GPS ~1–2 с.", "Нет кнопки: BRD_SAFETY_DEFLT=0 (BRD_SAFETYENABLE=0 в старых версиях)."], ["BRD_SAFETY_DEFLT", "BRD_SAFETYOPTION"], ["safety"])
R(r"PreArm: Disarm Switch on", "Включён тумблер Disarm", "Аукс-функция Arm/Disarm (153) в положении disarm.", ["Переключи тумблер."], [], [])
# --- Compass
R(r"PreArm: Compass calibration running", "Идёт калибровка компаса", "Калибровка не завершена.", ["Закончи или отмени калибровку."], [], ["compcal"])
R(r"PreArm: Compass calibrated requires reboot|Compass order change requires reboot|Compass cal requires reboot", "Компас откалиброван — нужна перезагрузка", "После калибровки/смены приоритета нужна перезагрузка.", ["Перезагрузи автопилот."], ["COMPASS_PRIO1_ID"], ["compcal"])
R(r"PreArm: Compass offsets too high", "Слишком большие оффсеты компаса",
  "Модуль смещений > COMPASS_OFFS_MAX (1800 по умолчанию) — рядом сильный магнитный источник.",
  ["Отодвинь компас от силовых проводов, моторов, батареи; ставь GPS-мачту.", "Перекалибруй компас вдали от металла.", "Внутренний компас на плате обычно неюзабелен на мелком коптере — используй внешний."],
  ["COMPASS_OFFS_MAX", "COMPASS_USE", "COMPASS_EXTERNAL"], ["compcal"])
R(r"PreArm: Check mag field", "Магнитное поле не соответствует модели Земли",
  "Модуль поля или разница по осям отличается от модели WMM по месту больше ARMING_MAGTHRESH (по умолчанию 100 mGauss).",
  ["Откалибруй компас на улице, вдали от металла/авто.", "Проверь COMPASS_ORIENT внешнего компаса и COMPASS_EXTERNAL.",
   "Проверь, что координаты определены (GPS), иначе модель WMM неверна.", "Снизь влияние токов: перемести компас, свей питающие провода.", "Не рекомендуется: увеличить ARMING_MAGTHRESH или поставить 0."],
  ["ARMING_MAGTHRESH", "COMPASS_ORIENT", "COMPASS_EXTERNAL", "COMPASS_AUTODEC"], ["compcal"])
R(r"PreArm: Compasses inconsistent", "Компасы противоречат друг другу",
  "Направления на двух компасах расходятся больше ARMING порога (по умолчанию 45°).",
  ["Откалибруй все компасы.", "Проверь COMPASS_ORIENT / COMPASS_EXTERNAL у каждого — частая причина неверная ориентация внешнего компаса.",
   "Если внутренний компас плохой — COMPASS_USE2=0 (или USE3), либо отключи внутренний."],
  ["COMPASS_ORIENT", "COMPASS_ORIENT2", "COMPASS_USE", "COMPASS_USE2", "COMPASS_USE3", "COMPASS_EXTERNAL"], ["compcal"])
R(r"Compass not calibrated|Compass \d+ not found|Compass .* not found", "Компас не откалиброван / не найден",
  "Нулевые оффсеты (не калибровался) или заявленный компас не найден на шине.",
  ["Выполни калибровку (Onboard, Mission Planner → Mandatory Hardware → Compass).", "Проверь подключение внешнего компаса, I2C/CAN, питание, COMPASS_DEV_ID.", "Если компас физически удалён — сбрось связку: COMPASS_DEV_ID=0 или COMPASS_PRIOn_ID=0."],
  ["COMPASS_DEV_ID", "COMPASS_PRIO1_ID", "COMPASS_USE"], ["compcal"])
R(r"Mag\(\d+\) bad (internal )?orientation|bad orientation", "Калибровка компаса: неверная ориентация",
  "Подгонка эллипсоида показала, что COMPASS_ORIENT не соответствует реальной установке.",
  ["Задай верный COMPASS_ORIENT (угол установки внешнего компаса, стрелка на GPS = нос).", "Либо включи COMPASS_AUTO_ROT и повтори калибровку."], ["COMPASS_ORIENT", "COMPASS_AUTO_ROT"], ["compcal"])
R(r"Mag\(\d+\) bad radius", "Калибровка компаса: неверный радиус", "Радиус поля слишком отличается от ожидаемого — помехи или не крутил по всем осям.", ["Повтори калибровку вдали от металла, поворачивая коптер по всем осям.", "Убери магнитные помехи."], ["COMPASS_CAL_FIT"], ["compcal"])
R(r"Mag\[\d+\]: (unhealthy|bad uncorrected)|Compass cal requires GPS|Mag: no position|WMM", "Ошибки калибровки компаса",
  "Для автокалибровки нужен GPS-фикс (WMM-модель), компас должен быть здоров.", ["Дождись GPS-фикса и повтори.", "Проверь соединение компаса."], [], ["compcal"])
R(r"Mag: Compass #\d+ with DEVID .* (replaced|removed)", "Компас заменён / удалён", "Изменился набор компасов (другое устройство на шине).", ["Откалибруй новый компас; проверь COMPASS_PRIOn_ID."], ["COMPASS_PRIO1_ID"], ["compcal"])
# --- GPS
R(r"PreArm: GPS \d+: Bad fix", "GPS: плохой фикс", "Нет 3D fix или мало спутников.", ["Выйди на открытое место, жди 1–3 мин.", "Проверь антенну/кабель, GPS_TYPE, SERIALn_PROTOCOL=5 и скорость порта."], ["GPS_TYPE", "GPS_MIN_ELEV"], ["gps"])
R(r"PreArm: GPS \d+: not healthy|GPS blending unhealthy", "GPS не отвечает", "Нет данных от GPS (обрыв, не тот порт/скорость/тип).", ["Проверь провода TX/RX, питание 5V, SERIALn_PROTOCOL=5, SERIALn_BAUD, GPS_TYPE.", "Проверь конфликт CAN GPS (GPS_TYPE=9) и узла."], ["GPS_TYPE", "GPS_AUTO_CONFIG"], ["gps"])
R(r"PreArm: GPS \d+: primary but TYPE 0", "Основной GPS отключён", "Выбран GPS_PRIMARY, у которого GPS_TYPE=0.", ["Укажи верный GPS_TYPE (или смени GPS_PRIMARY)."], ["GPS_PRIMARY", "GPS_TYPE", "GPS_TYPE2"], ["gps"])
R(r"PreArm: AHRS: waiting for home", "Ждём установки Home", "Home ещё не задан (нет GPS fix/origin).", ["Дождись GPS fix, или для indoor задай EK3_ORIGIN/установи Home вручную."], [], ["gps"])
R(r"PreArm: GPS positions differ|GPS and AHRS differ", "Расхождение позиций GPS", "Два GPS или GPS и AHRS расходятся по позиции больше порога.", ["Дождись стабилизации, проверь, что оба GPS на открытом месте.", "При проблемном втором GPS — GPS_TYPE2=0."], ["GPS_TYPE2", "GPS_AUTO_SWITCH"], ["gps"])
R(r"PreArm: GPS .* still configuring", "GPS ещё конфигурируется", "u-blox идёт настройка.", ["Подожди; если не заканчивается — GPS_AUTO_CONFIG, скорость порта, кабель."], ["GPS_AUTO_CONFIG"], ["gps"])
R(r"GPS_AUTO_SWITCH==2 but no blending", "Blending без второго GPS", "GPS_AUTO_SWITCH=2 требует двух GPS.", ["Подключи второй GPS (GPS_TYPE2) либо GPS_AUTO_SWITCH=1."], ["GPS_AUTO_SWITCH"], ["gps"])
R(r"GPS\[\d+\] yaw not available|Selected GPS Node|Same Node Id|Incorrect Role set", "Проблема GPS-yaw / DroneCAN GPS", "Настройка двух GPS-антенн или CAN-узла неверна.", ["Проверь GPS_MB1_TYPE, смещения антенн, CAN node ID, GPS_CAN_*."], ["GPS_TYPE", "GPS_MB1_TYPE"], ["gps", "dronecan"])
# --- IMU
R(r"PreArm: (Gyros|Accels) not healthy", "IMU не отвечает", "Гироскоп/акселерометр не отдаёт данные (SPI, питание, неисправность).", ["Перезагрузи; подожди инициализации.", "При повторении — проверь питание/виброразвязку; возможна неисправность IMU."], ["INS_USE", "INS_USE2", "INS_USE3"], [])
R(r"PreArm: Gyros not calibrated|3D Accel calibration needed", "Нет калибровки IMU", "Не выполнялась калибровка (gyro при старте, accel 6-сторонняя).", ["Не двигай при подаче питания; выполни 6-сторонюю калибровку акселя."], ["INS_ACC_ID", "INS_ACCOFFS_X"], ["acccal"])
R(r"PreArm: Accels calibrated requires reboot", "После калибровки акселя нужна перезагрузка", "Калибровка применена, но требует reboot.", ["Перезагрузи автопилот."], [], ["acccal"])
R(r"PreArm: (Accels|Gyros) inconsistent", "IMU расходятся между собой",
  "Показания двух IMU различаются больше порога (акселерометры > 0.75 м/с², гироскопы > 5°/с).",
  ["Не двигай коптер, перезагрузи.", "Откалибруй акселерометр.", "Проверь вибрации/виброразвязку и крепление платы.", "Если один IMU бракованный: INS_USE2=0 / INS_USE3=0.", "Это меняется с температурой — прогрей борт."],
  ["INS_USE", "INS_USE2", "INS_USE3", "INS_ACCEL_FILTER"], ["vibe", "acccal"])
R(r"PreArm: temperature cal running|Batch sampling requires reboot", "Температурная калибровка / batch sampling", "Идёт TCAL либо включён BATCH_ENABLE — нужен reboot.", ["Заверши калибровку или перезагрузись (INS_LOG_BAT_OPT)."], ["INS_TCAL1_ENABLE", "INS_LOG_BAT_MASK"], [])
R(r"Gyro \d+ rate \d+Hz < loop rate", "Скорость гироскопа ниже цикла", "INS_GYRO_RATE ниже частоты основного цикла.", ["Увеличь INS_GYRO_RATE или снизь SCHED_LOOP_RATE."], ["INS_GYRO_RATE", "SCHED_LOOP_RATE"], [])
R(r"Failed to register (gyro|accel)", "Не удалось зарегистрировать IMU", "Слишком много IMU/конфликт ID.", ["Сбрось INS_*_ID (удали stale-устройства), перезагрузись."], ["INS_ACC_ID", "INS_GYR_ID"], [])
# --- Baro
R(r"PreArm: Baro: |^not healthy|Baro .* not healthy", "Барометр не здоров", "Нет данных баро либо значения вне диапазона.", ["Проверь питание/пайку, перезагрузи; закрой баро поролоном.", "Если баро неисправен: BARO_PRIMARY, ARMING_CHECK (не рекомендуется)."], ["BARO_PRIMARY", "BARO_ALT_OFFSET"], [])
R(r"GPS alt error .* BARO_ALTERR_MAX", "Высота GPS и баро расходятся", "Высота по GPS отличается от барометра больше BARO_ALTERR_MAX (метры) — калибровка баро или GPS-высота неверны.", ["Перезагрузи при стабильном GPS.", "Увеличь BARO_ALTERR_MAX только если обоснованно."], ["BARO_ALTERR_MAX"], [])
# --- RC
R(r"PreArm: .* \(RC\d+\) is not neutral", "Стик не в нейтрали", "Крен/тангаж/рыскание при arm не в центре.", ["Отпусти стики, откалибруй пульт, проверь триммеры.", "Поставь RCx_DZ мёртвую зону."], ["RC1_TRIM", "RC2_TRIM", "RC4_TRIM", "RC1_DZ"], ["rc"])
R(r"PreArm: RC\d+_MIN is greater than RC\d+_TRIM|RC\d+_MAX is less than RC\d+_TRIM|radio (min too high|max too low)", "Неверная калибровка RC", "RCx_MIN > TRIM, MAX < TRIM или MIN слишком высоко.", ["Перекалибруй пульт в Mission Planner (Setup → Radio Calibration).", "Проверь, что на пульте выставлены каналы 1000–2000."], ["RC1_MIN", "RC1_MAX", "RC1_TRIM"], ["rc"])
R(r"PreArm: RC calibrating|Radio failsafe on", "Идёт калибровка RC / активен радио-failsafe", "Пульт потерян или калибровка не завершена.", ["Включи пульт, закончи калибровку; проверь FS_THR_*."], ["FS_THR_ENABLE", "FS_THR_VALUE"], ["fsradio"])
R(r"PreArm: Duplicate Aux Switch Options", "Дубли Aux-функций", "Одна и та же функция назначена на несколько каналов.", ["Оставь по одному каналу на функцию (RCx_OPTION)."], [], [])
R(r"PreArm: Mode channel and RC\d+_OPTION conflict", "Канал режимов совпадает с аукс-каналом", "FLTMODE_CH и RCx_OPTION используют один канал.", ["Назначь разные каналы."], ["FLTMODE_CH"], [])
R(r"Multiple SERIAL ports configured for RC input|duplicate RCIN", "Несколько портов RC", "Два SERIALn_PROTOCOL=23.", ["Оставь только один порт RCIN."], [], [])
# --- SERVO
R(r"PreArm: SERVO\d+_(MIN|MAX) is|SERVO\d+_FUNCTION=\d+ on disabled channel", "Неверные SERVOx_MIN/MAX/FUNCTION", "Параметры выхода противоречат друг другу или канал отключён.", ["Исправь SERVOx_MIN < SERVOx_TRIM < SERVOx_MAX; проверь SERVOx_FUNCTION и BRD_PWM_COUNT/BRD_IO_ENABLE."], ["SERVO1_MIN", "SERVO1_MAX", "SERVO1_TRIM"], [])
# --- System
R(r"PreArm: IOMCU is unhealthy", "IOMCU не отвечает", "Сопроцессор IO на Pixhawk недоступен.", ["Перезагрузи/перепрошей; при повторении — аппаратный дефект платы."], ["BRD_IO_ENABLE"], [])
R(r"PreArm: Board .* out of range|Servo voltage to low", "Напряжение платы/серво вне диапазона", "Vcc платы или шины серво за допустимыми пределами.", ["Проверь BEC/питание (5.0–5.5V)."], ["BRD_VBUS_MIN", "BRD_VSERVO_MIN"], [])
R(r"PreArm: heater temp low", "Нагреватель IMU", "Температура IMU ниже BRD_HEAT_TARG.", ["Подожди прогрева или снизь BRD_HEAT_TARG."], ["BRD_HEAT_TARG"], [])
R(r"PreArm: Param storage failed|parameter storage full", "Хранилище параметров", "Ошибка записи/переполнение FRAM/flash.", ["Сбрось параметры (Reset), не храни лишние Rally/Fence/Mission; проверь питание."], [], [])
R(r"PreArm: Main loop slow", "Медленный главный цикл", "Частота цикла ниже SCHED_LOOP_RATE — перегрузка CPU.", ["Уменьши нагрузку: частоты логов, SCHED_LOOP_RATE=200 (или 100), отключи лишние сервисы (OSD, scripting).", "Смотри лог PM/Perf."], ["SCHED_LOOP_RATE", "LOG_BITMASK"], ["logs"])
R(r"PreArm: Internal errors 0x|Internal Errors 0x", "Внутренние ошибки прошивки", "Выставлены флаги InternalError. Таблица битов — на вкладке «Коды лога»; битовая маска раскладывается ниже.", ["Расшифруй маску (вкладка Internal Errors), сохрани лог и сообщи на discuss.ardupilot.org.", "Частые: stack_overflow, spi_fail, i2c_isr, main_loop_stuck, params_restored."], [], ["logs"])
R(r"terrain (required but )?disabled|Terrain out of memory|Terrain: Allocation failed", "Terrain", "Режим/фенс требует данные terrain, а TERRAIN_ENABLE=0 или не хватает памяти.", ["TERRAIN_ENABLE=1, нужны данные с GCS/SD (/APM/TERRAIN)."], ["TERRAIN_ENABLE", "TERRAIN_SPACING"], ["terrain"])
R(r"waiting for terrain data|Terrain data missing", "Нет данных terrain", "Данные рельефа не загружены.", ["Подключи GCS на несколько минут для подкачки или положи файлы на SD."], ["TERRAIN_ENABLE"], ["terrain"])
R(r"PreArm: (Logging failed|No SD card|Logging not started|Downloading logs)", "Проблема с логированием / SD-картой", "Нет SD, карта неисправна, идёт скачивание лога.", ["Вставь/отформатируй SD (FAT32, ≤32 ГБ, быстрая A1/class10).", "Заверши загрузку логов по MAVLink.", "Проверь LOG_BACKEND_TYPE; временно отключи только для тестов — ARMING_CHECK логгера."], ["LOG_BACKEND_TYPE", "LOG_DISARMED", "ARMING_CHECK"], ["sd"])
R(r"Chip full, logging stopped|AP_Logger: (IO thread died|stuck thread)|Log recovery", "Проблема логгера", "Переполнение флеш-логов / зависание записи на SD.", ["Сотри логи, замени/отформатируй SD.", "Уменьши LOG_BITMASK/частоту."], ["LOG_BITMASK", "LOG_FILE_BUFSIZE"], ["sd"])
R(r"PreArm: CrashDump data detected|CrashDump data detected", "Обнаружен crashdump", "После сбоя прошивки на борту остался дамп.", ["Выгрузи дамп через MAVFTP и стирай: параметр FLASH_CRASH/сообщение в GCS.", "Обнови прошивку; сообщи разработчикам."], [], ["logs"])
R(r"Warning: Arming Checks Disabled", "ARMING_CHECK отключены", "ARMING_CHECK=0 — полёт без защитных проверок.", ["Верни ARMING_CHECK=1."], ["ARMING_CHECK"], ["prearm"])
R(r"PreArm: (Missing mission item|Mode requires mission|No mission library)", "Режим Auto без миссии", "Нет нужных пунктов миссии.", ["Загрузи миссию с TAKEOFF/WAYPOINT."], [], ["mission"])
R(r"PreArm: .*rally", "Rally points", "Требуется rally-точка, но она недоступна.", ["Добавь Rally Point или отключи RALLY_INCL_HOME / RTL."], ["RALLY_TOTAL"], [])
R(r"PreArm: (Mount|Generator|OpenDroneID|FETtec|PiccoloCAN|DroneCAN|VisOdom): ", "Периферия не прошла проверку", "Подсистема сообщает собственную ошибку после двоеточия.", ["Читай текст после двоеточия, проверь проводку/конфиг этого устройства."], [], [])
R(r"auxiliary authori", "Aux-authorisation", "Ждёт внешнее разрешение на arm (скрипт/GCS).", ["Дай разрешение скриптом/MAVLink либо отключи."], [], [])
# ------------------------------------------------------- АРМИНГ для РАЗРЕШЕНИЙ / батарея (фрагменты)
R(r"PreArm: Battery \d+ ", "Батарея не прошла пре-арм",
  "Батарея ниже порога арма, нездорова или перепутаны пороги failsafe.",
  ["«below minimum arming voltage» — зарядить; BATT_ARM_VOLT.", "«unhealthy» — монитор не отвечает: BATT_MONITOR, проводка power module.", "«low/critical voltage failsafe» — напряжение ниже BATT_LOW_VOLT/BATT_CRT_VOLT.", "«voltage failsafe critical >= low» — пороги перепутаны: CRT < LOW."],
  ["BATT_MONITOR", "BATT_ARM_VOLT", "BATT_LOW_VOLT", "BATT_CRT_VOLT", "BATT_ARM_MAH", "BATT_VOLT_MULT"], ["batt", "fsbatt"])
# ----------------------------------------------------------- Режимы/Полёт
R(r"Crash: Disarming", "Crash check — дизарм", "Обнаружен краш: большой угол ошибки и малое ускорение в течение 2 с.", ["Проверь, не было ли реального падения/опрокидывания.", "Если ложное — проверь вибрации, PID, FRAME_TYPE, направление моторов, CRASH_CHECK (FS_CRASH_CHECK=0)."], ["FS_CRASH_CHECK"], ["fscrash"])
R(r"Potential Thrust Loss", "Потеря тяги мотора", "Один из моторов выдаёт максимум, но коптер не держит.", ["Проверь моторы/ESC/пропы, батарею, AUW (взлётный вес).", "Ищи просадки напряжения; увеличь тягу/ёмкость."], ["MOT_THST_EXPO", "MOT_BAT_VOLT_MAX", "MOT_BAT_VOLT_MIN"], ["motors"])
R(r"Yaw Imbalance", "Дисбаланс по рысканию", "Перекос мощности между CW и CCW моторами.", ["Проверь пропы, направления вращения, наклон моторов, центр тяжести."], [], ["motors"])
R(r"Parachute: Too low|Chute", "Парашют", "Парашют не выпущен (высота низкая) или не настроен.", ["Проверь CHUTE_ENABLED, CHUTE_ALT_MIN, реле/серво."], ["CHUTE_ENABLED", "CHUTE_ALT_MIN"], [])
R(r"^EKF variance|EKF Failsafe: changed|EKF Failsafe", "EKF failsafe", "Дисперсия EKF превысила FS_EKF_THRESH на 1+ секунд — компас/GPS/высота ненадёжны.", ["Лог: XKF4/XKF3; ищи вибрации (VIBE), помехи компасу, потерю GPS.", "FS_EKF_ACTION: 1=Land, 2=AltHold, 3=Land даже в Stabilize.", "Исправь причину, FS_EKF_THRESH повышай осторожно."], ["FS_EKF_ACTION", "FS_EKF_THRESH"], ["fsekf", "ekf"])
R(r"Vibration compensation (ON|OFF)", "Компенсация вибраций", "Сильные вибрации — EKF включил режим компенсации (high vibe).", ["Исправь вибрации: балансировка пропов/моторов, мягкое крепление FC, фильтры INS_HNTCH_*.", "Смотри VIBE.VibeX/Y/Z (>30 плохо) и CLIP."], ["INS_HNTCH_ENABLE", "INS_GYRO_FILTER"], ["vibe"])
R(r"EKF primary changed", "Переключился основной EKF-lane", "EKF сменил ядро (IMU) — первый «потерял доверие».", ["Если часто — проблема IMU/вибрация/компас на конкретном ядре; смотри лог XKF*."], ["EK3_PRIMARY", "EK3_IMU_MASK"], ["ekf"])
R(r"EKF[23] lane switch", "Смена EKF lane", "Переключение на другое ядро EKF по ошибкам инноваций.", ["Если срабатывает часто — проверь вибрации, ориентацию компаса и GPS."], [], ["ekf"])
R(r"EKF[23] IMU\d+ (stopped|has stopped) aiding", "EKF перестал использовать GPS/сенсор", "Нет данных от помощника (GPS/optflow/VIO) в течение таймаута.", ["Проверь GPS, optflow, источники EK3_SRC*."], ["EK3_SRC1_POSXY"], ["ekf3src"])
R(r"EKF[23] IMU\d+ (emergency yaw reset|MAG\d+ ground mag anomaly|forced reset)", "EKF сбросил курс", "Курс по компасу рассогласовался (магнитная аномалия, плохой компас).", ["Откалибруй компас, проверь COMPASS_ORIENT, не взлетай с металла."], ["EK3_MAG_CAL"], ["compcal", "ekf"])
R(r"EKF[23] IMU\d+ (tilt alignment|yaw aligned|origin set|is using)", "Информационное сообщение EKF", "Норма: идёт выравнивание/начало использования источника.", ["Ничего не нужно."], [], ["ekf"])
R(r"EKF3 waiting for GPS config", "EKF ждёт конфиг GPS", "u-blox ещё не конфигурирован (GPS_AUTO_CONFIG).", ["Подожди; проверь кабель/скорость/тип GPS."], ["GPS_AUTO_CONFIG"], ["gps"])
R(r"EK3_MAG_CAL and EK3_SRC1_YAW inconsistent|Check EK3_SRC\d+_", "Противоречие источников EKF", "EK3_SRCn_* настроены несовместимо (например, YAW=GPS, а POS/VEL нет).", ["Mission Planner → EKF3 Source: используй один из шаблонов GPS / GPS+Optflow / ExternalNav.", "EK3_MAG_CAL должен соответствовать EK3_SRC1_YAW."], ["EK3_SRC1_POSXY", "EK3_SRC1_VELXY", "EK3_SRC1_POSZ", "EK3_SRC1_VELZ", "EK3_SRC1_YAW", "EK3_MAG_CAL"], ["ekf3src"])
R(r"EKF[23].*(not enough memory|allocation failed|not started)|NavEKF[23]: (not enough memory|memory allocation)|no EKF[23] cores", "EKF не стартовал (память)", "Не хватает RAM либо EKF отключён/ошибка конфигурации.", ["Уменьши нагрузку: отключи EKF2 (EK2_ENABLE=0), лишние IMU (EK3_IMU_MASK), logs/scripting.", "AHRS_EKF_TYPE=3 и EK3_ENABLE=1."], ["AHRS_EKF_TYPE", "EK2_ENABLE", "EK3_ENABLE"], ["ekf"])
R(r"EKF[23] core \d+ (setup failed|unhealthy)", "EKF core нездоров", "Одно из ядер EKF отвалилось.", ["Проверь IMU, питание, вибрации; перезагрузи."], [], ["ekf"])
R(r"EKF[23] refusing set origin|origin already set", "EKF: origin уже задан", "Попытка повторно задать начало координат.", ["Игнорируй; сброс — только перезагрузка."], [], [])
R(r"Radio Failsafe Cleared|GCS Failsafe Cleared|Glitch cleared", "Failsafe снят", "Условие failsafe пропало.", ["Ничего не нужно."], [], ["fs"])
R(r"^Radio Failsafe|Radio Failsafe -|Radio Failsafe$", "Радио failsafe", "Потеряна связь с пультом либо газ ниже FS_THR_VALUE.", ["Проверь приёмник, антенны, дальность и настройку failsafe в пульте.", "FS_THR_ENABLE выбирает действие (RTL/Land/SmartRTL)."], ["FS_THR_ENABLE", "FS_THR_VALUE"], ["fsradio"])
R(r"^GCS Failsafe|GCS Failsafe -", "GCS failsafe", "Потеряна связь с наземной станцией.", ["Проверь телеметрию; FS_GCS_ENABLE, FS_GCS_TIMEOUT."], ["FS_GCS_ENABLE", "FS_GCS_TIMEOUT"], ["fsgcs"])
R(r"^Battery Failsafe|\+ Battery Failsafe|^Battery %d is %s|^Battery \d+ is (low|critical)", "Батарея разряжена (failsafe)", "Напряжение или ёмкость упали ниже порогов BATT_LOW_*/BATT_CRT_*.", ["Немедленно садись или дай автопилоту выполнить BATT_FS_LOW_ACT/BATT_FS_CRT_ACT.", "Проверь калибровку BATT_VOLT_MULT и просадки напряжения под нагрузкой."], ["BATT_LOW_VOLT", "BATT_CRT_VOLT", "BATT_FS_LOW_ACT", "BATT_FS_CRT_ACT", "BATT_VOLT_MULT"], ["fsbatt"])
R(r"Failsafe: Terrain data missing|Restarting RTL - Terrain data missing", "Нет terrain в RTL", "RTL с terrain, а данных нет.", ["Загрузи terrain, RTL_ALT_TYPE=0 для отказа от terrain."], ["RTL_ALT_TYPE", "TERRAIN_ENABLE"], ["terrain"])
R(r"GPS Glitch or Compass error", "GPS глитч или ошибка компаса", "Flag GPS glitch/compass error во время полёта.", ["Проверь EKF, помехи компасу, GPS."], [], ["ekf"])
R(r"SmartRTL Unavailable|SmartRTL deactivated|SmartRTL: lost one point", "SmartRTL недоступен", "Нет достаточно точек пути/память переполнена/GPS потерян.", ["Взлетай с хорошим GPS; SRTL_POINTS/ACCURACY."], ["SRTL_POINTS", "SRTL_ACCURACY"], ["srtl"])
R(r"^Trying (RTL|Land) Mode", "Резервный режим failsafe", "Целевой failsafe-режим невозможен — переключение на запасной.", ["Проверь, чем вызван failsafe (см. предыдущие сообщения)."], [], ["fs"])
R(r"Mode change to .* failed", "Не удалось сменить режим", "Режим требует условий (GPS, миссия, высота); причина — текст после «failed:».", ["Читай причину: нет GPS, не armed, нет миссии, нет rangefinder и т.д.", "Переключись в режим без GPS либо выполни требования."], [], ["modes"])
R(r"Auto: Missing Takeoff Cmd", "В миссии нет TAKEOFF", "Запуск Auto на земле без команды взлёта.", ["Добавь TAKEOFF первым пунктом либо взлети вручную."], [], ["mission"])
R(r"Auto mission changed|Skipping invalid cmd|Unable to start landing sequence|No landing sequence|No return path|Unable to start find", "Проблема миссии Auto", "Миссия изменена/некорректная команда/нет посадочной последовательности.", ["Проверь миссию в планировщике, команды и порядок."], [], ["mission"])
R(r"Vehicle breaching|Terminating due to fence|Fence", "Geofence", "Пересечена граница Fence или fence настроен некорректно.", ["Проверь FENCE_TYPE, FENCE_RADIUS, FENCE_ALT_MAX/MIN, FENCE_MARGIN.", "FENCE_ACTION задаёт реакцию (RTL/Land/Brake).", "Для fence нужен GPS, заготовь полигоны."], ["FENCE_ENABLE", "FENCE_TYPE", "FENCE_ACTION", "FENCE_RADIUS", "FENCE_ALT_MAX", "FENCE_MARGIN"], ["fence"])
R(r"Rangefinder .* (Not Detected|No Data|Not Connected)|RNGFND\d+_PIN|RangeFinder:", "Дальномер", "Rangefinder не обнаружен/нет данных.", ["Проверь тип RNGFND1_TYPE, порт SERIALn_PROTOCOL=9, питание, адрес/скорость.", "Для I2C — адрес RNGFND1_ADDR; проверь диапазон MIN/MAX."], ["RNGFND1_TYPE", "RNGFND1_MIN_CM", "RNGFND1_MAX_CM", "RNGFND1_PIN"], ["rngf"])
R(r"SurfaceTracking|rangefinder (not enabled|unhealthy)|RTL: rangefinder", "Нет дальномера для режима", "Режим требует rangefinder, а он не включён/нездоров.", ["Настрой RNGFND1_*, RTL_ALT_TYPE/PLDP_*."], ["RNGFND1_TYPE", "RTL_ALT_TYPE"], ["rngf"])
R(r"PRX\d+: (No Data|Not Connected)|Configure PRX", "Proximity", "Датчик препятствий не отвечает.", ["Проверь PRX1_TYPE, порт, питание."], ["PRX1_TYPE", "PRX1_MIN", "PRX1_MAX"], ["oa"])
R(r"OA requires reboot|Dijkstra|BendyRuler", "Object Avoidance", "Для смены типа OA нужна перезагрузка или нет данных.", ["Перезагрузи; OA_TYPE, настройки Fence/Proximity."], ["OA_TYPE"], ["oa"])
R(r"PrecLand", "Precision Landing", "Цель потеряна или не инициализирован PrecLand.", ["PLND_ENABLED, PLND_TYPE, калибровка IR-Lock/камеры."], ["PLND_ENABLED", "PLND_TYPE"], ["prec"])
R(r"FlowCal|OptFlow|Optical", "Optical flow", "Не найден оптфлоу или калибровка не удалась.", ["FLOW_TYPE, ориентация FLOW_ORIENT_YAW, высота и освещённость."], ["FLOW_TYPE", "FLOW_ORIENT_YAW"], ["flow"])
R(r"AutoTune", "AutoTune: ход процесса", "Служебные сообщения AutoTune о текущей фазе и найденных коэффициентах (не ошибка).", ["Дождись «AutoTune: Success», затем приземлись в режиме AutoTune (переключатель оставь включённым) и disarm — так коэффициенты сохранятся."], ["AUTOTUNE_AXES", "AUTOTUNE_AGGR"], ["autotune"])
R(r"must be (>|<|>=) ?0|_POS[XYZ]_P must|_VEL[XYZ]_P|_ACCZ_[PI]", "Недопустимый PID/PosControl параметр", "Один из PID-параметров равен 0 или отрицательный.", ["Проверь указанные ATC_*/PSC_* и верни к дефолтам."], ["PSC_POSXY_P", "PSC_POSZ_P", "PSC_VELZ_P", "PSC_ACCZ_P"], ["tune"])
R(r"Motor ?Test|motor test|^%s: (Board initialising|RC not calibrated|vehicle not landed|Safety switch)|Motor Emergency", "Мотор-тест / Compass-Mot отказ", "Тест не может начаться: не armed/не выбрана рама/safety switch/газ.", ["Убери safety switch, откалибруй RC, поставь на землю."], ["MOT_SPIN_ARM"], ["mdisc"])
R(r"ESC calibration|ESC cal", "ESC калибровка", "Неверная последовательность калибровки.", ["Следуй процедуре ESC calibration (ESC_CALIBRATION=3 или Mission Planner)."], ["ESC_CALIBRATION"], ["motors"])
R(r"waiting for ESC RPM|ESC RPM out of range", "Нет RPM от ESC", "Нет телеметрии RPM от ESC (DShot/BLHeli).", ["SERVO_BLH_TRATE, SERVO_BLH_POLES, SERVO_DSHOT_ESC, включи телеметрию, проверь провод."], ["SERVO_BLH_AUTO", "SERVO_BLH_POLES"], ["motors"])
R(r"Turtle: ", "Turtle mode", "Требуется поднять газ.", ["Повысь газ для arm в turtle."], [], [])
R(r"Mag cal|CompassMot|Check compass|Throttle not zero|Not landed|RC not calibrated|Compass disabled", "CompassMot не стартовал", "Для CompassMot нужны калибровка пульта, нулевой газ и компас.", ["Откалибруй RC, газ=0, не armed, компас включён."], ["COMPASS_MOT_X"], ["compassmot"])
R(r"Config Error: fix problem then reboot", "Ошибка конфигурации — нужна перезагрузка", "Прошивка обнаружила критичную ошибку параметров.", ["Исправь параметры (см. красные сообщения выше), перезагрузись."], [], [])
R(r"WDG: T", "Сбрасывался watchdog", "Борт перезагрузился по watchdog — программный зависон.", ["Смотри Internal Errors, питание, нагрузку CPU, SD-карту, перепрошивку."], [], ["logs"])
R(r"Noise .* on motor", "Шум от мотора", "Анализатор шума нашёл пик на моторе.", ["Балансировка, замена мотора/пропа, настройка Notch (INS_HNTCH_*)."], ["INS_HNTCH_FREQ", "INS_HNTCH_ENABLE"], ["vibe"])
R(r"Failed to initiali[sz]e|Failed to allocate|out of memory|Out of memory", "Нехватка памяти / ошибка инициализации", "Не хватило RAM или инициализация сервиса не удалась.", ["Снизь нагрузку (логи, scripting, лишние IMU/GPS), обнови прошивку."], [], [])
R(r"No such mode|mode not available", "Режим недоступен", "Режим не поддерживается в сборке/конфиге.", ["Выбери доступный режим или собери прошивку с нужной опцией."], [], ["modes"])
R(r"Param write denied|Bad rally|rally point|Mission (storage|upload)|upload timeout|Flight plan update rejected|MISSION_ITEM|Need mavlink2|items are supported", "MAVLink: миссия/параметры", "Проблема передачи миссии/параметров/rally.", ["Повтори загрузку; MAVLink2 (SERIALn_PROTOCOL=2); проверь связь."], ["SERIAL1_PROTOCOL"], [])
R(r"signing|Signing", "MAVLink signing", "Ошибки ключа подписи.", ["Снимай подписи при armed не меняется — disarm и повтори."], [], [])
R(r"DFU|Bootloader|bootloader", "Bootloader / DFU", "Операция прошивки отклонена.", ["Используй актуальный bootloader и подписанную/не подписанную прошивку."], [], ["dfu"])
R(r"Node \d+ unhealthy|DNA allocation|Duplicate Node", "DroneCAN узел", "Проблема в CAN-шине или DNA.", ["Проверь терминаторы 120 Ом, питание CAN-устройств, CAN_Dx_PROTOCOL, DroneCAN GUI."], ["CAN_P1_DRIVER", "CAN_D1_PROTOCOL"], ["dronecan"])
R(r"Chute has no|Chute is released", "Парашют", "Не назначен канал/реле.", ["Назначь CHUTE_* и SERVOx_FUNCTION=?"], [], [])
R(r"Tmode", "Toy mode", "Сообщения режима Toy.", ["Для нестандартной прошивки — смотри FLTMODE/TMODE."], [], [])
R(r"Autorot|Governor Fault|H_RSC", "Вертолёт: ротор/autorotation", "Нарушение условий rotor speed controller.", ["Проверь H_RSC_*, датчик скорости ротора, ESC governor."], ["H_RSC_MODE"], [])

# --------------------------- Виртуальные сообщения (собираются из кусков либо с динамическим текстом)
EXTRA = [
    ("PreArm: Battery 1 below minimum arming voltage", "CRITICAL", "Батарея", "AP_BattMonitor_Backend.cpp (update_check)"),
    ("PreArm: Battery 1 below minimum arming capacity", "CRITICAL", "Батарея", "AP_BattMonitor_Backend.cpp (update_check)"),
    ("PreArm: Battery 1 unhealthy", "CRITICAL", "Батарея", "AP_BattMonitor.cpp"),
    ("PreArm: Battery 1 low voltage failsafe", "CRITICAL", "Батарея", "AP_BattMonitor_Backend.cpp (update_check)"),
    ("PreArm: Battery 1 critical voltage failsafe", "CRITICAL", "Батарея", "AP_BattMonitor_Backend.cpp (update_check)"),
    ("PreArm: Battery 1 voltage failsafe critical >= low", "CRITICAL", "Батарея", "AP_BattMonitor_Backend.cpp (update_check)"),
    ("PreArm: AHRS: EKF3 GPS drift X.Xm (needs X.X)", "CRITICAL", "EKF", "AP_NavEKF3_VehicleStatus.cpp"),
    ("PreArm: AHRS: EKF3 GPS horiz error X.Xm (needs X.X)", "CRITICAL", "EKF", "AP_NavEKF3_VehicleStatus.cpp"),
    ("PreArm: AHRS: EKF3 GPS HDOP X.X (needs 2.5)", "CRITICAL", "EKF", "AP_NavEKF3_VehicleStatus.cpp"),
    ("PreArm: AHRS: EKF3 GPS numsats N (needs 6)", "CRITICAL", "EKF", "AP_NavEKF3_VehicleStatus.cpp"),
    ("PreArm: AHRS: EKF3 Mag yaw error x=X.X y=X.X", "CRITICAL", "EKF", "AP_NavEKF3_VehicleStatus.cpp"),
    ("PreArm: AHRS: EKF3 starting GPS checks", "CRITICAL", "EKF", "AP_NavEKF3_VehicleStatus.cpp"),
    ("PreArm: Throttle (RC3) is not neutral", "CRITICAL", "Пульт/RC", "AP_Arming.cpp"),
    ("PreArm: Roll (RC1) is not neutral", "CRITICAL", "Пульт/RC", "AP_Arming.cpp"),
    ("PreArm: Throttle (RC3) too high", "CRITICAL", "Пульт/RC", "ArduCopter/AP_Arming.cpp"),
    ("PreArm: Motors: no SERVOx_FUNCTION set to Motor1", "CRITICAL", "Моторы", "AP_MotorsMulticopter.cpp"),
    ("PreArm: Motors: Check frame class and type", "CRITICAL", "Моторы", "AP_Motors_Class.cpp"),
    ("PreArm: Motors: MOT_SPIN_ARM > MOT_SPIN_MIN", "CRITICAL", "Моторы", "AP_MotorsMulticopter.cpp"),
    ("PreArm: Motors: Check MOT_PWM_MIN and MOT_PWM_MAX", "CRITICAL", "Моторы", "AP_MotorsMulticopter.cpp"),
    ("PreArm: Compass not calibrated", "CRITICAL", "Компас", "AP_Compass.cpp"),
    ("PreArm: Compass 2 not found", "CRITICAL", "Компас", "AP_Compass.cpp"),
    ("PreArm: Baro: not healthy", "CRITICAL", "Барометр", "AP_Baro.cpp"),
    ("EKF3 IMU0 is using GPS", "INFO", "EKF", "AP_NavEKF3_Control.cpp"),
    ("EKF3 IMU0 origin set", "INFO", "EKF", "AP_NavEKF3_Control.cpp"),
    ("EKF3 IMU0 tilt alignment complete", "INFO", "EKF", "AP_NavEKF3_Control.cpp"),
    ("EKF3 IMU0 yaw aligned", "INFO", "EKF", "AP_NavEKF3_MagFusion.cpp"),
    ("Low Battery 1, 10.50V, 20%", "WARNING", "Батарея", "AP_BattMonitor.cpp"),
    ("Critical Battery 1, 10.00V, 10%", "CRITICAL", "Батарея", "AP_BattMonitor.cpp"),
    ("Radio Failsafe", "CRITICAL", "Пульт/RC", "events.cpp"),
    ("GCS Failsafe", "CRITICAL", "Телеметрия/GCS", "events.cpp"),
    ("Bad Gyro Health", "CRITICAL", "IMU", "AP_Arming.cpp"),
    ("Bad AHRS", "CRITICAL", "EKF", "AP_Arming.cpp"),
    ("Bad Velocity", "CRITICAL", "EKF", "ArduCopter"),
    ("EKF3 IMU0 MAG0 fusion is disabled", "WARNING", "Компас", "AP_NavEKF3"),
    ("GPS 1: detected u-blox", "INFO", "GPS", "GPS_Backend"),
    ("Lost GPS signal / GPS Glitch", "WARNING", "GPS", "ArduCopter"),
    ("Dead reckoning", "WARNING", "EKF", "ArduCopter"),
    ("Land detector: not landed", "INFO", "Режимы", "land_detector.cpp"),
]

# Коды из LOG: ERR (Subsys, ECode) — AP_Logger.h
ERR_SUBSYS = {
    1: "MAIN", 2: "RADIO", 3: "COMPASS", 4: "OPTFLOW (не используется)", 5: "FAILSAFE_RADIO", 6: "FAILSAFE_BATT",
    7: "FAILSAFE_GPS (не используется)", 8: "FAILSAFE_GCS", 9: "FAILSAFE_FENCE", 10: "FLIGHT_MODE", 11: "GPS", 12: "CRASH_CHECK",
    13: "FLIP", 14: "AUTOTUNE (не используется)", 15: "PARACHUTES", 16: "EKFCHECK", 17: "FAILSAFE_EKFINAV", 18: "BARO", 19: "CPU",
    20: "FAILSAFE_ADSB", 21: "TERRAIN", 22: "NAVIGATION", 23: "FAILSAFE_TERRAIN", 24: "EKF_PRIMARY", 25: "THRUST_LOSS_CHECK",
    26: "FAILSAFE_SENSORS", 27: "FAILSAFE_LEAK", 28: "PILOT_INPUT", 29: "FAILSAFE_VIBE", 30: "INTERNAL_ERROR", 31: "FAILSAFE_DEADRECKON",
}
ERR_SUBSYS_RU = {
    1: "Основной цикл", 2: "Радио/RC", 3: "Компас", 4: "Optflow", 5: "Failsafe: радио", 6: "Failsafe: батарея", 7: "Failsafe: GPS",
    8: "Failsafe: GCS", 9: "Failsafe: Fence", 10: "Смена режима полёта", 11: "GPS", 12: "Crash check", 13: "Flip", 14: "AutoTune",
    15: "Парашют", 16: "EKF check", 17: "Failsafe: EKF/Inav", 18: "Барометр", 19: "CPU", 20: "Failsafe: ADS-B", 21: "Terrain",
    22: "Навигация", 23: "Failsafe: terrain", 24: "Смена основного EKF", 25: "Thrust loss", 26: "Failsafe: сенсоры", 27: "Failsafe: протечка",
    28: "Ввод пилота", 29: "Failsafe: вибрации", 30: "Внутренние ошибки", 31: "Failsafe: dead reckoning",
}
ERR_CODES = [
    (0, "ERROR_RESOLVED / FAILSAFE_RESOLVED", "Проблема устранена / failsafe снят (для любой подсистемы)"),
    (1, "FAILED_TO_INITIALISE / FAILSAFE_OCCURRED / MAIN_INS_DELAY / CRASH_CHECK_CRASH / INTERNAL_ERRORS_DETECTED", "Зависит от подсистемы: для FAILSAFE_* — failsafe сработал; для MAIN(1) — задержка INS; CRASH_CHECK — краш; INTERNAL_ERROR — обнаружены внутренние ошибки; иначе — сбой инициализации"),
    (2, "RADIO_LATE_FRAME / CRASH_CHECK_LOSS_OF_CONTROL / FLIP_ABANDONED / MISSING_TERRAIN_DATA / FAILED_TO_SET_DESTINATION / PARACHUTE_TOO_LOW / EKFCHECK_BAD_VARIANCE / BARO_GLITCH / GPS_GLITCH", "RADIO: поздний кадр RC; CRASH: потеря управления; FLIP: отменён; TERRAIN: нет данных; NAV: не удалось задать цель; PARACHUTE: слишком низко; EKFCHECK: плохая дисперсия; BARO/GPS: глитч"),
    (3, "RESTARTED_RTL / PARACHUTE_LANDED / BAD_DEPTH(Sub)", "NAV: RTL перезапущен; PARACHUTE: уже на земле"),
    (4, "UNHEALTHY / FAILED_CIRCLE_INIT", "Датчик нездоров (компас, GPS, баро) / NAV: не удалось инициировать круг"),
    (5, "DEST_OUTSIDE_FENCE", "NAV: цель за пределами fence"),
    (6, "RTL_MISSING_RNGFND", "NAV: RTL требует rangefinder, нет данных"),
]
INTERNAL_ERRORS = [
    (0, "logger_mapfailure", "Ошибка отображения структуры лога"), (1, "logger_missing_logstructure", "Нет описания структуры лога"),
    (2, "logger_logwrite_missingfmt", "Запись лога без формата"), (3, "logger_too_many_deletions", "Слишком много удалений логов"),
    (4, "logger_bad_getfilename", "Не получено имя лог-файла"), (5, "panic", "AP_HAL::panic() — критическая ошибка"),
    (6, "logger_flushing_without_sem", "Flush лога без семафора"), (7, "logger_bad_current_block", "Битый блок лога"),
    (8, "logger_blockcount_mismatch", "Несовпадение числа блоков лога"), (9, "logger_dequeue_failure", "Ошибка очереди логгера"),
    (10, "constraining_nan", "Попытка ограничить NaN (математика дала NaN) — смотри PID/сенсоры"), (11, "watchdog_reset", "Был сброс по watchdog"),
    (12, "iomcu_reset", "Сброс IOMCU"), (13, "iomcu_fail", "IOMCU не отвечает"), (14, "spi_fail", "Ошибка SPI (датчик/питание)"),
    (15, "main_loop_stuck", "Главный цикл завис"), (16, "gcs_bad_missionprotocol_link", "Ошибка протокола миссий"), (17, "bitmask_range", "Выход за диапазон битовой маски"),
    (18, "gcs_offset", "Ошибочный сдвиг GCS"), (19, "i2c_isr", "Ошибка I2C ISR"), (20, "flow_of_control", "Недостижимый код (баг прошивки)"),
    (21, "switch_full_sector_recursion", "Рекурсия переключения сектора"), (22, "bad_rotation", "Неверная ориентация/rotation"), (23, "stack_overflow", "Переполнение стека"),
    (24, "imu_reset", "Сброс IMU"), (25, "gpio_isr", "Ошибка GPIO ISR"), (26, "mem_guard", "Повреждение памяти (guard)"),
    (27, "dma_fail", "Ошибка DMA"), (28, "params_restored", "Параметры восстановлены (повреждены/сброшены)"), (29, "invalid_arg_or_result", "Неверный аргумент/результат"),
]

SUB_HINTS = {}
from kb_more import *  # noqa
import kb_more
SUB_HINTS = kb_more.SUB_HINTS

import kb_code  # noqa  (правила по коду, вставляются в начало)

# -*- coding: utf-8 -*-
"""Дополнительные правила (подключаются из kb.py в конце)."""
from kb import R, DOCS  # noqa

R(r"^%s Failsafe|Failsafe - |^%s (started|stopped|timeout)", "Failsafe-событие (источник в начале сообщения)",
  "events.cpp: первым словом подставляется источник (Radio / Battery / GCS / EKF / Fence / Terrain ...). «started» — действие failsafe запущено, «timeout» — истёк тайм-аут.",
  ["Найди в логе сообщение выше: оно называет источник failsafe.", "Смотри лог ERR (подсистема FAILSAFE_*) — вкладка «Коды лога».", "Исправь причину и проверь настройки FS_*."],
  ["FS_THR_ENABLE", "BATT_FS_LOW_ACT", "FS_GCS_ENABLE", "FS_EKF_ACTION"], ["fs"])
R(r"Bad AHRS|Bad Gyro Health|Bad Velocity", "Плохой AHRS / гироскопы / скорость",
  "Формулировки pre-arm старых версий / GCS: AHRS или IMU не готовы либо скорость EKF не сходится.",
  ["Не двигай коптер 30 с, перезагрузись; калибровка акселя/компаса; проверка вибраций."], [], ["ekf", "prearm"])
R(r"Dead reckoning", "Dead reckoning — потеря GPS", "EKF летит без внешнего позиционирования (только инерциалка).",
  ["Немедленно садись/RTL; проверь GPS, FS_DR_ENABLE, EK3_SRC*."], ["FS_DR_ENABLE", "FS_DR_TIMEOUT"], ["fsekf"])
R(r"Lost GPS signal", "Потеря GPS", "Нет 3D fix в полёте.", ["Проверь антенну, помехи, режим без GPS."], [], ["gps"])
R(r"Airspeed", "Датчик скорости (для Copter не нужен)", "Датчик airspeed включён, но Copter его не использует.", ["ARSPD_TYPE=0, если датчика нет."], ["ARSPD_TYPE"], [])
R(r"Failed to open ", "Не удалось открыть файл", "Нет SD-карты/файла (terrain, логи, скрипт).", ["Проверь SD, отформатируй FAT32."], [], ["sd"])
R(r"Motor Interlock not configured", "Motor Interlock не настроен", "Interlock задан в параметрах, но аукс-функция не назначена.", ["Назначь RCx_OPTION=32 или отключи Interlock."], ["RC7_OPTION"], [])
R(r"PiccoloCAN|Same rfnd on different CAN", "CAN-устройство", "Неверная конфигурация CAN-периферии.", ["Проверь CAN_Pn_DRIVER, CAN_Dn_PROTOCOL."], ["CAN_P1_DRIVER"], ["dronecan"])
R(r"VTOL Fwd Throttle", "VTOL throttle (только Plane)", "Сообщение относится к QuadPlane.", ["Для Copter не актуально."], [], [])
R(r"Reached maximum descent", "Достигнут лимит снижения", "Посадка: превышено макс. снижение без касания.", ["Проверь высоту, LAND_SPD, rangefinder."], ["LAND_SPD_MS"], [])
R(r"SID_AXIS|Aircraft must be flying|Axis requires", "System ID режим", "Режим System ID не может стартовать.", ["Выбери ось SID_AXIS, лети в AltHold/Loiter вручную."], ["SID_AXIS"], [])
R(r"no terrain data|alt-above-home|unexpected error (calculating|setting)", "Terrain недоступен — используется высота от Home",
  "RTL/Land запросили terrain, данных нет — сработал fallback.", ["TERRAIN_ENABLE=1 и загрузи данные, или RTL_ALT_TYPE=0."], ["TERRAIN_ENABLE", "RTL_ALT_TYPE"], ["terrain"])
R(r"FOLL_ENABLE", "Follow выключен", "Режим Follow требует включённый FOLL.", ["FOLL_ENABLE=1 и перезагрузка."], ["FOLL_ENABLE"], [])
R(r"inconsistent .* deg\. Wait or reboot", "Курс EKF/DCM расходится", "Разные оценки yaw (EKF vs DCM/компас) расходятся на много градусов.",
  ["Подожди или перезагрузись, откалибруй компас."], ["COMPASS_ORIENT"], ["compcal"])
R(r"invalid EKF type|not using configured AHRS type", "Неверный тип EKF", "AHRS_EKF_TYPE не соответствует включённым ядрам.", ["AHRS_EKF_TYPE=3, EK3_ENABLE=1."], ["AHRS_EKF_TYPE", "EK3_ENABLE"], ["ekf"])
R(r"vel error", "Ошибка скорости EKF на земле", "Горизонтальная невязка GPS-скорости >2 м/с до взлёта.", ["Не двигай, подожди; вибрации; плохой GPS."], [], ["ekf"])
R(r"Log buffer not available", "CAN log buffer", "Не хватило памяти под CAN-логи.", ["Отключи CAN_LOGLEVEL."], ["CAN_LOGLEVEL"], [])
R(r"GPS \d+: (probing|specified)|unable to configure band|RTCMv3|GSOF|COM port", "GPS: конфигурация", "Автоопределение/настройка приёмника.",
  ["Часто это просто инфо о детекте; при ошибках проверь GPS_TYPE, баудрейт, GPS_AUTO_CONFIG."], ["GPS_TYPE", "GPS_AUTO_CONFIG"], ["gps"])
R(r"Bad lat or lon|vertex|PolyFence|circle radius|return point", "Ошибка полигонов Fence", "Загруженные fence-данные некорректны.",
  ["Очисти fence и загрузи заново; проверь координаты и количество вершин (≥3)."], ["FENCE_TOTAL"], ["fence"])
R(r"TCAL", "Температурная калибровка IMU", "Служебные сообщения TCAL.", ["failed fit — повтори в большем температурном диапазоне."], ["INS_TCAL1_ENABLE"], [])
R(r"All parameters reset|wiping parameter|Creating |entering lockup|panic\(|dereferencing|deadlock", "Отладочные команды", "Сообщения команд отладки/сброса.", ["Выполняются только явными командами; штатно не появляются."], [], [])
R(r"MISSION_REQUEST", "Старый MAVLink-протокол миссий", "GCS использует устаревший MISSION_REQUEST.", ["Обнови GCS / включи MAVLink2."], [], [])
R(r"OSD|MSP", "OSD/MSP", "OSD не может стартовать.", ["Проверь OSD_TYPE, SERIALn_PROTOCOL=33 (MSP DisplayPort), шрифт."], ["OSD_TYPE"], [])
R(r"VISO|VisOdom|Visual|roll/pitch diff|yaw diff|waiting for AHRS attitude", "Visual Odometry (T265)", "Ориентация камеры не соответствует AHRS.",
  ["VISO_ORIENT, VISO_TYPE, проверь монтаж."], ["VISO_ORIENT", "VISO_TYPE"], ["ekf3src"])
R(r"Field Elevation", "BARO_FIELD_ELV", "Нельзя менять поле при armed.", ["Сделай disarm."], [], [])
R(r"LTC2946|INA239|FuelFlow|device fail|battery .* powering off", "Монитор батареи (I2C)", "Не найден датчик тока/напряжения.",
  ["Проверь шину I2C, BATT_MONITOR, адрес."], ["BATT_MONITOR", "BATT_I2C_BUS"], ["batt"])
R(r"TFMini|Pong", "Дальномер: прошивка", "Версия прошивки датчика старая.", ["Обнови прошивку TFMini до ≥2.0.3."], [], ["rngf"])
R(r"Compass cal object|Cannot start compass thread|MagCal", "Калибровка компаса: внутренняя ошибка", "Не удалось запустить калибровку (память/GPS).", ["Перезагрузись; дождись GPS."], [], ["compcal"])
R(r"Disarm for log download", "Disarm для загрузки лога", "Скачивание лога требует disarm.", ["Сделай disarm и повтори."], [], ["sd"])
R(r"Motors: unable to setup|AP_Relay not available|RC\d+_OPTION|ADSB", "Aux-функция не инициализирована", "Aux-функция недоступна в сборке или неверна.", ["Проверь RCx_OPTION и поддержку функции."], [], [])
R(r"Inverted flight|Flight Mode Pause", "Aux-функция недоступна в режиме", "Функция не поддерживается текущим режимом.", ["Смени режим или выбери другую функцию."], [], [])
R(r"I2C addr|device is null|wrong I2C addr|SPI fail", "Ошибка шины/датчика", "Устройство не отвечает на I2C/SPI.", ["Проверь пайку, адрес, питание, подтягивающие резисторы."], [], [])

SUB_HINTS = {
    "Компас": ("Проблемы с компасом: калибровка, ориентация, помехи.", ["Откалибруй компас вдали от металла.", "Проверь COMPASS_ORIENT и COMPASS_EXTERNAL.", "Убери силовые провода от компаса."], ["compcal"]),
    "GPS": ("Проблемы с GPS: сигнал, кабель, тип.", ["Проверь GPS_TYPE, SERIALn_PROTOCOL=5, питание, открытое небо."], ["gps"]),
    "EKF": ("EKF не доверяет датчикам.", ["Смотри лог XKF*, VIBE; исправь вибрации и помехи."], ["ekf"]),
    "AHRS/EKF": ("AHRS/EKF не готов.", ["Подожди, не двигай; проверь компас и GPS."], ["ekf"]),
    "Батарея": ("Монитор батареи / failsafe.", ["Проверь BATT_MONITOR, калибровку напряжения/тока, пороги BATT_LOW_*/CRT_*."], ["batt", "fsbatt"]),
    "IMU": ("Проблема IMU.", ["Перезагрузись, калибровка акселя, проверь вибрации."], ["acccal", "vibe"]),
    "Барометр": ("Барометр.", ["Закрой поролоном, проверь питание."], []),
    "Geofence": ("Geofence.", ["Проверь FENCE_* и полигоны."], ["fence"]),
    "Дальномер": ("Rangefinder.", ["RNGFND1_TYPE, порт, питание."], ["rngf"]),
    "Моторы": ("Моторы/ESC.", ["Проверь FRAME_*, SERVOx_FUNCTION, калибровку ESC."], ["motors"]),
    "Режимы полёта": ("Режим полёта.", ["Проверь требования режима (GPS, миссия, rangefinder)."], ["modes"]),
    "Failsafe/Crash": ("Failsafe.", ["Найди источник по логам (ERR)."], ["fs"]),
    "Пре-арм проверки": ("Pre-arm.", ["Текст после «PreArm:» — это условие; см. ARMING_CHECK."], ["prearm"]),
    "Логи/SD": ("Логирование.", ["SD-карта FAT32, LOG_BACKEND_TYPE."], ["sd"]),
    "MAVLink/GCS": ("MAVLink.", ["Проверь связь и MAVLink2."], []),
    "DroneCAN": ("CAN.", ["Терминаторы, питание, CAN_Dn_PROTOCOL."], ["dronecan"]),
    "Пульт/RC": ("Пульт.", ["Калибровка, RC_PROTOCOLS, SERIALn_PROTOCOL=23."], ["rc"]),
}

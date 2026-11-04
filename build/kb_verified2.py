# -*- coding: utf-8 -*-
"""Проверенная база, часть 2 (сверено с кодом Copter-4.6.3). Подключается в конце kb_verified.py."""
from kb_verified import V, SKY, NOISE, LOG, REBOOT

GPSFIX = [SKY, NOISE, "Проверь в Status число спутников и HDOP.",
          "Только если причина понятна: EK3_CHECK_SCALE (например 150) увеличивает допуски, а EK3_GPS_CHECK позволяет отключить отдельные проверки."]
SCALE = " Порог умножается на EK3_CHECK_SCALE/100 (по умолчанию 100). После однократного прохождения порог временно ×1.3 (гистерезис)."
EKSRC = "libraries/AP_NavEKF3/AP_NavEKF3_VehicleStatus.cpp, calcGpsGoodToAlign() (EKF2 — аналогично в AP_NavEKF2_VehicleStatus.cpp)"

V("PreArm: AHRS: GPS numsats %u (needs 6)", "EKF: мало спутников (< 6)", "EKF не начнёт использовать GPS, пока спутников < 6 (жёстко в коде). Бит 0 (NSats) в EK3_GPS_CHECK.",
  GPSFIX, ["EK3_GPS_CHECK"], ["gps", "ekf"], EKSRC, diag=["Status/HUD: sats. Лог GPS.NSats."])
V("PreArm: AHRS: GPS HDOP %.1f (needs 2.5)", "EKF: HDOP хуже 2.5", "EKF требует HDOP ≤ 2.5 (в коде: get_hdop() > 250, HDOP хранится ×100). Это отдельно от GPS_HDOP_GOOD. Бит 1 (HDoP) в EK3_GPS_CHECK.",
  GPSFIX, ["EK3_GPS_CHECK", "GPS_HDOP_GOOD"], ["gps", "ekf"], EKSRC)
V("PreArm: AHRS: GPS horiz error %.1fm (needs %.1f)", "EKF: горизонтальная точность GPS хуже 5 м", "Оценка точности от приёмника hAcc > 5 м × масштаб. Бит 3 (position error) в EK3_GPS_CHECK." + SCALE,
  GPSFIX, ["EK3_CHECK_SCALE", "EK3_GPS_CHECK"], ["gps", "ekf"], EKSRC)
V("PreArm: AHRS: GPS vert error %.1fm (needs < %.1f)", "EKF: вертикальная точность GPS хуже 7.5 м", "vAcc от приёмника > 7.5 м × масштаб. Бит 3 (position error) в EK3_GPS_CHECK." + SCALE,
  GPSFIX, ["EK3_CHECK_SCALE", "EK3_GPS_CHECK"], ["gps", "ekf"], EKSRC)
V("PreArm: AHRS: GPS speed error %.1f (needs < %.1f)", "EKF: точность скорости GPS хуже 1 м/с", "Точность скорости от приёмника > 1.0 м/с × масштаб. Бит 2 (speed error) в EK3_GPS_CHECK." + SCALE,
  GPSFIX, ["EK3_CHECK_SCALE", "EK3_GPS_CHECK"], ["gps", "ekf"], EKSRC)
V("PreArm: AHRS: GPS drift %.1fm (needs %.1f)", "EKF: позиция GPS «плывёт» на земле",
  "На земле суммируется смещение позиции GPS (с затуханием 10 с); если > 3 м × масштаб — отказ. Работает только при бите 5 (pos drift) в EK3_GPS_CHECK; по умолчанию EK3_GPS_CHECK=31 — бит 5 выключен." + SCALE,
  GPSFIX + ["Если стартуешь с лодки/машины — сними бит 5 в EK3_GPS_CHECK."], ["EK3_GPS_CHECK", "EK3_CHECK_SCALE"], ["gps", "ekf"], EKSRC)
V(["PreArm: AHRS: GPS horizontal speed %.2fm/s (needs %.2f)", "PreArm: AHRS: GPS vertical speed %.2fm/s (needs %.2f)"], "EKF: GPS показывает движение на земле",
  "На земле отфильтрованная скорость GPS (горизонтальная или вертикальная) > 0.3 м/с × масштаб. Биты 7 (horiz speed) и 6 (vert speed) в EK3_GPS_CHECK, по умолчанию выключены. Особенность кода: в тексте «horizontal speed» печатается накопленный дрейф, а не скорость.",
  GPSFIX + ["С движущейся платформы — сними биты 6/7."], ["EK3_GPS_CHECK", "EK3_CHECK_SCALE"], ["gps", "ekf"], EKSRC)
V("PreArm: AHRS: Mag yaw error x=%.1f y=%.1f", "EKF: компас не согласуется с моделью курса",
  "Тест-отношения магнитометра (magTestRatio.x/y) или курса (yawTestRatio) > 1. Бит 4 (yaw error) в EK3_GPS_CHECK. Если держится > 5 с на земле (disarmed), EKF сам запрашивает сброс курса.",
  ["Перекалибруй компас вдали от металла.", "Проверь COMPASS_ORIENT внешнего компаса.", "Убери коптер с металла/из машины.", "Если внутренний компас в помехах — отключи (COMPASS_USE2/3=0)."],
  ["COMPASS_ORIENT", "COMPASS_USE2", "EK3_GPS_CHECK"], ["compcal", "ekf"], EKSRC, diag=[LOG + ": XKF3.IMX/IMY/IMZ, XKF4.SM."])
V("PreArm: AHRS: EKF starting GPS checks", "EKF начал проверку качества GPS", "Служебное: первая проверка GPS ещё не завершена. Обычно сменяется другим сообщением через секунды.", ["Подожди."], [], ["ekf"], EKSRC)

V("Flight Mode Pause failed", "Пауза не поддерживается в этом режиме", "Аукс-функция «FlightMode Pause/Resume» (RCx_OPTION=178): flightmode->pause() вернул false — текущий режим не умеет паузу.",
  ["Используй паузу в Auto/Guided или выбери другой режим."], [], ["modes"], code="ArduCopter/RC_Channel.cpp")
V("Inverted flight not available in %s mode", "Перевёрнутый полёт недоступен", "Аукс-функция InvertedFlight (RCx_OPTION=43): режим не поддерживает inverted (allows_inverted() = false).", ["Используй режим, где это поддерживается (вертолёт)."], [], [],
  code="ArduCopter/RC_Channel.cpp")
V(["Autorot Mode Not Enabled", "Autorot: Must be Armed and Flying"], "Режим авторотации (вертолёт)", "Not Enabled — авторотация выключена параметрами; Must be Armed and Flying — включать можно только в воздухе.",
  ["Включи авторотацию в параметрах вертолёта."], [], [], code="ArduCopter/mode_autorotate.cpp")
V(["RTL: unexpected error calculating target alt", "RTL: unexpected error setting climb target"], "Внутренняя ошибка расчёта RTL",
  "Не удалось перевести высоту точки возврата в «над Home» или задать цель набора высоты. Обычно из-за отсутствия origin/terrain.", ["Проверь позицию EKF и terrain; сохрани лог и сообщи, если повторяется."], ["RTL_ALT_TYPE"], [],
  code="ArduCopter/mode_rtl.cpp")
V(["Aircraft must be flying", "Axis requires manual throttle", "Axis requires switch from Loiter", "No axis selected, SID_AXIS = 0"], "Режим System ID не стартует",
  "Условия mode_systemid.cpp: SID_AXIS ≠ 0; коптер armed и в воздухе; для части осей нужен режим с ручным газом, для других — переход из Loiter.", ["Задай SID_AXIS, взлети и включай SystemID из подходящего режима."], ["SID_AXIS"], [],
  code="ArduCopter/mode_systemid.cpp, init()")
V("%s: %s", "Мотор-тест: проверка не прошла", "motors->motor_test_checks() вернул ошибку — после имени теста текст причины (обычно «Check frame class and type»).", ["Задай FRAME_CLASS/FRAME_TYPE и перезагрузи."], ["FRAME_CLASS", "FRAME_TYPE"], ["frame"],
  code="ArduCopter/motor_test.cpp")
V("H_RSC_AROT_RUNUP must be > H_RSC_AROT_RAMP", "Вертолёт: время раскрутки после авторотации", "Время раскрутки (runup) должно быть больше времени разгона газа (ramp) хотя бы на 1 с.", ["Исправь параметры раскрутки в группе H_RSC_AROT_."], [], [],
  code="libraries/AC_Autorotation/RSC_Autorotation.cpp")
V(["BendyRuler OA requires reboot", "Dijkstra OA requires reboot", "OA requires reboot"], "Object Avoidance: нужна перезагрузка", "Тип OA сменили, но объект алгоритма создаётся только при старте.", [REBOOT], ["OA_TYPE"], ["oa"],
  code="libraries/AC_Avoidance/AP_OAPathPlanner.cpp")
V("Dijkstra: %s", "Dijkstra: ошибка построения пути", "Алгоритм обхода по fence не смог построить путь; %s — причина (нет fence, мало памяти, точка вне fence…).", ["Проверь полигоны fence и цель маршрута."], ["OA_TYPE"], ["oa"],
  code="libraries/AC_Avoidance/AP_OADijkstra.cpp")
FL = "libraries/AC_Fence/AC_PolyFence_loader.cpp"
V(["AC_Fence: invalid polygon vertex count %u", "AC_Fence: latlon read failed", "AC_Fence: non-positive circle radius", "AC_Fence: polygon read failed", "Fence corrupt", "Fence read failed",
   "PolyFence: Multiple return points found", "PolyFence: latlon read failed"], "Сохранённый fence повреждён",
  "Чтение fence из памяти: полигон < 3 вершин, радиус круга ≤ 0, ошибка чтения координат или несколько точек возврата.", ["Очисти fence и загрузи заново из GCS (Plan → GeoFence)."], ["FENCE_ENABLE"], ["fence"], code=FL)
V(["Bad lat or lon", "Invalid vertex count (%u)", "Multiple return points", "Non-positive circle radius", "Received incorrect type (want=%u got=%u)", "Received incorrect vertex type (want=%u got=%u)",
   "Unexpected vertex count want=%u got=%u ", "Fence validation failed"], "Загружаемый fence некорректен",
  "validate_fence(): неверные координаты, полигон < 3 вершин, несколько точек возврата, радиус ≤ 0, вершины полигона пришли не подряд или не того типа.", ["Перерисуй fence в GCS и загрузи снова; обнови GCS."], [], ["fence"], code=FL + ", validate_fence()")
V("Fence exceeds storage size", "Fence не помещается в память", "Требуемый объём хранилища больше доступного.", ["Упрости полигоны (меньше вершин)."], [], ["fence"], code=FL)
V(["Invalid FENCE_TOTAL", "Invalid fence point, bad count (%u vs %u)", "Invalid fence point, bad lat or lng", "Invalid fence point, index past total (%u >= %u)", "Invalid fence point, index past total(%u >= %u)", "Failed to get return point"],
  "Старый протокол fence (FENCE_POINT)", "Загрузка через устаревший протокол FENCE_POINT: FENCE_TOTAL ≠ 0 и < 5, номер точки ≥ количества, неверные координаты.", ["Используй современную GCS (fence через протокол mission)."], ["FENCE_TOTAL"], ["fence"], code=FL)
V("PolyFence: storage write failed", "Не удалось записать fence", "Ошибка записи точки fence в хранилище.", [REBOOT], [], ["fence"], code=FL)
V("Vehicle contains advanced fences", "На борту fence нового формата", "Через старый протокол нельзя прочитать inclusion/exclusion-полигоны.", ["Используй современную GCS."], [], ["fence"], code=FL)
V(["%s must be < %s", "%s out of range"], "Вертолёт: неверные точки кривой коллектива", "AC_InputManager_Heli: значения IM_STB_COL_1…4 должны быть в 0…100 и строго возрастать.", ["Исправь IM_STB_COL_1 < IM_STB_COL_2 < IM_STB_COL_3 < IM_STB_COL_4."],
  ["IM_STB_COL_1"], [], code="libraries/AC_InputManager/AC_InputManager_Heli.cpp")
V(["PreArm: DroneCAN: %s", "PreArm: PiccoloCAN: %s", "PreArm: FETtec: %s", "PreArm: Generator: %s", "PreArm: Mount: %s", "PreArm: OpenDroneID: %s", "PreArm: VisOdom: %s"],
  "Устройство не прошло свою проверку", "Pre-arm проверка периферии вернула ошибку; после двоеточия — текст от драйвера устройства.", ["Найди в поиске полный текст; проверь подключение и параметры этого устройства."], [], [],
  code="libraries/AP_Arming/AP_Arming.cpp")
V(["PreArm: No mission library present", "PreArm: No rally library present"], "Прошивка собрана без миссий/rally", "Требуется миссия/rally, а библиотеки нет в этой сборке.", ["Убери требование ARMING_MIS_ITEMS или используй стандартную прошивку."], ["ARMING_MIS_ITEMS"], [],
  code="libraries/AP_Arming/AP_Arming.cpp")
V(["PreArm: PiccoloCAN not enabled", "PreArm: Same rfnd on different CAN ports"], "Конфликт настроек CAN", "PiccoloCAN not enabled — протокол назначен, но драйвер не создан; Same rfnd — один тип CAN-дальномера на двух шинах.",
  ["Проверь CAN_D1_PROTOCOL / CAN_P1_DRIVER, перезагрузи."], ["CAN_D1_PROTOCOL", "CAN_P1_DRIVER"], ["dronecan"], code="libraries/AP_Arming/AP_Arming.cpp")
V("PreArm: VTOL Fwd Throttle is not zero", "Канал прямой тяги не на нуле", "Есть аукс-канал прямой тяги (FWD_THR), и он > 2 %.", ["Опусти этот канал в ноль."], [], [], code="libraries/AP_Arming/AP_Arming.cpp")
V("Failed to Set Field Elevation: Armed", "Нельзя менять высоту площадки в полёте", "BARO_FIELD_ELV меняют только disarmed.", ["Сделай disarm."], ["BARO_FIELD_ELV"], [], code="libraries/AP_Baro/AP_Baro.cpp")
V("PreArm: Battery %d feature BATTERY_SUM not available", "Тип Sum недоступен в сборке", "BATT_MONITOR задан как Sum, а прошивка собрана без этой функции.", ["Смени тип или прошивку."], ["BATT_MONITOR"], ["batt"], code="libraries/AP_BattMonitor/AP_BattMonitor.cpp")
V(["FuelFlow: Failed to attach to pin %u", "device fail", "LTC2946: Failed to configure device", "LTC2946: Failed to find device 0x%04x", "Vehicle %d battery %d is powering off"], "Датчик батареи не инициализировался",
  "Драйвер монитора батареи не нашёл/не настроил устройство (I2C или пин), либо смарт-батарея сообщает о выключении.", ["Проверь подключение, BATT_I2C_BUS / BATT_I2C_ADDR, BATT_MONITOR."], ["BATT_MONITOR", "BATT_I2C_BUS", "BATT_I2C_ADDR"], ["batt"],
  code="libraries/AP_BattMonitor/")
V("Log buffer not available", "Нет памяти для лога CAN", "Буфер логирования CAN не выделен.", ["Уменьши CAN_LOGLEVEL или освободи память."], ["CAN_LOGLEVEL"], [], code="libraries/AP_CANManager/AP_CANManager.cpp")
V(["Bootloader erase failed", "Bootloader write1 failed", "Bootloader not signed", "Refusing DFU for secure firmware", "Entering DFU mode"], "Обновление/защита bootloader",
  "Команды обновления bootloader / DFU: ошибка стирания или записи флеша, неподписанный bootloader либо отказ DFU для secure-прошивки.", ["Повтори обновление bootloader из GCS, не отключая питание.", "Для secure-плат используй подписанные образы."], [], ["dfu"],
  code="libraries/AP_CheckFirmware/, libraries/GCS_MAVLink/GCS_Common.cpp")
V(["Compass cal object not initialised", "CompassCalibrator: Cannot start compass thread.", "Mag: WMM table error", "MagCal: No location, fix_radius skipped"], "Калибровка компаса: служебные ошибки",
  "Калибратор не создан или поток не запущен (память), нет данных модели поля для координат, или нет позиции (тогда проверка радиуса пропускается).", [REBOOT, "Для проверки радиуса дождись GPS."], [], ["compcal"],
  code="libraries/AP_Compass/AP_Compass_Calibration.cpp, CompassCalibrator.cpp")
V("DroneCAN DNA allocation failed; database full", "DroneCAN: база node ID заполнена", "Сервер динамических node ID (DNA) не может выдать новый ID.", ["Очисти базу DNA (опция в CAN_D1_UC_OPTION) и перезагрузи; лучше задай устройствам статические ID."], ["CAN_D1_UC_OPTION"], ["dronecan"],
  code="libraries/AP_DroneCAN/AP_DroneCAN_DNA_Server.cpp")
V(["Incorrect Role set for DroneCAN GPS, %d should be Base", "Same Node Id %lu set for multiple GPS"], "DroneCAN GPS: неверная настройка", "Для moving baseline роль узла должна быть Base; или один node ID указан для двух GPS.",
  ["Проверь GPS1_CAN_NODEID / GPS2_CAN_NODEID и типы GPS1_TYPE / GPS2_TYPE (22 = Base, 23 = Rover)."], ["GPS1_CAN_NODEID", "GPS2_CAN_NODEID", "GPS1_TYPE"], ["dronecan", "gps"], code="libraries/AP_GPS/AP_GPS_DroneCAN.cpp")
V(["DroneCAN%u-%u: failed RTCMv3 parser allocation", "u-blox %d: failed RTCMv3 parser allocation"], "Нет памяти для парсера RTCM", "Не удалось выделить память под RTCM-парсер (RTK / moving baseline).", ["Освободи память, отключи ненужные функции."], [], ["gps"], code="libraries/AP_GPS/")
V(["GSOF instance %d has invalid COM port setting of %d", "GSOF instance %d has no port"], "Trimble GSOF: неверный порт", "GPSn_COM_PORT задан неверно или нет UART.", ["Исправь GPS1_COM_PORT."], ["GPS1_COM_PORT"], ["gps"], code="libraries/AP_GPS/AP_GPS_GSOF.cpp")
V("GPS %u: unable to configure band 0x%02x", "u-blox: не удалось настроить диапазон", "Приёмник не принял настройку GNSS-диапазонов (GPS1_GNSS_MODE не поддерживается модулем).", ["Верни GPS1_GNSS_MODE=0 (оставить как настроен модуль)."], ["GPS1_GNSS_MODE"], ["gps"],
  code="libraries/AP_GPS/AP_GPS_UBLOX.cpp")
V(["%s: Failed to attach interrupt to %d", "%s: Failed to detach interrupt from %d", "RPM: Failed to attach to pin %d"], "Не удалось занять пин прерывания", "Пин для PWM-входа (RPM, дальномер и т.п.) недоступен для прерываний или занят.",
  ["Выбери другой пин; если пин — выход SERVOx, поставь SERVOx_FUNCTION=-1."], [], [], code="libraries/AP_HAL/GPIO.cpp")
V(["Failed to allocate window for INS", "Failed to allocate %u bytes for IMU batch sampling", "Failed to allocate %u bytes for notch filter"], "Нет памяти для фильтров IMU", "Не хватило памяти под окно FFT, batch sampler или notch-фильтры.",
  ["Уменьши INS_LOG_BAT_* и число гармоник notch (INS_HNTCH_HMNCS), отключи ненужное."], ["INS_LOG_BAT_MASK", "INS_HNTCH_HMNCS"], ["vibe"], code="libraries/AP_InertialSensor/, libraries/Filter/HarmonicNotchFilter.cpp")
V(["Failed to register accel id %u", "Failed to register gyro id %u"], "Слишком много IMU", "Достигнут максимум INS_MAX_INSTANCES — лишний датчик не зарегистрирован.", ["Обычно ни на что не влияет."], [], [], code="libraries/AP_InertialSensor/AP_InertialSensor.cpp")
V("TCAL[%u]: failed fit", "Температурная калибровка IMU не удалась", "save_calibration() не смог подобрать полином по набранным данным.", ["Повтори калибровку с холодного состояния, охватив больший диапазон температур."], ["INS_TCAL1_ENABLE"], [],
  code="libraries/AP_InertialSensor/AP_InertialSensor_tempcal.cpp")
V(["AP_Logger: IO thread died", "AP_Logger: stuck thread (%s)", "Chip full, logging stopped"], "Логгер не успевает / флеш заполнен", "Поток записи логов завис (медленная или битая SD) или встроенный флеш заполнен.",
  ["Замени/отформатируй SD-карту (быстрая, класс A1).", "Для встроенного флеша — сотри логи.", "Уменьши LOG_BITMASK."], ["LOG_BITMASK", "LOG_FILE_BUFSIZE"], ["sd"], code="libraries/AP_Logger/")
V("Disarm for log download", "Скачивание логов только после disarm", "Загрузка лога по MAVLink запрещена при armed.", ["Сделай disarm и повтори."], [], ["sd"], code="libraries/AP_Logger/AP_Logger_MAVLinkLogTransfer.cpp")
V(["Unable to start landing sequence", "Unable to start find a landing abort sequence"], "В миссии нет посадочной последовательности", "Нет DO_LAND_START (или abort-последовательности), к которой можно перейти.", ["Добавь DO_LAND_START в миссию."], [], ["mission"],
  code="libraries/AP_Mission/AP_Mission.cpp")
V("PreArm: Motors: no SERVOx_FUNCTION set to Motor7 for tail servo", "Трикоптер: не назначено хвостовое серво", "Для FRAME_CLASS=7 (Tri) хвостовое серво должно быть на выходе с SERVOx_FUNCTION=39 (Motor7).",
  ["Назначь выходу хвостового серво SERVOx_FUNCTION=39."], ["SERVO7_FUNCTION", "FRAME_CLASS"], ["frame"], code="libraries/AP_Motors/AP_MotorsTri.cpp")
V(["PreArm: Motors: H_RSC_MODE invalid", "PreArm: Motors: H_RSC_SETPOINT out of range", "PreArm: Motors: H_RSC_IDLE out of range", "PreArm: Motors: H_RSC_CRITICAL out of range", "PreArm: Motors: H_RUNUP_TIME too small",
   "PreArm: Motors: Servo Test is still running", "PreArm: Motors: Set H_COL_ANG_MIN to measured min blade pitch in deg", "PreArm: Motors: Set H_COL_ANG_MAX to measured max blade pitch in deg",
   "PreArm: Motors: H_SW_H3_PHANG out of range", "PreArm: Motors: H_SW1_H3_PHANG out of range", "PreArm: Motors: H_SW2_H3_PHANG out of range", "PreArm: Motors: H_TAIL_SPEED out of range",
   "PreArm: Motors: H_GYR_GAIN out of range", "PreArm: Motors: H_GYR_GAIN_ACRO out of range", "PreArm: Motors: Disabled on heli"], "Вертолёт: неверные параметры ротора/автомата перекоса",
  "AP_MotorsHeli*::arming_checks(): H_RSC_MODE вне допустимых; H_RSC_SETPOINT вне 10…100; H_RSC_IDLE / H_RSC_CRITICAL вне 0…100; время раскрутки ≤ времени разгона (в тексте сообщения написано «H_RUNUP_TIME», реальные параметры — H_RSC_RUNUP_TIME и H_RSC_RAMP_TIME); H_COL_ANG_MIN/MAX не измерены (стоят значения по умолчанию); фазовый угол H3 вне ±30°; H_TAIL_SPEED вне 0…100; H_GYR_GAIN* вне 0…1000; идёт тест сервоприводов.",
  ["Исправь параметр из сообщения по диапазону выше.", "H_COL_ANG_MIN / MAX — измерь реальные углы лопастей угломером."], [], [], code="libraries/AP_Motors/AP_MotorsHeli*.cpp, arming_checks()")
V(["Governor Fault: Rotor Overspeed", "Governor Fault: Rotor Underspeed"], "Вертолёт: губернатор вышел за диапазон", "Обороты ротора вышли за целевые ± диапазон — губернатор отключается.",
  ["Проверь датчик оборотов, параметры губернатора H_RSC_GOV_*, двигатель/ESC."], [], [], code="libraries/AP_Motors/AP_MotorsHeli_RSC.cpp")
V(["NavEKF2: core %d setup failed", "NavEKF2: lane switch %u"], "EKF2: служебные сообщения", "Ядро EKF2 не настроилось / EKF2 сменил основное ядро. Copter по умолчанию использует EKF3.", ["Если EKF2 не нужен — EK2_ENABLE=0."], ["EK2_ENABLE"], ["ekf"],
  code="libraries/AP_NavEKF2/AP_NavEKF2.cpp")
V(["OSD_TYPE2 not compatible with first OSD", "OSD: Failed to load font %u", "AP_OSD: bad font size %u ", "MSP DisplayPort uart not available", "MSP backend not available"], "OSD не инициализировался",
  "Второй OSD несовместим с первым; файл шрифта не найден или неверного размера; для MSP DisplayPort нет UART с SERIALn_PROTOCOL=42 или MSP-бэкенда.", ["Проверь OSD_TYPE / OSD_TYPE2, файлы шрифтов, SERIALn_PROTOCOL=42 для DisplayPort."], ["OSD_TYPE", "OSD_TYPE2"], [],
  code="libraries/AP_OSD/")
V(["FlowCal: failed to start", "OptFlow Cal: failed sensor not enabled"], "Калибровка optical flow не запустилась", "Нет датчика optical flow (FLOW_TYPE=0) или не создан калибратор.", ["Задай FLOW_TYPE, перезагрузи."], ["FLOW_TYPE"], ["flow"],
  code="libraries/AP_OpticalFlow/AP_OpticalFlow.cpp")
V(["Chute has no channel", "Chute has no relay", "AP_Relay not available"], "Парашют не настроен на выход", "Тип выпуска servo — нет выхода с SERVOx_FUNCTION=27; тип relay — нет реле с функцией Parachute.",
  ["Для серво: SERVOx_FUNCTION=27. Для реле: RELAY1_FUNCTION = Parachute."], ["CHUTE_TYPE", "RELAY1_FUNCTION"], [], code="libraries/AP_Parachute/AP_Parachute.cpp")
V("Configure PRX%u_MIN and PRX%u_MAX", "DroneCAN proximity: не задан диапазон", "Для DroneCAN-датчика PRXn_MIN и PRXn_MAX равны 0.", ["Задай PRX1_MIN / PRX1_MAX по характеристикам датчика."], ["PRX1_MIN", "PRX1_MAX"], ["oa"],
  code="libraries/AP_Proximity/AP_Proximity_DroneCAN.cpp")
V(["RPM%u_PIN not set", "RPM%u_PIN=%d invalid", "RPM%u_PIN=%d, set SERVO%u_FUNCTION=-1"], "Датчик оборотов: пин", "RPMn_PIN не задан, неверен или является выходом серво (его нужно освободить через SERVOx_FUNCTION=-1).",
  ["Задай RPM1_PIN; если это выход SERVOx — SERVOx_FUNCTION=-1."], ["RPM1_PIN"], [], code="libraries/AP_RPM/AP_RPM.cpp")
V(["RangeFinder: Altitude reading overflow alert", "RangeFinder: IF signal saturation alert", "RangeFinder: Temperature alert", "RangeFinder: Voltage alert"], "Радар Ainstein LR-D1 сообщает о неисправности",
  "Флаги неисправности от самого датчика: перегрев, питание, насыщение сигнала, переполнение высоты.", ["Проверь питание и условия работы датчика."], ["RNGFND1_TYPE"], ["rngf"], code="libraries/AP_RangeFinder/AP_RangeFinder_Ainstein_LR_D1.cpp")
V("TFMini: FW ver %u.%u.%u (need>=2.0.3)", "TFMini-Plus: старая прошивка", "Версия прошивки датчика < 2.0.3.", ["Обнови прошивку TFMini-Plus утилитой Benewake."], ["RNGFND1_TYPE"], ["rngf"], code="libraries/AP_RangeFinder/AP_RangeFinder_Benewake_TFMiniPlus.cpp")
V(["%s=%d invalid", "%s=%d, set SERVO%u_FUNCTION=-1", "pin conflict RELAY%u_PIN = RELAY%u_PIN"], "Реле: неверный пин", "RELAYn_PIN неверен, занят выходом серво или совпадает с другим реле.", ["Исправь RELAYn_PIN; для выхода серво SERVOx_FUNCTION=-1."], ["RELAY1_PIN"], [],
  code="libraries/AP_Relay/AP_Relay.cpp")
V("SERIAL%u_PROTOCOL: duplicate RCIN not permitted", "Второй порт RCIN запрещён", "RCIN уже назначен на другой UART.", ["Оставь SERIALn_PROTOCOL=23 только на одном порту."], [], ["rc"], code="libraries/AP_SerialManager/AP_SerialManager.cpp")
V(["Terrain: Allocation failed", "waiting for terrain data", "Terrain: clamping offset %.0f to %.0f"], "Terrain: память / загрузка / смещение",
  "Allocation failed — нет памяти под кэш; waiting — данные рельефа ещё загружаются с GCS/SD; clamping — поправка ограничена TERRAIN_OFS_MAX.", ["Подожди загрузки при подключённой GCS с интернетом.", "Если terrain не нужен — TERRAIN_ENABLE=0."],
  ["TERRAIN_ENABLE", "TERRAIN_OFS_MAX"], ["terrain"], code="libraries/AP_Terrain/AP_Terrain.cpp")
V("No such mode %u", "Запрошен несуществующий режим", "GCS или скрипт запросил режим с неизвестным номером.", ["Проверь FLTMODE1…6 и команды GCS."], ["FLTMODE1"], ["modes"], code="libraries/AP_Vehicle/AP_Vehicle.cpp")
V("WDG: T%d SL%u FL%u FT%u FA%x FTP%u FLR%x FICSR%u MM%u MC%u IE%u IEC%u TN:%.4s", "Был сброс по watchdog",
  "После перезагрузки по watchdog выводится снимок состояния (поток TN, последняя ошибка и т.д.). Значит, прошивка зависла.",
  ["Сохрани лог и это сообщение целиком, сообщи на discuss.ardupilot.org.", "Проверь питание платы и SD-карту.", "Обнови прошивку."], [], ["logs"], code="libraries/AP_Vehicle/AP_Vehicle.cpp")
V(["Param write denied (%s)", "Bad rally point ID", "Bad rally point count", "Error setting rally point", "Failed to get rally point", "Flight plan update rejected", "Need mavlink2 for item transfer", "Only %u items are supported",
   "got MISSION_ITEM; GCS should send MISSION_ITEM_INT", "got MISSION_REQUEST; use MISSION_REQUEST_INT!", "Fence upload timeout", "Rally upload timeout", "Mission upload timeout", "Out of memory for upload", "failed to initialize MAVFTP"],
  "MAVLink: ошибка загрузки миссии/параметров", "Параметр только для чтения; неверный номер/количество rally; передача миссии без MAVLink2 или старыми сообщениями; таймаут загрузки; слишком много пунктов; нет памяти.",
  ["Повтори загрузку; телеметрия должна быть в MAVLink2 (SERIALn_PROTOCOL=2).", "Обнови GCS."], ["SERIAL1_PROTOCOL"], [], code="libraries/GCS_MAVLink/")
V(["ERROR: Failed to save signing key", "ERROR: Won't setup signing when armed"], "MAVLink signing", "Ключ подписи не сохранился / нельзя настраивать подпись при armed.", ["Сделай disarm и повтори."], [], [], code="libraries/GCS_MAVLink/GCS_Signing.cpp")
V(["ADSB not available", "Failed to init: RC%u_OPTION: %u "], "Аукс-функция недоступна", "ADSB not available — переключатель ADS-B avoidance есть, но ADS-B выключен/нездоров; Failed to init — функция RCx_OPTION не поддерживается этой сборкой.",
  ["Проверь RCx_OPTION и наличие функции в прошивке."], ["RC7_OPTION"], [], code="libraries/RC_Channel/RC_Channel.cpp")
V("Mission storage failed", "Ошибка хранилища миссии", "StorageManager: ошибка ввода-вывода хранилища (FRAM/флеш).", [REBOOT, "Если повторяется — аппаратная проблема хранилища."], [], [], code="libraries/StorageManager/StorageManager.cpp")

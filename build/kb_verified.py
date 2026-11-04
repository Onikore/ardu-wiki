# -*- coding: utf-8 -*-
"""Проверенная база: каждое сообщение сверено с исходниками Copter-4.6.3.
Ключ — точный шаблон текста (как в data.js). Пороги и значения параметров взяты из кода/описаний @Param.
Поле code — где именно в коде (функция/константы), на чём основано объяснение.
"""
VERIFIED = {}


def V(keys, t, c, f, p=(), d=(), code="", causes=(), diag=(), more=(), ignore=""):
    e = dict(t=t, c=c, f=list(f), p=list(p), d=list(d), code=code, causes=list(causes), diag=list(diag), more=list(more), ignore=ignore)
    for k in ([keys] if isinstance(keys, str) else keys):
        VERIFIED[k] = e


SKY = "Выйди под открытое небо и подожди 2–5 минут, не двигая коптер."
NOISE = "Убери GPS подальше от видеопередатчика, камеры, USB3, ESC и силовых проводов; лучше на мачту."
LOG = "Mission Planner → DataFlash Logs → Review a Log"
REBOOT = "Перезагрузи автопилот (выключи питание полностью)."

# ============================ ArduCopter/AP_Arming.cpp
V("PreArm: System not initialised", "Автопилот ещё не закончил загрузку",
  "Проверка hal.scheduler->is_system_initialized(): основная инициализация (датчики, EKF, периферия) ещё не завершена. Обычно это первые секунды после включения.",
  ["Подожди 10–30 с после подачи питания.", "Если сообщение не уходит — посмотри Messages: выше будут ошибки инициализации конкретного устройства.", REBOOT],
  code="ArduCopter/AP_Arming.cpp, pre_arm_checks()")
V("PreArm: Interlock/E-Stop Conflict", "Motor Interlock и E-Stop назначены одновременно",
  "Есть канал с функцией Motor Interlock (RCx_OPTION=32) и одновременно канал с Motor Emergency Stop (31) или Arm/Emergency Stop. Copter не разрешает эти функции вместе.",
  ["Найди в RCx_OPTION каналы со значениями 32 и 31/165 и оставь только одну из функций."], ["RC7_OPTION", "RC8_OPTION"], ["prearm"],
  code="ArduCopter/AP_Arming.cpp, pre_arm_checks()")
V("PreArm: Motor Interlock Enabled", "Тумблер Motor Interlock включён при арминге",
  "Interlock используется (назначен канал с RCx_OPTION=32) и тумблер в положении «моторы разрешены» (motor_interlock_switch). Arm допускается только при выключенном Interlock.",
  ["Переключи тумблер Interlock в «выключено», сделай arm, затем включи Interlock.", "Если Interlock не нужен (обычно не нужен на мультикоптере) — убери RCx_OPTION=32."], ["RC7_OPTION"], ["prearm"],
  code="ArduCopter/AP_Arming.cpp, pre_arm_checks()")
V("PreArm: Motors: %s", "Ошибка конфигурации моторов (уточнение после «Motors:»)",
  "AP_MotorsMulticopter::arming_checks() вернул ошибку. Возможные тексты: «Check frame class and type» (рама не инициализирована), «no SERVOx_FUNCTION set to MotorN», «MOT_SPIN_MIN too high», «MOT_SPIN_ARM > MOT_SPIN_MIN», «Check MOT_PWM_MIN and MOT_PWM_MAX».",
  ["Смотри конкретную запись ниже в поиске («Check frame class and type» и т.д.)."], ["FRAME_CLASS", "FRAME_TYPE"], ["frame"],
  code="ArduCopter/AP_Arming.cpp → libraries/AP_Motors/AP_MotorsMulticopter.cpp")
V("PreArm: Motors: Check frame class and type", "Рама не задана / не поддерживается",
  "AP_Motors::arming_checks(): initialised_ok() = false — для заданных FRAME_CLASS + FRAME_TYPE не удалось построить схему моторов (не задано или неподдерживаемое сочетание).",
  ["Mission Planner → Setup → Mandatory Hardware → Frame Type: выбери раму (например Quad + X).", "Либо задай FRAME_CLASS (1 Quad, 2 Hexa, 3 Octa, 7 Tri …) и FRAME_TYPE (0 Plus, 1 X …).", "Перезагрузи: схема моторов строится при старте."],
  ["FRAME_CLASS", "FRAME_TYPE"], ["frame"], code="libraries/AP_Motors/AP_Motors_Class.cpp, arming_checks()")
V("PreArm: Motors: no SERVOx_FUNCTION set to Motor%u", "Выход для мотора не назначен",
  "Для мотора N, который нужен выбранной раме, нет ни одного выхода с SERVOx_FUNCTION = MotorN (33 = Motor1, 34 = Motor2, … 40 = Motor8, далее 82+).",
  ["Открой Setup → Servo Output и назначь выходам функции Motor1…MotorN по схеме рамы.", "Проверь, что номер мотора в сообщении совпадает с тем, что нужно раме (Quad — 4 мотора)."],
  ["SERVO1_FUNCTION", "FRAME_CLASS"], ["frame", "motors"], code="libraries/AP_Motors/AP_MotorsMulticopter.cpp, arming_checks()")
V("PreArm: Motors: MOT_SPIN_MIN too high %.2f > 0.3", "MOT_SPIN_MIN больше 0.3",
  "Проверка thr_lin.get_spin_min() > 0.3. Такой минимум газа слишком велик для полёта.",
  ["Установи MOT_SPIN_MIN около 0.15 (по умолчанию) и проверь на стенде, что моторы уверенно крутятся."], ["MOT_SPIN_MIN"], ["motors"],
  code="libraries/AP_Motors/AP_MotorsMulticopter.cpp, arming_checks()")
V("PreArm: Motors: MOT_SPIN_ARM > MOT_SPIN_MIN", "MOT_SPIN_ARM больше MOT_SPIN_MIN",
  "Обороты на арме (MOT_SPIN_ARM, по умолчанию 0.10) должны быть не больше минимальных полётных (MOT_SPIN_MIN, по умолчанию 0.15).",
  ["Уменьши MOT_SPIN_ARM или увеличь MOT_SPIN_MIN так, чтобы MOT_SPIN_ARM ≤ MOT_SPIN_MIN."], ["MOT_SPIN_ARM", "MOT_SPIN_MIN"], ["motors"],
  code="libraries/AP_Motors/AP_MotorsMulticopter.cpp, arming_checks()")
V("PreArm: Motors: Check MOT_PWM_MIN and MOT_PWM_MAX", "Неверные MOT_PWM_MIN / MOT_PWM_MAX",
  "check_mot_pwm_params() не прошла: диапазон PWM для ESC задан некорректно (например MIN ≥ MAX или значения вне допустимых).",
  ["Для обычных PWM-ESC: MOT_PWM_MIN=1000, MOT_PWM_MAX=2000 (или 0/0 — тогда берётся диапазон RC3).", "Для DShot (MOT_PWM_TYPE 4–7) значения тоже должны быть корректны; обычно 1000/2000."],
  ["MOT_PWM_MIN", "MOT_PWM_MAX", "MOT_PWM_TYPE"], ["motors"], code="libraries/AP_Motors/AP_MotorsMulticopter.cpp, arming_checks()")
V("PreArm: RC not found", "Автопилот ни разу не видел сигнал пульта",
  "rc().has_had_rc_receiver() и has_had_rc_override() оба false — с момента включения не пришло ни одного кадра от приёмника и ни одного RC override по MAVLink.",
  ["Включи пульт, проверь, что приёмник привязан (bind) и горит связь.", "Приёмник на UART: этому порту нужен SERIALn_PROTOCOL=23 (RCIN); на порту RCIN/SBUS — ничего настраивать не нужно.",
   "RC_PROTOCOLS = 1 (все протоколы) — если меняли, верни.", "Проверь питание приёмника (5 V) и сигнальный провод.", "Когда полосы в Setup → Radio Calibration задвигались — сделай калибровку."],
  ["RC_PROTOCOLS", "RC_OPTIONS"], ["rc"], code="ArduCopter/AP_Arming.cpp, rc_throttle_failsafe_checks()",
  diag=["Setup → Mandatory Hardware → Radio Calibration: двигаются ли полосы.", "В логе нет сообщений RCIN — данные не приходят."],
  ignore="Для стенда без пульта: снять бит «RC Channels» в ARMING_CHECK и FS_THR_ENABLE=0. В полёте так нельзя.")
V("PreArm: Throttle below failsafe", "Газ ниже порога радио-failsafe",
  "channel_throttle->get_radio_in() < FS_THR_VALUE (по умолчанию 975). Проверка работает при FS_THR_ENABLE ≠ 0. Автопилот видит такой низкий PWM газа, что считает пульт потерянным.",
  ["Посмотри RC3 в Radio Calibration при опущенном стике: он должен быть выше FS_THR_VALUE (обычно ~1000+).", "Перекалибруй пульт; проверь, что в пульте канал газа не урезан (endpoints/subtrim).",
   "Если при выключенном пульте приёмник шлёт газ < 975 — это и есть нормальный failsafe; включи пульт."],
  ["FS_THR_VALUE", "FS_THR_ENABLE", "RC3_MIN"], ["fsradio", "rc"], code="ArduCopter/AP_Arming.cpp, rc_throttle_failsafe_checks()")
V("PreArm: Altitude disparity", "Высота баро и инерциалки расходятся > 1 м",
  "|inertial_nav высота − baro_alt| > PREARM_MAX_ALT_DISPARITY_CM = 100 см. Обычно бывает, если баро «уплыл» (сквозняк, нагрев, солнце) или коптер двигали после включения.",
  ["Не трогай коптер 30–60 с.", REBOOT + " Баро обнуляется при старте.", "Закрой барометр кусочком поролона от света и потока воздуха.", "Проверь вибрации (VIBE.VibeZ) — с ними инерциалка «уплывает»."],
  ["BARO_PRIMARY"], ["prearm", "vibe"], code="ArduCopter/AP_Arming.cpp, barometer_checks(); PREARM_MAX_ALT_DISPARITY_CM=100",
  diag=[LOG + ": BARO.Alt и CTUN.Alt / XKF1.PD в покое."])
V("PreArm: EKF attitude is bad", "EKF не готов по ориентации",
  "pre_arm_ekf_attitude_check(): флаг filt_status.flags.attitude = false — EKF ещё не выровнял крен/тангаж/курс или отбрасывает данные IMU.",
  ["Положи коптер ровно и не двигай 30 с после включения.", "Сделай калибровку акселерометра (6 положений) и Level.", "Если не проходит — смотри сообщения «EKF3 IMU… tilt alignment complete / yaw aligned»: какого этапа нет."],
  ["AHRS_ORIENTATION"], ["ekf", "acccal"], code="ArduCopter/AP_Arming.cpp, parameter_checks() → pre_arm_ekf_attitude_check()")
V("PreArm: Battery failsafe", "Battery failsafe уже сработал",
  "copter.battery.has_failsafed() — напряжение или ёмкость уже прошли порог BATT_LOW_* или BATT_CRT_*, failsafe активен. Arm с активным battery failsafe запрещён.",
  ["Заряди/замени батарею и перезагрузи (failsafe не сбрасывается сам).", "Если батарея полная — сверь напряжение мультиметром и откалибруй BATT_VOLT_MULT.", "Проверь пороги BATT_LOW_VOLT/BATT_CRT_VOLT для своего числа банок (ориентир ~3.5/3.4 В на банку LiPo)."],
  ["BATT_LOW_VOLT", "BATT_CRT_VOLT", "BATT_LOW_MAH", "BATT_CRT_MAH", "BATT_VOLT_MULT"], ["fsbatt", "batt"], code="ArduCopter/AP_Arming.cpp, parameter_checks()")
V("PreArm: Check FS_THR_VALUE", "FS_THR_VALUE задан неверно",
  "Условие: RC3_MIN ≤ FS_THR_VALUE + 10 или FS_THR_VALUE < 910. Порог failsafe должен быть ≥ 910 и минимум на 10 мкс ниже минимума газа.",
  ["Типично: RC3_MIN ≈ 1000 после калибровки, FS_THR_VALUE = 975.", "Если RC3_MIN после калибровки ≤ 985 — расширь ход газа в пульте или уменьши FS_THR_VALUE (но не ниже 910)."],
  ["FS_THR_VALUE", "RC3_MIN"], ["fsradio"], code="ArduCopter/AP_Arming.cpp, parameter_checks()")
V("PreArm: FS_GCS_ENABLE=2 removed, see FS_OPTIONS", "FS_GCS_ENABLE=2 больше не поддерживается",
  "Значение 2 (продолжать миссию в Auto) удалено. Сейчас продолжение настраивается битами FS_OPTIONS.",
  ["Задай FS_GCS_ENABLE: 1 RTL, 3 SmartRTL или RTL, 4 SmartRTL или Land, 5 Land, 6 DO_LAND_START или RTL, 7 Brake или Land.", "Чтобы продолжать Auto при потере GCS — включи соответствующий бит в FS_OPTIONS."],
  ["FS_GCS_ENABLE", "FS_OPTIONS"], ["fsgcs"], code="ArduCopter/AP_Arming.cpp, parameter_checks(); значения из @Param FS_GCS_ENABLE")
V("PreArm: Check ANGLE_MAX", "ANGLE_MAX вне 1000…8000",
  "ANGLE_MAX (в сотых градуса) < 1000 или > 8000, т.е. вне 10°…80°.", ["Установи ANGLE_MAX = 3000 (30°, по умолчанию) или другое значение в диапазоне."], ["ANGLE_MAX"], [],
  code="ArduCopter/AP_Arming.cpp, parameter_checks()")
V("PreArm: Check ACRO_BAL_ROLL/PITCH", "ACRO_BAL_* больше ATC_ANG_*_P",
  "ACRO_BAL_ROLL > ATC_ANG_RLL_P или ACRO_BAL_PITCH > ATC_ANG_PIT_P. Выравнивание в Acro не может быть сильнее угловых P-усилений.",
  ["Уменьши ACRO_BAL_ROLL/PITCH (по умолчанию 1.0) до значения ≤ ATC_ANG_RLL_P / ATC_ANG_PIT_P."], ["ACRO_BAL_ROLL", "ACRO_BAL_PITCH", "ATC_ANG_RLL_P", "ATC_ANG_PIT_P"], [],
  code="ArduCopter/AP_Arming.cpp, parameter_checks()")
V("PreArm: Check PILOT_SPEED_UP", "PILOT_SPEED_UP ≤ 0", "Максимальная скорость подъёма от стика должна быть > 0 (см/с).",
  ["Установи PILOT_SPEED_UP = 250 (по умолчанию)."], ["PILOT_SPEED_UP"], [], code="ArduCopter/AP_Arming.cpp, parameter_checks()")
V("PreArm: Motor Interlock not configured", "Interlock требуется, но не назначен",
  "Для вертолёта (или конфигурации, требующей interlock) не найден канал с RCx_OPTION=32 (Motor Interlock).",
  ["Назначь тумблер с RCx_OPTION=32."], ["RC8_OPTION"], [], code="ArduCopter/AP_Arming.cpp, parameter_checks()")
V("PreArm: Invalid MultiCopter FRAME_CLASS", "FRAME_CLASS не подходит для прошивки",
  "В прошивке мультикоптера FRAME_CLASS указывает на вертолёт (класс Heli) — такая рама требует heli-прошивку.",
  ["Задай FRAME_CLASS для мультикоптера (1 Quad, 2 Hexa, 3 Octa, …) или прошей вертолётную прошивку.", REBOOT],
  ["FRAME_CLASS", "FRAME_TYPE"], ["frame"], code="ArduCopter/AP_Arming.cpp, parameter_checks()")
V("PreArm: ADSB threat detected", "ADS-B: рядом воздушное судно",
  "copter.failsafe.adsb = true — avoidance по ADS-B считает, что рядом угроза.",
  ["Дождись, пока борт уйдёт.", "Если ADS-B не используется — ADSB_TYPE=0."], ["ADSB_TYPE"], [], code="ArduCopter/AP_Arming.cpp, parameter_checks()")
V("PreArm: Bad parameter: %s", "Недопустимые коэффициенты регуляторов",
  "pos_control/attitude_control->pre_arm_checks() нашли параметр с недопустимым значением (обычно P, I или D ≤ 0). После двоеточия — какой параметр.", ["См. конкретное сообщение (ATC_… / PSC_… must be > 0)."], [], ["tune"],
  code="ArduCopter/AP_Arming.cpp, parameter_checks()")
for k, which in [("PreArm: Bad parameter: ATC_%s_P must be > 0", "P"), ("PreArm: Bad parameter: ATC_%s_P must be >= 0", "P"),
                 ("PreArm: Bad parameter: ATC_%s_I must be > 0", "I"), ("PreArm: Bad parameter: ATC_%s_I must be >= 0", "I"),
                 ("PreArm: Bad parameter: ATC_%s_D must be >= 0", "D")]:
    V(k, "Неверный коэффициент " + which + " регулятора ориентации (ATC_…)",
      "AC_AttitudeControl::pre_arm_checks(): коэффициент " + which + " одного из регуляторов ATC_ANG_* / ATC_RAT_* отрицателен или равен нулю там, где нужен > 0. Вместо %s подставится имя регулятора (например ATC_RAT_RLL).",
      ["Открой Full Parameter List, найди указанный ATC_…_" + which + " и верни значение по умолчанию (Reset to default).",
       "Ориентиры по умолчанию для Copter: ATC_RAT_RLL_P / ATC_RAT_PIT_P = 0.135, ATC_RAT_YAW_P = 0.18.", "После ручной правки PID — сделай AutoTune или осторожный тестовый висеж."],
      ["ATC_RAT_RLL_P", "ATC_RAT_PIT_P", "ATC_RAT_YAW_P"], ["tune"], code="libraries/AC_AttitudeControl/AC_AttitudeControl.cpp, pre_arm_checks(); дефолты AC_AttitudeControl_Multi.h")
for k in ["PreArm: Bad parameter: PSC_ACCZ_I must be > 0", "PreArm: Bad parameter: PSC_ACCZ_P must be > 0", "PreArm: Bad parameter: PSC_POSXY_P must be > 0",
          "PreArm: Bad parameter: PSC_POSZ_P must be > 0", "PreArm: Bad parameter: PSC_VELZ_P must be > 0"]:
    V(k, "Неверный коэффициент регулятора позиции (PSC_…)",
      "AC_PosControl::pre_arm_checks(): указанный коэффициент ≤ 0. Без него контроль высоты/позиции не работает.",
      ["Верни параметр к значению по умолчанию (Reset to default в Full Parameter List).", "Дефолты Copter: PSC_POSZ_P = 1.0, PSC_VELZ_P = 5.0, PSC_ACCZ_P = 0.3, PSC_ACCZ_I = 1.0."],
      ["PSC_POSZ_P", "PSC_VELZ_P", "PSC_ACCZ_P", "PSC_ACCZ_I", "PSC_POSXY_P"], ["tune"], code="libraries/AC_AttitudeControl/AC_PosControl.cpp, pre_arm_checks(); дефолты POSCONTROL_* в начале файла")
V("PreArm: High GPS HDOP", "HDOP больше GPS_HDOP_GOOD",
  "gps.get_hdop() > GPS_HDOP_GOOD (по умолчанию 140, т.е. HDOP 1.4). Проверка выполняется, если режим требует GPS или включён fence.",
  [SKY, NOISE, "Проверь в Status число спутников (нужно ≥ 10–12 для хорошего HDOP).", "Только если понимаешь риск: увеличь GPS_HDOP_GOOD (например 200)."],
  ["GPS_HDOP_GOOD"], ["gps"], code="ArduCopter/AP_Arming.cpp, gps_checks(); GPS_HDOP_GOOD_DEFAULT=140 (ArduCopter/config.h)")
V("PreArm: Proximity %d deg, %4.2fm (want > %0.1fm)", "Препятствие ближе допустимого",
  "Включено proximity-avoidance, и датчик видит объект в направлении X° ближе, чем допустимо (дистанция ≤ порога). Порог зависит от AVOID_MARGIN.",
  ["Отодвинь коптер от предметов в указанном направлении.", "Проверь, не видит ли датчик элементы самого коптера (шасси, пропы) — тогда PRX1_IGN_ANG1…4 / PRX1_IGN_WID1…4 или PRX1_ORIENT."],
  ["PRX1_TYPE", "AVOID_MARGIN"], ["oa"], code="ArduCopter/AP_Arming.cpp, proximity_checks()")
V("PreArm: AHRS: %s", "AHRS/EKF не готов (причина после «AHRS:»)",
  "ahrs.pre_arm_check() вернул ошибку — дальше идёт конкретный текст от AHRS или EKF. Найди в поиске точное продолжение (GPS numsats, Mag yaw error, waiting for home…).",
  ["Найди в поиске полный текст сообщения — у каждого варианта своя причина."], [], ["ekf"], code="ArduCopter/AP_Arming.cpp, pre_arm_ekf_checks")
V("PreArm: Need Position Estimate", "Режим требует позицию, а её нет",
  "Текущий режим требует GPS (Loiter, PosHold, Auto, Guided, RTL…), а copter.position_ok() = false: у EKF нет ни абсолютной (GPS), ни относительной (optical flow) позиции, либо активен EKF failsafe.",
  ["Армь в Stabilize / AltHold, если GPS сейчас нет.", SKY + " Дождись сообщений «EKF3 IMU0 is using GPS» и «origin set».", "Для полётов без GPS настрой optical flow + rangefinder и EK3_SRC1_*."],
  ["EK3_SRC1_POSXY", "EK3_SRC1_VELXY"], ["gps", "ekf"], code="ArduCopter/AP_Arming.cpp, gps_checks(); position_ok() в system.cpp")
V("PreArm: Fence enabled, need position estimate", "Fence включён, но нет позиции",
  "Fence (FENCE_ENABLE) требует позицию, а position_ok() = false.",
  [SKY, "Если fence не нужен (полёт в помещении) — FENCE_ENABLE=0."], ["FENCE_ENABLE"], ["fence", "gps"], code="ArduCopter/AP_Arming.cpp, gps_checks()")
V("PreArm: Need Alt Estimate", "Нет оценки высоты",
  "Режим без ручного газа (AltHold, Loiter…) требует высоту, а ekf_alt_ok() = false — EKF не уверен в вертикальной позиции/скорости.",
  ["Подожди, не двигай коптер.", "Проверь барометр и вибрации.", "Армь в Stabilize, если срочно."], ["EK3_SRC1_POSZ"], ["ekf"], code="ArduCopter/AP_Arming.cpp, alt_checks()")
V("PreArm: GPS glitching", "EKF отметил GPS glitch",
  "filt_status.flags.gps_glitching — EKF отклоняет GPS-позицию, она скачет относительно прогноза.",
  [NOISE, "Отойди от зданий/деревьев (переотражения).", "Подожди — флаг снимется, когда данные станут согласованы."], ["GPS1_TYPE"], ["gps"], code="ArduCopter/AP_Arming.cpp, pre_arm_ekf_checks / gps_checks()")
V(["PreArm: EKF compass variance", "PreArm: EKF position variance", "PreArm: EKF velocity variance", "PreArm: EKF height variance"], "Дисперсия EKF выше FS_EKF_THRESH",
  "Соответствующая дисперсия (variance) EKF ≥ FS_EKF_THRESH (по умолчанию 0.8). Это те же величины, по которым в полёте срабатывает EKF failsafe: compass — магнитометр, position/velocity — GPS, height — баро/высота.",
  ["compass: перекалибруй компас вдали от металла, проверь COMPASS_ORIENT и помехи от силовых проводов.", "position/velocity: " + SKY + " " + NOISE, "height: закрой баро от потока/света, проверь вибрации.", "Не повышай FS_EKF_THRESH, пока не нашёл причину."],
  ["FS_EKF_THRESH", "COMPASS_ORIENT"], ["ekf", "compcal", "vibe"], code="ArduCopter/AP_Arming.cpp, pre_arm_ekf_checks; FS_EKF_THRESHOLD_DEFAULT=0.8",
  diag=[LOG + ": XKF4 — SM (mag), SP (pos), SV (vel), SH (hgt); у какого значение > 0.8.", "VIBE.VibeX/Y/Z и Clip."])
V("PreArm: GCS failsafe on", "Активен GCS failsafe",
  "copter.failsafe.gcs = true — связь с наземной станцией была и пропала дольше FS_GCS_TIMEOUT (по умолчанию 5 с), FS_GCS_ENABLE ≠ 0.",
  ["Восстанови связь с GCS (телеметрия, Wi-Fi).", "Если летаешь без GCS — FS_GCS_ENABLE=0."], ["FS_GCS_ENABLE", "FS_GCS_TIMEOUT"], ["fsgcs"], code="ArduCopter/AP_Arming.cpp, parameter_checks()")
V("PreArm: %s mode not armable", "В этом режиме arm запрещён",
  "flightmode->allows_arming(method) = false. Например RTL, Land, SmartRTL, Brake, Flip, Follow, AutoRotate не позволяют arm; Auto/Guided — только при определённых условиях.",
  ["Переключись в Stabilize, AltHold или Loiter, сделай arm, затем переключай режим."], [], ["modes"], code="ArduCopter/AP_Arming.cpp, mandatory_checks()")
V("PreArm: Leaning", "Коптер наклонён больше ANGLE_MAX",
  "Наклон (по acos(cos roll · cos pitch)) больше ANGLE_MAX (по умолчанию 30°). Обычно — коптер стоит на склоне или неверная калибровка Level.",
  ["Поставь на ровную поверхность.", "Если на ровном столе HUD показывает наклон — сделай Accel Calibration и Level."], ["ANGLE_MAX", "AHRS_TRIM_X", "AHRS_TRIM_Y"], ["acccal"],
  code="ArduCopter/AP_Arming.cpp, arm_checks()")
V("PreArm: Throttle too high", "Газ не на минимуме при arm",
  "arm_checks(): (1) в любом режиме — стик газа выше верхней границы мёртвой зоны центра, get_pilot_desired_climb_rate() > 0; (2) в режимах с ручным газом (Stabilize, Acro, Drift) газ должен быть ровно 0. Не проверяется при arm из GCS/скрипта в Guided/Auto.",
  ["Опусти стик газа полностью вниз.", "Проверь Radio Calibration: при опущенном стике RC3 должен совпадать с RC3_MIN.", "Если в пульте стоит триммер/субтрим газа — убери."],
  ["RC3_MIN", "RC3_DZ"], ["rc"], code="ArduCopter/AP_Arming.cpp, arm_checks()")
V(["PreArm: Safety Switch", "PreArm: Hardware safety switch"], "Не нажат аппаратный safety switch",
  "hal.util->safety_switch_state() == SAFETY_DISARMED: аппаратная кнопка безопасности не нажата (светодиод на кнопке мигает).",
  ["Нажми и удерживай кнопку safety ~2 с, пока светодиод не станет гореть постоянно.", "Если кнопки нет: BRD_SAFETY_DEFLT=0 и перезагрузка."],
  ["BRD_SAFETY_DEFLT", "BRD_SAFETYOPTION"], ["safety"], code="ArduCopter/AP_Arming.cpp, arm_checks(); libraries/AP_Arming/AP_Arming.cpp, hardware_safety_check()",
  ignore="Отключение кнопки (BRD_SAFETY_DEFLT=0) — штатная настройка, если кнопки нет.")
V("PreArm: Disarm Switch on", "Тумблер Disarm в положении «disarm»",
  "Канал с аукс-функцией «Disarm» (RCx_OPTION=81) в высоком положении — arm заблокирован.", ["Переключи тумблер в низкое положение."], ["RC7_OPTION"], [],
  code="libraries/AP_Arming/AP_Arming.cpp, disarm_switch_checks()")

# ============================ libraries/AP_Arming/AP_Arming.cpp
V("PreArm: Baro: %s", "Проверка барометра не прошла", "AP_Baro::arming_checks() вернула ошибку; текст после «Baro:» — подробность (not healthy / GPS alt error).", ["Найди полный текст в поиске."], [], [],
  code="libraries/AP_Arming/AP_Arming.cpp, barometer_checks()")
V("PreArm: Baro: not healthy", "Барометр не здоров",
  "AP_Baro::all_healthy() = false — хотя бы один включённый барометр не отдаёт корректные данные.",
  [REBOOT, "Проверь, нет ли рядом с датчиком брызг/пыли; закрой поролоном.", "Если барометр внешний — проверь I2C/SPI-подключение.", "Повторяется на столе — вероятна неисправность платы."],
  ["BARO_PRIMARY"], [], code="libraries/AP_Baro/AP_Baro.cpp, arming_checks()")
V("PreArm: Baro: GPS alt error %.0fm (see BARO_ALTERR_MAX)", "Высота баро и GPS сильно расходятся",
  "Разница между высотой GPS и барометрической высотой (по стандартной атмосфере) больше BARO_ALTERR_MAX (по умолчанию 2000 м). Описание параметра в коде: частая причина — поддельный датчик MS5607 вместо MS5611 на «Pixhawk»-клонах.",
  ["Если плата — клон Pixhawk и ошибка ~ сотни метров: включи нужный бит в BARO_OPTIONS (трактовать MS5611 как MS5607).", "Проверь, что у GPS 3D fix и нормальная высота.", "BARO_ALTERR_MAX=0 отключает проверку (не лечит причину)."],
  ["BARO_ALTERR_MAX", "BARO_OPTIONS"], [], code="libraries/AP_Baro/AP_Baro.cpp, arming_checks(); описание @Param BARO_ALTERR_MAX")
V("PreArm: Airspeed %d not healthy", "Включён датчик airspeed, но он не работает",
  "Датчик airspeed включён и используется (ARSPD_TYPE ≠ 0, ARSPD_USE), но не здоров. Copter им обычно не пользуется.", ["Если датчика нет — ARSPD_TYPE=0."], ["ARSPD_TYPE"], [],
  code="libraries/AP_Arming/AP_Arming.cpp, airspeed_checks()")
V("PreArm: Logging failed", "Логгер перестал писать", "AP::logger().logging_failed() — запись логов на носитель не удалась (ошибка SD/флеша).",
  ["Вытащи и вставь SD-карту, проверь её на компьютере.", "Отформатируй (FAT32 для ≤ 32 ГБ) или замени карту на качественную.", REBOOT], ["LOG_BACKEND_TYPE"], ["sd"], code="libraries/AP_Arming/AP_Arming.cpp, logging_checks()",
  ignore="Бит «Logging Available» в ARMING_CHECK можно снять, но без логов не разобрать аварию.")
V("PreArm: No SD card", "SD-карта не обнаружена", "AP::logger().CardInserted() = false.",
  ["Вставь карту до включения питания.", "Проверь карту на компьютере, отформатируй FAT32.", "Если используешь только флеш/MAVLink-логи — LOG_BACKEND_TYPE соответственно."], ["LOG_BACKEND_TYPE"], ["sd"], code="libraries/AP_Arming/AP_Arming.cpp, logging_checks()")
V("PreArm: Downloading logs", "Идёт скачивание логов", "AP::logger().in_log_download() — во время скачивания логов по MAVLink arm запрещён.",
  ["Дождись окончания или отмени загрузку логов в GCS."], [], ["sd"], code="libraries/AP_Arming/AP_Arming.cpp, logging_checks()")
V("PreArm: Logging not started", "Логгер не начал запись", "Включена проверка логирования, но logger->logging_started() = false на момент arm.",
  ["Проверь SD-карту и LOG_BACKEND_TYPE.", REBOOT], ["LOG_BACKEND_TYPE"], ["sd"], code="libraries/AP_Arming/AP_Arming.cpp")
V("PreArm: Gyros not healthy", "Гироскоп не отдаёт данные", "ins.get_gyro_health_all() = false — хотя бы один используемый гироскоп нездоров.",
  [REBOOT, "Проверь питание платы (просадки при подключении периферии).", "Если повторяется — неисправность IMU; как временная мера можно отключить проблемный IMU (INS_USE2/INS_USE3=0)."], ["INS_USE", "INS_USE2", "INS_USE3"], [],
  code="libraries/AP_Arming/AP_Arming.cpp, ins_checks()")
V("PreArm: Accels not healthy", "Акселерометр не отдаёт данные", "ins.get_accel_health_all() = false.",
  [REBOOT, "Проверь питание.", "При повторении — неисправность IMU; временно INS_USE2/3=0 для проблемного."], ["INS_USE", "INS_USE2", "INS_USE3"], [], code="libraries/AP_Arming/AP_Arming.cpp, ins_checks()")
V("PreArm: Gyros not calibrated", "Гироскоп не откалиброван при старте",
  "ins.gyro_calibrated_ok_all() = false — калибровка гироскопа при включении не прошла (коптер двигали/трясли при старте).", ["Перезагрузи, держа коптер неподвижно первые секунды."], ["INS_GYR_CAL"], [],
  code="libraries/AP_Arming/AP_Arming.cpp, ins_checks()")
V("PreArm: 3D Accel calibration needed", "Не выполнена калибровка акселерометра", "ins.accel_calibrated_ok_all() = false — для одного из акселерометров нет калибровки.",
  ["Setup → Mandatory Hardware → Accel Calibration (6 положений), затем Level."], ["INS_ACCOFFS_X"], ["acccal"], code="libraries/AP_Arming/AP_Arming.cpp, ins_checks()")
V("PreArm: Accels calibrated requires reboot", "После калибровки акселя нужна перезагрузка", "ins.accel_cal_requires_reboot().", [REBOOT], [], ["acccal"], code="libraries/AP_Arming/AP_Arming.cpp, ins_checks()")
V("PreArm: Accels inconsistent", "Акселерометры расходятся",
  "ins_accels_consistent(): показания акселерометров разных IMU расходятся больше ARMING_ACCTHRESH (по умолчанию 0.75 м/с²).",
  ["Сделай Accel Calibration — часто причина в ней.", "Дай плате прогреться 1–2 мин и перезагрузи.", "Проверь вибрации и крепление полётника.", "Определи плохой IMU по логу (IMU/IMU2/IMU3) и при необходимости отключи INS_USE2/3=0."],
  ["ARMING_ACCTHRESH", "INS_USE2", "INS_USE3"], ["acccal", "vibe"], code="libraries/AP_Arming/AP_Arming.cpp, ins_accels_consistent(); AP_ARMING_ACCEL_ERROR_THRESHOLD=0.75",
  diag=[LOG + ": IMU.AccX/Y/Z против IMU2/IMU3 в покое."])
V("PreArm: Gyros inconsistent", "Гироскопы расходятся",
  "ins_gyros_consistent(): гироскопы расходятся больше 5°/с; при нескольких гироскопах после восстановления согласованности нужно ещё 10 с подряд без расхождения.",
  ["Не двигай коптер 10–20 с.", "Перезагрузи неподвижно (гироскоп калибруется при старте).", "При повторении — проверь логи IMU/IMU2, отключи проблемный INS_USE2/3=0."], ["INS_USE2", "INS_USE3"], [],
  code="libraries/AP_Arming/AP_Arming.cpp, ins_gyros_consistent() (порог 5 °/с, 10 000 мс)")
V("PreArm: temperature cal running", "Идёт температурная калибровка IMU", "ins.temperature_cal_running().", ["Дождись окончания (TCAL… completed) или отключи INS_TCALn_ENABLE."], ["INS_TCAL1_ENABLE"], [],
  code="libraries/AP_Arming/AP_Arming.cpp, ins_checks()")
V("PreArm: Batch sampling requires reboot", "Включён batch sampler — нужна перезагрузка", "Batch sampling IMU включён (INS_LOG_BAT_MASK), но ещё не инициализирован.", [REBOOT], ["INS_LOG_BAT_MASK"], [],
  code="libraries/AP_Arming/AP_Arming.cpp, ins_checks()")
V("PreArm: Compass calibration running", "Идёт калибровка компаса", "_compass.is_calibrating().", ["Заверши (Accept) или отмени калибровку."], [], ["compcal"], code="libraries/AP_Arming/AP_Arming.cpp, compass_checks()")
V("PreArm: Compass calibrated requires reboot", "После калибровки компаса нужна перезагрузка", "_compass.compass_cal_requires_reboot().", [REBOOT], [], ["compcal"], code="libraries/AP_Arming/AP_Arming.cpp, compass_checks()")
V("PreArm: Compass not healthy", "Компас нездоров", "_compass.healthy() = false — основной компас не отдаёт корректные данные.",
  ["Проверь подключение внешнего компаса (I2C SDA/SCL, питание GPS-модуля) или DroneCAN.", REBOOT, "Если внешнего компаса нет — проверь COMPASS_USE/COMPASS_PRIO1_ID указывают на существующий."],
  ["COMPASS_USE", "COMPASS_PRIO1_ID"], ["compcal"], code="libraries/AP_Arming/AP_Arming.cpp, compass_checks()")
V("PreArm: Compass offsets too high", "Слишком большие оффсеты компаса",
  "Модуль вектора оффсетов (COMPASS_OFS_X/Y/Z основного компаса) > COMPASS_OFFS_MAX (по умолчанию 1800). Значит, при калибровке рядом с компасом было сильное постоянное поле: силовые провода, магниты моторов, металл.",
  ["Отодвинь компас от силовых проводов, моторов и батареи (GPS-мачта).", "Перекалибруй на улице вдали от металла и машин.", "Внутренний компас на маленьком коптере часто непригоден — используй внешний, внутренний отключи (COMPASS_USE2/3=0 или по приоритету).",
   "COMPASS_OFFS_MAX не поднимай — это скроет проблему."], ["COMPASS_OFFS_MAX", "COMPASS_USE", "COMPASS_USE2"], ["compcal"],
  code="libraries/AP_Arming/AP_Arming.cpp, compass_checks(); AP_COMPASS_OFFSETS_MAX_DEFAULT=1800",
  diag=["Параметры COMPASS_OFS_X/Y/Z: модуль √(x²+y²+z²)."], ignore="Нет: большой оффсет = неверный курс, коптер может «закручиваться» (toilet bowl).")
V("PreArm: Check mag field: %4.0f, max %d, min %d", "Сила магнитного поля вне 185…875 mGauss",
  "Модуль поля основного компаса вне AP_ARMING_COMPASS_MAGFIELD_MIN=185 … MAX=875 mGauss (0.35…1.65 от 530). Значит компас не откалиброван, рядом магнитный предмет или датчик неисправен.",
  ["Перекалибруй компас вдали от металла.", "Убери магнитные предметы рядом с компасом.", "Проверь, что компас не стоит вплотную к силовым проводам."], ["COMPASS_USE"], ["compcal"],
  code="libraries/AP_Arming/AP_Arming.cpp, compass_magfield_expected / compass_checks()")
V("PreArm: Check mag field (xy diff:%.0f>%d)", "Поле компаса по X/Y не совпадает с моделью Земли",
  "Когда известна позиция, компас сравнивается с моделью WMM: максимум |diff| по осям X/Y > ARMING_MAGTHRESH (по умолчанию 100 mGauss).",
  ["Проверь COMPASS_ORIENT (ориентация внешнего компаса).", "Перекалибруй вдали от металла.", "Убери помехи от силовых проводов."], ["ARMING_MAGTHRESH", "COMPASS_ORIENT"], ["compcal"],
  code="libraries/AP_Arming/AP_Arming.cpp, compass_checks()")
V("PreArm: Check mag field (z diff:%.0f>%d)", "Поле компаса по Z не совпадает с моделью Земли",
  "Порог 2 × ARMING_MAGTHRESH. Особенность кода 4.6.3: условие сравнивает |diff.x|, а в тексте печатается diff.z — поэтому число в сообщении может быть меньше порога. Проверка по сути та же: поле не соответствует модели.",
  ["Проверь COMPASS_ORIENT (часто перевёрнут модуль — неверный знак Z).", "Перекалибруй компас."], ["ARMING_MAGTHRESH", "COMPASS_ORIENT"], ["compcal"],
  code="libraries/AP_Arming/AP_Arming.cpp, compass_checks() — строка с fabsf(diff_mgauss.x) > threshold*2")
V("PreArm: Compasses inconsistent", "Компасы противоречат друг другу",
  "Compass::consistent(): для каждого компаса, используемого для курса, сравнивается с основным: угол 3D-векторов > 90°, или угол в плоскости XY > 60°, или разница длин XY > 200 mGauss.",
  ["Проверь COMPASS_ORIENT* — у внешних компасов неправильная ориентация даёт именно это.", "Перекалибруй все компасы.", "Если один компас стоит в помехах (внутренний) — отключи его использование (COMPASS_USE2/3=0)."],
  ["COMPASS_ORIENT", "COMPASS_ORIENT2", "COMPASS_USE2", "COMPASS_USE3"], ["compcal"], code="libraries/AP_Compass/AP_Compass.cpp, consistent(); AP_COMPASS_MAX_XY_ANG_DIFF=60°, XYZ=90°, XY_LENGTH=200",
  diag=[LOG + ": MAG.MagX/Y/Z против MAG2/MAG3 — у какого расходится."])
V("PreArm: GPS %i: primary but TYPE 0", "Основной GPS отключён", "GPS с номером i выбран основным (GPS_PRIMARY), но его тип = 0.",
  ["Исправь GPS_PRIMARY или задай тип этому GPS."], ["GPS_PRIMARY", "GPS1_TYPE", "GPS2_TYPE"], ["gps"], code="libraries/AP_Arming/AP_Arming.cpp, gps_checks()")
V("PreArm: GPS %i: Bad fix", "Нет 3D-фикса GPS", "gps.status(i) < GPS_OK_FIX_3D для используемого GPS.", [SKY, NOISE, "Проверь провод/разъём антенны."], ["GPS1_TYPE"], ["gps"],
  code="libraries/AP_Arming/AP_Arming.cpp, gps_checks()")
V("PreArm: GPS %i: not healthy", "GPS не отвечает / нестабилен", "gps.is_healthy(i) = false — данные не приходят или приходят с перебоями.",
  ["Проверь провода TX/RX и питание GPS.", "SERIALn_PROTOCOL=5 на нужном порту, GPS1_TYPE=1 (авто).", "Для DroneCAN: CAN_P1_DRIVER=1, CAN_D1_PROTOCOL=1, GPS1_TYPE=9."], ["GPS1_TYPE", "GPS_AUTO_CONFIG"], ["gps"],
  code="libraries/AP_Arming/AP_Arming.cpp, gps_checks()")
V("PreArm: AHRS: waiting for home", "Home ещё не установлен", "AP::ahrs().home_is_set() = false — Home ставится после того, как EKF получил позицию.",
  [SKY, "В помещении без GPS используй режимы без GPS."], [], ["gps"], code="libraries/AP_Arming/AP_Arming.cpp, gps_checks()")
V("PreArm: GPS positions differ by %4.1fm", "Два GPS расходятся > 50 м", "AP_GPS::all_consistent(): расстояние между позициями GPS1 и GPS2 ≥ 50 м.",
  ["Подожди, пока оба GPS сойдутся.", "Проверь второй GPS; если он неисправен — GPS2_TYPE=0."], ["GPS2_TYPE", "GPS_AUTO_SWITCH"], ["gps"], code="libraries/AP_GPS/AP_GPS.cpp, all_consistent()")
V("PreArm: GPS and AHRS differ by %4.1fm", "GPS и AHRS расходятся > 10 м", "Расстояние между позицией GPS и позицией AHRS > AP_ARMING_AHRS_GPS_ERROR_MAX = 10 м.",
  ["Подожди 1–2 минуты после фикса.", "Если коптер везли после включения — перезагрузи на месте старта."], [], ["gps", "ekf"], code="libraries/AP_Arming/AP_Arming.cpp, gps_checks()")
V("PreArm: GPS %d still configuring this GPS", "GPS ещё настраивается", "gps.first_unconfigured_gps(): автонастройка (GPS_AUTO_CONFIG) ещё не закончена.",
  ["Подожди 10–30 с.", "Если не заканчивается — проверь кабель (особенно TX автопилота → RX GPS) и скорость порта."], ["GPS_AUTO_CONFIG"], ["gps"], code="libraries/AP_Arming/AP_Arming.cpp, gps_checks()")
V("PreArm: Duplicate Aux Switch Options", "Одна аукс-функция на нескольких каналах", "rc().duplicate_options_exist() — одна функция RCx_OPTION назначена на два канала.",
  ["Найди повторяющиеся RCx_OPTION и оставь функцию на одном канале."], [], [], code="libraries/AP_Arming/AP_Arming.cpp, rc_arm_checks()")
V("PreArm: Mode channel and RC%d_OPTION conflict", "Канал режимов занят аукс-функцией", "Канал FLTMODE_CH одновременно имеет RCx_OPTION ≠ 0.",
  ["Либо смени FLTMODE_CH, либо поставь RCx_OPTION=0 для этого канала."], ["FLTMODE_CH"], [], code="libraries/AP_Arming/AP_Arming.cpp, rc_arm_checks()")
V("PreArm: %s (RC%d) is not neutral", "Стик крена/тангажа/рыскания не в центре",
  "Канал Roll/Pitch/Yaw вне мёртвой зоны центра (get_control_in() ≠ 0). Пропускается, если в RC_OPTIONS включён бит ARMING_SKIP_CHECK_RPY.",
  ["Отпусти стики, убери триммеры в пульте.", "Перекалибруй пульт (центр стиков = RCx_TRIM).", "Если стики «плавают» — увеличь мёртвую зону RCx_DZ."], ["RC1_TRIM", "RC2_TRIM", "RC4_TRIM", "RC1_DZ"], ["rc"],
  code="libraries/AP_Arming/AP_Arming.cpp, rc_arm_checks()")
V("PreArm: Throttle (RC%d) is not neutral", "Газ не на нуле",
  "Включён бит ARMING_CHECK_THROTTLE в RC_OPTIONS (по умолчанию), и газ не ноль (get_control_in() ≠ 0).", ["Опусти газ.", "Перекалибруй пульт."], ["RC_OPTIONS", "RC3_MIN"], ["rc"],
  code="libraries/AP_Arming/AP_Arming.cpp, rc_arm_checks()")
V(["PreArm: RC%d_MIN is greater than RC%d_TRIM", "PreArm: RC%d_MAX is less than RC%d_TRIM"], "Нарушен порядок RCx_MIN ≤ TRIM ≤ MAX",
  "Для канала N минимум больше центра или максимум меньше центра — калибровка испорчена.", ["Перекалибруй пульт (Radio Calibration), двигая стики и тумблеры до упоров."], ["RC1_MIN", "RC1_TRIM", "RC1_MAX"], ["rc"],
  code="libraries/AP_Arming/AP_Arming.cpp, rc_calibration_checks()")
V(["PreArm: %s radio min too high", "PreArm: %s radio max too low"], "Пульт не откалиброван (ход канала мал)",
  "RCx_MIN > 1300 или RCx_MAX < 1700 (RC_CALIB_MIN_LIMIT_PWM / RC_CALIB_MAX_LIMIT_PWM) для основного канала — похоже, калибровку не делали.",
  ["Сделай Radio Calibration, двигая стики до упоров.", "Проверь, что в пульте ход каналов полный (endpoints 100%)."], ["RC1_MIN", "RC1_MAX"], ["rc"], code="libraries/AP_Arming/AP_Arming.cpp, rc_checks_copter_sub(); RC_Channel.h")
V("PreArm: RC calibrating", "Идёт калибровка пульта", "rc().calibrating().", ["Закончи калибровку в GCS."], [], ["rc"], code="libraries/AP_Arming/AP_Arming.cpp")
V("PreArm: Radio failsafe on", "Активен радио-failsafe", "AP_Notify::flags.failsafe_radio — пульт потерян или газ ниже FS_THR_VALUE.",
  ["Включи пульт, проверь приёмник.", "Проверь RC3 ≥ FS_THR_VALUE при опущенном газе."], ["FS_THR_ENABLE", "FS_THR_VALUE"], ["fsradio"], code="libraries/AP_Arming/AP_Arming.cpp")
V("PreArm: Missing mission item: %s", "В миссии нет обязательной команды", "Включены проверки ARMING_MIS_ITEMS: в миссии нет нужного типа команды (land, takeoff, …).",
  ["Добавь в миссию нужную команду или убери требование в ARMING_MIS_ITEMS."], ["ARMING_MIS_ITEMS"], ["mission"], code="libraries/AP_Arming/AP_Arming.cpp, mission_checks()")
V("PreArm: Mode requires mission", "Режим требует миссию", "Текущий режим требует миссию, а в ней ≤ 1 команды (только Home).", ["Загрузи миссию или смени режим."], [], ["mission"],
  code="libraries/AP_Arming/AP_Arming.cpp, mission_checks()")
V(["PreArm: No sufficiently close rally point located", "PreArm: Can't check rally without position"], "Нет близкой Rally-точки",
  "Включено требование rally в ARMING_MIS_ITEMS: нужна позиция и rally-точка в пределах RALLY_LIMIT_KM.", ["Добавь rally-точку рядом, дождись GPS или убери требование."], ["ARMING_MIS_ITEMS", "RALLY_LIMIT_KM"], [],
  code="libraries/AP_Arming/AP_Arming.cpp, mission_checks()")
V(["PreArm: Failed to open %s", "PreArm: Failed to open fence storage"], "Не открылось хранилище миссии/fence на SD",
  "mission/fence->failed_sdcard_storage() или StorageManager::storage_failed() — хранилище на SD-карте не открылось.", ["Проверь SD-карту, перезагрузи."], [], ["sd"], code="libraries/AP_Arming/AP_Arming.cpp")
V(["PreArm: SERVO%d_MIN is greater than SERVO%d_TRIM", "PreArm: SERVO%d_MAX is less than SERVO%d_TRIM"], "Нарушен порядок SERVOx_MIN ≤ TRIM ≤ MAX",
  "Для выхода N минимальный PWM больше TRIM или максимальный меньше TRIM.", ["Исправь SERVOx_MIN / TRIM / MAX (например 1000 / 1500 / 2000)."], ["SERVO1_MIN", "SERVO1_TRIM", "SERVO1_MAX"], [],
  code="libraries/AP_Arming/AP_Arming.cpp, servo_checks()")
V("PreArm: SERVO%u_FUNCTION=%u on disabled channel", "Функция на отключённом выходе", "Выходу назначена функция, но этот выход отключён (например назначен как GPIO или используется другой функцией платы).",
  ["Перенеси функцию на рабочий выход или включи выход."], ["SERVO1_FUNCTION"], [], code="libraries/AP_Arming/AP_Arming.cpp, servo_checks()")
V("PreArm: IOMCU is unhealthy", "IO-процессор не отвечает", "iomcu.healthy() = false при BRD_IO_ENABLE ≠ 0 (сопроцессор на Pixhawk с MAIN OUT).",
  [REBOOT, "Перепрошей прошивку (она обновляет и IOMCU).", "Если MAIN OUT не нужны — BRD_IO_ENABLE=0."], ["BRD_IO_ENABLE"], [], code="libraries/AP_Arming/AP_Arming.cpp, board_voltage_checks/system_checks")
V("PreArm: Board (%1.1fv) out of range %1.1f-%1.1fv", "Напряжение питания платы вне диапазона",
  "Напряжение шины 5 В меньше BRD_VBUS_MIN или больше 5.8 В (AP_ARMING_BOARD_VOLTAGE_MAX).", ["Проверь BEC/power module, не питай только от USB.", "Измерь 5 В мультиметром."], ["BRD_VBUS_MIN"], [],
  code="libraries/AP_Arming/AP_Arming.cpp, board_voltage_checks()")
V("PreArm: Servo voltage to low (%1.2fv < %1.2fv)", "Низкое напряжение на шине серво", "Напряжение servo rail меньше BRD_VSERVO_MIN.", ["Проверь питание шины серво (BEC)."], ["BRD_VSERVO_MIN"], [],
  code="libraries/AP_Arming/AP_Arming.cpp, board_voltage_checks()")
V("PreArm: heater temp low (%0.1f < %i)", "IMU не прогрелась", "Температура подогреваемой IMU ниже порога для arm (зависит от BRD_HEAT_TARG).", ["Подожди прогрева.", "BRD_HEAT_TARG=-1 отключает подогрев."], ["BRD_HEAT_TARG"], [],
  code="libraries/AP_Arming/AP_Arming.cpp")
V("PreArm: Param storage failed", "Ошибка хранилища параметров", "hal.storage->healthy() = false.", [REBOOT, "При повторении — проблема FRAM/флеша платы."], [], [], code="libraries/AP_Arming/AP_Arming.cpp, system_checks()")
V("PreArm: parameter storage full", "Хранилище параметров переполнено", "AP_Param::get_eeprom_full().", ["Сбрось параметры к умолчанию (Full Parameter List → Reset) и задай заново только нужные."], [], [],
  code="libraries/AP_Arming/AP_Arming.cpp, system_checks()")
V("PreArm: Main loop slow (%uHz < %uHz)", "Главный цикл медленнее 90 % от нужной частоты",
  "Фактическая частота цикла < 90 % от SCHED_LOOP_RATE — процессор перегружен.",
  ["Уменьши LOG_BITMASK (особенно IMU raw / FFT).", "Уменьши SCHED_LOOP_RATE (например 400 → 300/200) на слабой плате.", "Отключи лишнее: EK2_ENABLE=0, SCR_ENABLE=0 если скрипты не нужны, лишние OSD/CAN."],
  ["SCHED_LOOP_RATE", "LOG_BITMASK"], ["logs"], code="libraries/AP_Arming/AP_Arming.cpp, system_checks()", diag=[LOG + ": PM.NLon, PM.Load, PM.MaxT."])
V("PreArm: Terrain out of memory", "Terrain не выделил память", "terrain->init_failed() при TERRAIN_ENABLE=1.", ["Если terrain не нужен — TERRAIN_ENABLE=0.", "Уменьши потребление памяти другими функциями."], ["TERRAIN_ENABLE"], ["terrain"],
  code="libraries/AP_Arming/AP_Arming.cpp, system_checks()")
V("PreArm: ADSB out of memory", "ADS-B не выделил память", "adsb->init_failed() при включённом ADSB.", ["ADSB_TYPE=0 если не используется."], ["ADSB_TYPE"], [], code="libraries/AP_Arming/AP_Arming.cpp")
V("PreArm: Internal errors 0x%x l:%u %s", "Внутренние ошибки прошивки",
  "AP::internalerror().errors() ≠ 0. 0x… — битовая маска (расшифровка на вкладке «Коды лога»), l: — строка кода, где возникла последняя ошибка.",
  ["Расшифруй маску на вкладке «Коды лога».", REBOOT, "Если ошибка повторяется — сохрани лог и сообщи на discuss.ardupilot.org (укажи маску и l:)."], [], ["logs"],
  code="libraries/AP_Arming/AP_Arming.cpp, system_checks(); libraries/AP_InternalError/AP_InternalError.h")
V(["PreArm: terrain disabled", "PreArm: terrain required but disabled"], "Миссия требует terrain, а он отключён",
  "В миссии есть точки с высотой над рельефом, а TERRAIN_ENABLE=0 (или terrain недоступен).", ["TERRAIN_ENABLE=1 и дай данным загрузиться, или переведи точки миссии в высоту над Home."], ["TERRAIN_ENABLE"], ["terrain"],
  code="libraries/AP_Arming/AP_Arming.cpp, terrain_checks()")
V("PreArm: Multiple SERIAL ports configured for RC input", "Несколько портов RCIN", "Найдено больше одного SERIALn_PROTOCOL=23.", ["Оставь RCIN только на одном порту."], [], ["rc"], code="libraries/AP_Arming/AP_Arming.cpp")
V("PreArm: Motors Emergency Stopped", "Включён Emergency Stop", "SRV_Channels::get_emergency_stop() — моторы в аварийном стопе (аукс-функция E-Stop или команда).",
  ["Выключи тумблер E-Stop (RCx_OPTION=31/165)."], ["RC7_OPTION"], [], code="libraries/AP_Arming/AP_Arming.cpp, estop_checks()")
V(["PreArm: CrashDump data detected", "CrashDump data detected"], "На борту есть дамп сбоя",
  "Найдены данные предыдущего аварийного падения прошивки (hardfault).",
  ["Сохрани crash_dump.bin через MAVFTP (Mission Planner → Config → MAVFTP → @SYS) и сообщи разработчикам.", "Чтобы продолжить: перепрошивка стирает дамп; либо снять бит «System» в ARMING_CHECK (не рекомендуется)."], [], ["logs"],
  code="libraries/AP_Arming/AP_Arming.cpp, crashdump_checks()")
V("Warning: Arming Checks Disabled", "Arm выполнен без проверок", "Arm при ARMING_CHECK=0.", ["Верни ARMING_CHECK=1."], ["ARMING_CHECK"], ["prearm"], code="libraries/AP_Arming/AP_Arming.cpp, arm()")
V("PreArm: GPS_AUTO_SWITCH==2 but no blending", "Включено смешивание GPS, но смешивания нет", "GPS_AUTO_SWITCH=2 (blend), но blending недоступен (нет второго GPS или собрано без него).",
  ["GPS_AUTO_SWITCH=1, если GPS один."], ["GPS_AUTO_SWITCH"], ["gps"], code="libraries/AP_Arming/AP_Arming.cpp")
V(["PreArm: Auxiliary authorisation refused", "PreArm: Waiting for auxiliary authorisation", "PreArm: Too many auxiliary authorisers", "PreArm: memory low for auxiliary authorisation"],
  "Внешняя авторизация arm (скрипт/компаньон)", "Скрипт Lua или компаньон-компьютер зарегистрировал «aux auth» и не разрешил arm (refused) или ещё не ответил (waiting).",
  ["Найди скрипт/компаньон, который регистрирует авторизацию, и выясни его условие.", "Если не нужен — отключи скрипт."], ["SCR_ENABLE"], [], code="libraries/AP_Arming/AP_Arming.cpp, aux_auth_checks()")
V("PreArm: AHRS not healthy", "AHRS нездоров", "ahrs.healthy() = false.", ["Подожди после включения; смотри другие сообщения AHRS/EKF."], [], ["ekf"], code="libraries/AP_Arming/AP_Arming.cpp")
V("PreArm: Gyro %d rate %dHz < loop ratex1.8 %dHz", "Частота гироскопа слишком низкая", "Частота гироскопа < 1.8 × частоты основного цикла.", ["Уменьши SCHED_LOOP_RATE или увеличь частоту IMU (INS_GYRO_RATE)."], ["SCHED_LOOP_RATE", "INS_GYRO_RATE"], [],
  code="libraries/AP_InertialSensor/AP_InertialSensor.cpp, pre_arm_check_gyro_backend_rate_hz()")

# ============================ AHRS / EKF текст после «PreArm: AHRS:»
V(["PreArm: AHRS: EKF3 not started", "PreArm: AHRS: EKF2 not started"], "Выбранный EKF не запущен", "AHRS_EKF_TYPE указывает на EKF, который не стартовал (выключен EKn_ENABLE или не хватило памяти).",
  ["AHRS_EKF_TYPE=3 и EK3_ENABLE=1.", "Смотри сообщения «EKF3 not enough memory / allocation failed».", REBOOT], ["AHRS_EKF_TYPE", "EK3_ENABLE"], ["ekf"], code="libraries/AP_AHRS/AP_AHRS.cpp, pre_arm_check()")
V("PreArm: AHRS: Not healthy", "AHRS/EKF нездоров (без подробностей)", "AP_AHRS::healthy() (или DCM) = false, а конкретная причина не сформирована.", ["Подожди 30–60 с.", "Ищи другие сообщения EKF рядом.", REBOOT], [], ["ekf"],
  code="libraries/AP_AHRS/AP_AHRS.cpp, pre_arm_check()")
V(["PreArm: AHRS: EKF3 still initialising", "PreArm: AHRS: EKF2 still initialising"], "EKF ещё инициализируется", "Ядро EKF ещё не завершило старт.", ["Подожди несколько секунд."], [], ["ekf"],
  code="libraries/AP_NavEKF3/AP_NavEKF3_core.cpp")
V(["PreArm: AHRS: EKF3 init failure: No GPS lock", "PreArm: AHRS: EKF2 init failure: No GPS lock"], "EKF ждёт GPS (режим без бокового скольжения)",
  "Срабатывает при assume_zero_sideslip() — это для самолётов. На Copter это сообщение обычно не появляется.", ["Если появилось — дождись 3D fix."], [], ["gps"], code="libraries/AP_NavEKF3/AP_NavEKF3_core.cpp")
V(["PreArm: AHRS: Waiting for 3D fix"], "EKF ждёт 3D-фикс GPS", "У выбранного GPS нет 3D fix.", [SKY, NOISE], [], ["gps"], code="libraries/AP_NavEKF3/AP_NavEKF3_Measurements.cpp")
V(["PreArm: AHRS: EKF3 core %d unhealthy", "PreArm: AHRS: EKF2 core %d unhealthy"], "Ядро EKF нездорово",
  "NavEKF3_core::healthy() = false, и у ядра нет более конкретной причины. Условия: (1) внутренние ошибки фильтра (faults ≠ 0); (2) одновременно velTestRatio, posTestRatio и hgtTestRatio > 1; (3) с момента старта EKF меньше 1 с; (4) на земле без внешней позиции (AID_NONE): горизонтальная инновация позиции > 1 м или высоты > 1 м — коптер двигали или баро «уплыл».",
  ["Подожди несколько секунд после включения.", "Не двигай коптер на земле, пока нет GPS.", "Закрой баро, проверь вибрации.", "Если всегда одно ядро — проблемный IMU (EK3_IMU_MASK показывает, какие IMU используются); временно INS_USE2/3=0.", REBOOT],
  ["EK3_IMU_MASK", "INS_USE2", "INS_USE3"], ["ekf", "vibe"], code="libraries/AP_NavEKF3/AP_NavEKF3.cpp, pre_arm_check(); AP_NavEKF3_Outputs.cpp, healthy()",
  diag=[LOG + ": XKF4.SV/SP/SH по ядрам (C=0,1,2) — у кого > 1; XKF4.FS — faults."])
V(["PreArm: AHRS: no EKF3 cores", "PreArm: AHRS: no EKF2 cores"], "EKF не создал ни одного ядра", "Ядра не созданы: нехватка памяти или EK3_IMU_MASK пуст.",
  ["EK3_IMU_MASK ≥ 1, EK3_ENABLE=1.", "Освободи память: EK2_ENABLE=0, SCR_ENABLE=0.", REBOOT], ["EK3_IMU_MASK", "EK3_ENABLE", "EK2_ENABLE"], ["ekf"], code="libraries/AP_NavEKF3/AP_NavEKF3.cpp")
V("PreArm: AHRS: EKF3[%u] vel error %.1f", "На земле скорость GPS не сходится с EKF",
  "На земле при использовании GPS: горизонтальная инновация скорости > 2 м/с (жёстко в коде). То есть GPS показывает движение, которого нет, или EKF «уплыл».",
  [SKY, NOISE, "Не двигай коптер.", REBOOT], [], ["gps", "ekf"], code="libraries/AP_NavEKF3/AP_NavEKF3_Outputs.cpp, pre_arm_check()")
V("PreArm: AHRS: %s %s inconsistent %d deg. Wait or reboot", "Оценки ориентации AHRS расходятся",
  "AP_AHRS сравнивает ориентацию основного EKF с запасной оценкой (DCM): по оси roll/pitch/yaw расхождение больше допустимого.", ["Подожди (оценки сойдутся) или перезагрузи неподвижно.", "При частом повторе по yaw — откалибруй компас."],
  ["COMPASS_ORIENT"], ["ekf", "compcal"], code="libraries/AP_AHRS/AP_AHRS.cpp, attitudes_consistent()")
V("PreArm: AHRS: invalid EKF type", "Неверный AHRS_EKF_TYPE", "AHRS_EKF_TYPE имеет неподдерживаемое значение.", ["AHRS_EKF_TYPE=3 (EKF3)."], ["AHRS_EKF_TYPE"], ["ekf"], code="libraries/AP_AHRS/AP_AHRS.cpp")
V("PreArm: AHRS: not using configured AHRS type", "Используется не тот EKF, что настроен",
  "Активный EKF отличается от AHRS_EKF_TYPE (настроенный не готов, AHRS переключился на запасной) при использовании компаса.", ["Подожди готовности EKF; смотри другие сообщения EKF.", REBOOT], ["AHRS_EKF_TYPE"], ["ekf"],
  code="libraries/AP_AHRS/AP_AHRS.cpp, pre_arm_check()")
for src in ["POSXY", "VELXY", "POSZ", "VELZ", "YAW"]:
    V("PreArm: AHRS: Check EK3_SRC%d_" + src, "Недопустимое значение EK3_SRCn_" + src,
      "AP_NavEKF_Source::pre_arm_check(): у EK3_SRCn_" + src + " значение, которое не поддерживается (ветка default в switch).", ["Задай допустимый источник: по умолчанию POSXY=3 (GPS), VELXY=3 (GPS), POSZ=1 (Baro), VELZ=3 (GPS), YAW=1 (Compass)."],
      ["EK3_SRC1_" + src], ["ekf3src"], code="libraries/AP_NavEKF/AP_NavEKF_Source.cpp, pre_arm_check()")
V("PreArm: AHRS: EK3_MAG_CAL and EK3_SRC1_YAW inconsistent", "EK3_MAG_CAL противоречит источнику курса",
  "EK3_MAG_CAL = 5 или 6 (варианты для GPS-курса), а EK3_SRC1_YAW не GPS.", ["Либо EK3_SRC1_YAW = GPS (2 или 3), либо EK3_MAG_CAL верни к 3 (по умолчанию)."], ["EK3_MAG_CAL", "EK3_SRC1_YAW"], ["ekf3src"],
  code="libraries/AP_NavEKF3/AP_NavEKF3.cpp, pre_arm_check()")

# ============================ AP_BattMonitor
V("PreArm: Battery %d unhealthy", "Монитор батареи нездоров",
  "Драйвер батареи N не создан / не совпадает тип (BATT_MONITOR) или его состояние healthy = false (нет данных от датчика).",
  ["Проверь BATT_MONITOR (например 4 = аналоговый V+I) и перезагрузи после изменения.", "Проверь кабель power module, BATT_VOLT_PIN/BATT_CURR_PIN для своей платы.", "Для I2C/CAN-датчиков — шина и адрес."], ["BATT_MONITOR", "BATT_VOLT_PIN", "BATT_CURR_PIN"], ["batt"],
  code="libraries/AP_BattMonitor/AP_BattMonitor.cpp, arming_checks(); AP_BattMonitor_Backend.cpp")
V("PreArm: Battery %d below minimum arming voltage", "Напряжение ниже BATT_ARM_VOLT", "Напряжение батареи меньше BATT_ARM_VOLT (по умолчанию 0 — проверка выключена).",
  ["Заряди батарею.", "Проверь BATT_ARM_VOLT для своего числа банок."], ["BATT_ARM_VOLT"], ["batt"], code="libraries/AP_BattMonitor/AP_BattMonitor_Backend.cpp, arming_checks()")
V("PreArm: Battery %d below minimum arming capacity", "Остаток ёмкости ниже BATT_ARM_MAH", "Оставшаяся ёмкость меньше BATT_ARM_MAH.", ["Заряди/замени батарею; проверь BATT_CAPACITY."], ["BATT_ARM_MAH", "BATT_CAPACITY"], ["batt"],
  code="libraries/AP_BattMonitor/AP_BattMonitor_Backend.cpp, arming_checks()")
V(["PreArm: Battery %d low voltage failsafe", "PreArm: Battery %d critical voltage failsafe"], "Напряжение уже ниже порога failsafe", "Напряжение ниже BATT_LOW_VOLT / BATT_CRT_VOLT (с учётом BATT_FS_VOLTSRC).",
  ["Заряди батарею.", "Сверь напряжение мультиметром, откалибруй BATT_VOLT_MULT.", "Проверь пороги для своей батареи."], ["BATT_LOW_VOLT", "BATT_CRT_VOLT", "BATT_VOLT_MULT", "BATT_FS_VOLTSRC"], ["batt", "fsbatt"],
  code="libraries/AP_BattMonitor/AP_BattMonitor_Backend.cpp, arming_checks()")
V(["PreArm: Battery %d low capacity failsafe", "PreArm: Battery %d critical capacity failsafe"], "Ёмкость уже ниже порога failsafe", "Оставшаяся ёмкость ниже BATT_LOW_MAH / BATT_CRT_MAH.",
  ["Заряди/замени батарею.", "Если ставил свежую батарею — перезагрузи (счётчик mAh сбрасывается при старте)."], ["BATT_LOW_MAH", "BATT_CRT_MAH", "BATT_CAPACITY"], ["fsbatt"],
  code="libraries/AP_BattMonitor/AP_BattMonitor_Backend.cpp, arming_checks()")
V(["PreArm: Battery %d voltage failsafe critical >= low", "PreArm: Battery %d capacity failsafe critical >= low"], "Пороги failsafe перепутаны",
  "Порог critical не ниже порога low (BATT_CRT_VOLT ≥ BATT_LOW_VOLT или BATT_CRT_MAH ≥ BATT_LOW_MAH), когда оба заданы.", ["Сделай critical меньше low (например LOW 10.5 В, CRT 10.2 В для 3S)."],
  ["BATT_LOW_VOLT", "BATT_CRT_VOLT", "BATT_LOW_MAH", "BATT_CRT_MAH"], ["fsbatt"], code="libraries/AP_BattMonitor/AP_BattMonitor_Backend.cpp, arming_checks()")
V("PreArm: Battery %d %s", "Батарея не прошла проверку (подробность в конце)", "AP_BattMonitor::arming_checks(): после номера — причина от драйвера. Найди полный текст в поиске.", ["См. конкретный вариант сообщения."], [], ["batt"],
  code="libraries/AP_BattMonitor/AP_BattMonitor.cpp")

# ============================ Compass / GPS / IMU libs
V("PreArm: Compass not calibrated", "Компас не откалиброван", "Для одного из используемых компасов нет калибровки (all_configured = false).",
  ["Setup → Mandatory Hardware → Compass → Start (Onboard calibration), крути коптер по всем осям.", REBOOT], ["COMPASS_USE"], ["compcal"], code="libraries/AP_Compass/AP_Compass.cpp, configured()")
V("PreArm: Compass %d not found", "Сохранённый компас не найден", "Компас с сохранённым COMPASS_PRIOn_ID не обнаружен на шине.",
  ["Проверь подключение компаса.", "Если его убрали навсегда — в Setup → Compass удали его из списка приоритетов (или COMPASS_PRIOn_ID=0) и перезагрузи."], ["COMPASS_PRIO1_ID", "COMPASS_PRIO2_ID"], ["compcal"],
  code="libraries/AP_Compass/AP_Compass.cpp, configured()")
V(["PreArm: Compass order change requires reboot", "Compass cal requires reboot after priority change"], "Изменён порядок компасов — нужна перезагрузка", "Список приоритетов изменён, но не применён.", [REBOOT], ["COMPASS_PRIO1_ID"], ["compcal"],
  code="libraries/AP_Compass/AP_Compass.cpp")
V("PreArm: GPS[%u] yaw not available", "Нет курса от GPS", "Курс от GPS (moving baseline / dual antenna) не обновлялся > 15 с.",
  ["Проверь обе антенны и RTK-связь между модулями (GPS1_TYPE / GPS2_TYPE, GPS1_MB_TYPE / GPS2_MB_TYPE).", "Если GPS-курс не используется — верни EK3_SRC1_YAW=1."], ["GPS1_TYPE", "EK3_SRC1_YAW"], ["gps"], code="libraries/AP_GPS/AP_GPS.cpp, pre_arm_checks()")
V("PreArm: GPS blending unhealthy", "Смешивание GPS нездорово", "GPS_AUTO_SWITCH=2, но смешанный (blended) GPS нездоров.", ["Проверь оба GPS; при проблемах GPS_AUTO_SWITCH=1."], ["GPS_AUTO_SWITCH"], ["gps"],
  code="libraries/AP_GPS/AP_GPS.cpp, pre_arm_checks()")
V("PreArm: Selected GPS Node %lu not set as instance %d", "DroneCAN GPS: выбранный узел не найден", "GPSn_CAN_NODEID задан, но узел с таким ID не стал этим экземпляром GPS.",
  ["Проверь ID узла в DroneCAN GUI и GPS1_CAN_NODEID / GPS2_CAN_NODEID."], ["GPS1_TYPE"], ["dronecan", "gps"], code="libraries/AP_GPS/AP_GPS_DroneCAN.cpp")
V(["PreArm: Rangefinder %X: Not Detected", "PreArm: Rangefinder %X: No Data", "PreArm: Rangefinder %X: Not Connected"], "Дальномер не работает",
  "Not Detected — драйвер не создан (датчик не найден при старте); No Data — данных нет; Not Connected — нет связи.",
  ["Проверь RNGFND1_TYPE, порт (SERIALn_PROTOCOL=9 для UART), I2C-адрес, питание.", "Not Detected — перезагрузи после исправления (поиск датчика только при старте)."], ["RNGFND1_TYPE"], ["rngf"],
  code="libraries/AP_RangeFinder/AP_RangeFinder.cpp, prearm_healthy()")
V(["PreArm: RNGFND%u_PIN not set", "PreArm: RNGFND%u_PIN=%d invalid", "PreArm: RNGFND%u_PIN=%d, set SERVO%u_FUNCTION=-1"], "Пин аналогового/PWM-дальномера",
  "Для дальномера типа, читающего пин, RNGFNDn_PIN не задан, неверен или занят выходом серво.", ["Задай верный RNGFNDn_PIN; если пин — это выход SERVOx, поставь SERVOx_FUNCTION=-1 (GPIO)."], ["RNGFND1_PIN"], ["rngf"],
  code="libraries/AP_RangeFinder/AP_RangeFinder.cpp")

# ============================ Copter runtime (events / failsafe / ekf_check / crash_check)
V("Crash: Disarming: AngErr=%.0f>%.0f, Accel=%.1f<%.1f", "Crash check: дизарм",
  "Все условия держались 2 с: armed и не на земле, FS_CRASH_CHECK=1, режим поддерживает проверку, ускорение < 3 м/с², наклон > 15°, ошибка ориентации > 30°, скорость < 10 м/с. Это похоже на опрокидывание/застревание.",
  ["Если коптер реально упал — проверь моторы/пропы/ESC.", "Если дизарм в воздухе: смотри, почему ошибка ориентации > 30° (неверный порядок/направление моторов, перепутаны пропы, отказ мотора, слишком слабые PID).", "Отключать FS_CRASH_CHECK=0 — только понимая риск."],
  ["FS_CRASH_CHECK"], ["fscrash"], code="ArduCopter/crash_check.cpp, crash_check(); CRASH_CHECK_* в начале файла",
  diag=[LOG + ": ATT.Roll/DesRoll, Pitch/DesPitch; RCOU — какой мотор на 100 %, какой на 0."])
V("Potential Thrust Loss (%d)", "Возможная потеря тяги мотора N",
  "1 с подряд: коптер почти ровный (цель наклона < 15°), газ ≥ 90 % или упёрся в верх, и при этом снижается. Номер — мотор, который подозревается.",
  ["Садись. Проверь указанный мотор, ESC, пропеллер (трещины, проскальзывание).", "Проверь, не слишком ли тяжёлый коптер (висение > 70 % газа — мало запаса).", "Проверь просадку батареи."],
  ["MOT_THST_HOVER"], ["motors"], code="ArduCopter/crash_check.cpp, thrust_loss_check(); THRUST_LOSS_CHECK_*")
V("Yaw Imbalance %0.0f%", "Перекос по рысканию",
  "Интегратор регулятора рыскания (ATC_RAT_YAW_I) держится > 75 % от IMAX или упёрся в IMAX — коптеру постоянно не хватает момента по рысканию.",
  ["Проверь, не перекошены ли моторы (наклон мотора даёт момент по курсу).", "Проверь направления вращения и пропеллеры CW/CCW.", "Проверь, нет ли слабого мотора/ESC."], ["ATC_RAT_YAW_IMAX"], ["motors"],
  code="ArduCopter/crash_check.cpp, yaw_imbalance_check(); YAW_IMBALANCE_IMAX_THRESHOLD=0.75")
V("EKF variance", "EKF ненадёжен (предупреждение)",
  "ekf_over_threshold(): считаются превышения FS_EKF_THRESH: магнитометр, скорость (если нет optical flow, двойной порог даёт +2) и позиция. Сообщение — когда условие держится; EKF failsafe — после 1 с (10 итераций при 10 Гц).",
  ["Будь готов перейти в AltHold/Stabilize.", "После посадки смотри XKF4 (SV/SP/SM).", "Типичные причины: помехи компасу (ток моторов), плохой GPS, вибрации."],
  ["FS_EKF_THRESH", "FS_EKF_ACTION"], ["fsekf", "ekf"], code="ArduCopter/ekf_check.cpp, ekf_over_threshold(); EKF_CHECK_ITERATIONS_MAX=10")
V("EKF Failsafe: changed to %s Mode", "EKF failsafe — смена режима", "EKF failsafe сработал, режим сменён согласно FS_EKF_ACTION (1 Land, 2 AltHold, 3 Land даже в Stabilize).",
  ["Возьми управление в AltHold/Stabilize, если безопасно.", "Разбери лог XKF4."], ["FS_EKF_ACTION", "FS_EKF_THRESH"], ["fsekf"], code="ArduCopter/ekf_check.cpp, failsafe_ekf_event()")
V("EKF Failsafe Cleared", "EKF failsafe снят", "Дисперсии вернулись ниже порога.", ["Режим автоматически не возвращается — переключи сам."], [], ["fsekf"], code="ArduCopter/ekf_check.cpp")
V("EKF primary changed:%d", "Сменилось основное ядро EKF", "AHRS переключился на другое ядро EKF (другой IMU).", ["Разовое — не страшно. Частое — проверь IMU/вибрации."], ["EK3_IMU_MASK"], ["ekf"], code="ArduCopter/ekf_check.cpp")
V(["Vibration compensation ON", "Vibration compensation OFF"], "Компенсация вибраций EKF",
  "ON: больше 1 с подряд EKF видит признаки «вибрационного» дрейфа высоты (инновации скорости и позиции по Z обе положительны и дисперсия скорости > 1, или AHRS сообщает vibration affected) при FS_VIBE_ENABLE=1, armed, не в ручном режиме. Copter начинает использовать более устойчивый к вибрациям контроль высоты. OFF — 15 с без признаков.",
  ["Устрани вибрации: балансировка пропов, мягкое крепление полётника, проверка моторов.", "Настрой Harmonic Notch (INS_HNTCH_*).", "Смотри VIBE (VibeZ < 30 хорошо) и Clip."], ["FS_VIBE_ENABLE", "INS_HNTCH_ENABLE"], ["vibe"],
  code="ArduCopter/ekf_check.cpp, check_vibration()")
V("GPS Glitch or Compass error", "EKF: глитч GPS или ошибка компаса", "Флаг gps_glitching от EKF в полёте; пишется ERR GPS/GPS_GLITCH.", ["Будь готов к AltHold/Stabilize.", "После полёта: GPS.NSats/HDop, MAG, XKF3."], [], ["gps", "ekf"],
  code="ArduCopter/events.cpp, gpsglitch_check()")
V("Glitch cleared", "Глитч снят", "Флаг gps_glitching снят.", ["Ничего."], [], [], code="ArduCopter/events.cpp")
V(["Radio Failsafe", "Radio Failsafe - Continuing Auto", "Radio Failsafe - Continuing Guided Mode", "Radio Failsafe - Continuing Landing", "Radio Failsafe - Disarming"],
  "Радио-failsafe", "Пульт потерян (нет кадров или газ < FS_THR_VALUE). Действие — FS_THR_ENABLE (1 RTL, 3 Land, 4 SmartRTL или RTL, 5 SmartRTL или Land, 6 DO_LAND_START или RTL, 7 Brake или Land); «Continuing …» — продолжает по битам FS_OPTIONS; «Disarming» — на земле.",
  ["Проверь антенны приёмника (не за карбоном, не у VTX), дальность.", "Проверь настройку failsafe в приёмнике (No pulses или газ ниже FS_THR_VALUE).", "Смотри в логе RSSI/LQ перед событием."],
  ["FS_THR_ENABLE", "FS_THR_VALUE", "FS_OPTIONS"], ["fsradio"], code="ArduCopter/events.cpp, failsafe_radio_on_event(); значения из @Param FS_THR_ENABLE")
V("Radio Failsafe Cleared", "Пульт снова на связи", "Радио-failsafe снят.", ["Режим не возвращается автоматически — переключи сам."], [], ["fsradio"], code="ArduCopter/events.cpp")
V(["Battery Failsafe", "Battery Failsafe - Continuing Landing", "Battery Failsafe - Disarming", "GCS + Battery Failsafe - Continuing Landing", "Radio + Battery Failsafe - Continuing Landing"],
  "Battery failsafe", "Напряжение/ёмкость прошли BATT_LOW_* или BATT_CRT_*. Действие — BATT_FS_LOW_ACT / BATT_FS_CRT_ACT (0 нет, 1 Land, 2 RTL, 3 SmartRTL или RTL, 4 SmartRTL или Land, 6 DO_LAND_START или RTL, 7 Brake или Land).",
  ["Садись.", "После полёта: сверь BAT.Volt с реальным, калибровка BATT_VOLT_MULT; проверь просадку под нагрузкой (BAT.Volt vs BAT.VoltR).", "Подбери пороги под свою батарею."],
  ["BATT_LOW_VOLT", "BATT_CRT_VOLT", "BATT_FS_LOW_ACT", "BATT_FS_CRT_ACT", "BATT_FS_VOLTSRC"], ["fsbatt"], code="ArduCopter/events.cpp, handle_battery_failsafe(); значения @Param BATT_FS_LOW_ACT (Copter)")
V("Battery %d is %s %.2fV used %.0f mAh", "Батарея перешла в состояние low/critical", "AP_BattMonitor: у батареи N сменилось состояние failsafe (%s = «low», «critical» или «missing, last:» — монитор пропал), напряжение и израсходованные мА·ч.",
  ["Садись. См. «Battery Failsafe»."], ["BATT_LOW_VOLT", "BATT_CRT_VOLT"], ["fsbatt"], code="libraries/AP_BattMonitor/AP_BattMonitor.cpp, check_failsafes()")
V(["GCS Failsafe", "GCS Failsafe - Continuing Auto Mode", "GCS Failsafe - Continuing Landing", "GCS Failsafe - Continuing Pilot Control", "GCS Failsafe - Disarming"],
  "GCS failsafe", "Нет heartbeat от GCS дольше FS_GCS_TIMEOUT (5 с). Действие — FS_GCS_ENABLE (1 RTL, 3 SmartRTL или RTL, 4 SmartRTL или Land, 5 Land, 6 DO_LAND_START или RTL, 7 Brake или Land). По умолчанию FS_OPTIONS продолжает полёт, если пилот управляет вручную («Continuing Pilot Control»).",
  ["Проверь телеметрию.", "Если GCS не нужна в полёте — FS_GCS_ENABLE=0."], ["FS_GCS_ENABLE", "FS_GCS_TIMEOUT", "FS_OPTIONS"], ["fsgcs"], code="ArduCopter/events.cpp, failsafe_gcs_check()/on_event()")
V("GCS Failsafe Cleared", "Связь с GCS восстановлена", "GCS failsafe снят.", ["Ничего."], [], ["fsgcs"], code="ArduCopter/events.cpp")
V(["Failsafe: Terrain data missing", "Restarting RTL - Terrain data missing"], "Нет данных рельефа в полёте",
  "Нужные данные terrain отсутствуют дольше таймаута; Copter делает RTL или повторяет RTL с высотой от Home.", ["Загрузи terrain до полёта (подключи GCS с интернетом) или используй высоту над Home (RTL_ALT_TYPE=0)."], ["TERRAIN_ENABLE", "RTL_ALT_TYPE"], ["terrain"],
  code="ArduCopter/events.cpp, failsafe_terrain_*; mode_rtl.cpp")
V(["SmartRTL Unavailable, Trying RTL Mode", "SmartRTL Unavailable, Using Land Mode"], "SmartRTL недоступен — запасной режим", "Failsafe просил SmartRTL, но путь не записан/деактивирован — включается RTL или Land.",
  ["Проверь, почему SmartRTL деактивирован (сообщение «SmartRTL deactivated: …»)."], ["SRTL_POINTS"], ["srtl"], code="ArduCopter/events.cpp, set_mode_SmartRTL_or_*()")
V(["Trying RTL Mode", "Trying Land Mode"], "Режим failsafe недоступен — пробуем следующий", "Не удалось включить нужный режим (обычно нет позиции) — пробуется RTL, затем Land.", ["Ищи выше причину failsafe и почему режим недоступен."], [], ["fs"],
  code="ArduCopter/events.cpp")
V(["Dead Reckoning started", "Dead Reckoning stopped", "Dead Reckoning timeout"], "Dead reckoning: EKF без внешней позиции",
  "started — EKF перешёл в dead reckoning (потерял GPS, оценивает по инерциалке/ветру); stopped — позиция вернулась; timeout — длится дольше FS_DR_TIMEOUT, затем действие FS_DR_ENABLE (0 нет, 1 Land, 2 RTL, 3 SmartRTL или RTL, 4 SmartRTL или Land, 6 DO_LAND_START или RTL).",
  ["Сразу возьми управление в AltHold/Stabilize или жди действия failsafe.", "После посадки: GPS.Status/NSats в момент потери."], ["FS_DR_ENABLE", "FS_DR_TIMEOUT"], ["fsekf", "gps"],
  code="ArduCopter/events.cpp, failsafe_deadreckon_check(); значения @Param FS_DR_ENABLE")
V("Mode change to %s failed: %s", "Не удалось включить режим",
  "Copter::mode_change_failed(). Причины в коде: «requires position» (нет GPS), «need alt estimate», «throttle too high», «init failed» (режим не инициализировался), «in fence recovery», «runup not complete» (вертолёт), «GCS entry disabled (FLTMODE_GCSBLOCK)».",
  ["Читай причину после «failed:» и устрани её; для «requires position» — жди GPS или используй AltHold/Stabilize."], [], ["modes"], code="ArduCopter/mode.cpp, set_mode()")
V("Auto: Missing Takeoff Cmd", "Auto на земле без команды взлёта", "Armed, на земле, а миссия не начинается с TAKEOFF.", ["Добавь TAKEOFF первой командой миссии."], [], ["mission"], code="ArduCopter/mode_auto.cpp, init()")
V(["Mode change to AUTO RTL failed: No landing sequence found", "Mode change to AUTO RTL failed: No return path found", "Mode change to AUTO RTL failed: No return path or landing sequence found"],
  "AUTO RTL невозможен", "В миссии нет DO_LAND_START / посадочной последовательности или к ней нет пути.", ["Добавь DO_LAND_START и посадку в миссию."], [], ["mission"], code="ArduCopter/mode_auto.cpp")
V("Skipping invalid cmd #%i", "Команда миссии не поддерживается", "Команда N не может быть выполнена Copter — пропущена.", ["Проверь миссию: команды для Plane/Rover Copter не выполняет."], [], ["mission"], code="ArduCopter/mode_auto.cpp")
V(["Auto mission changed, restarted command", "Auto mission changed but failed to restart command"], "Миссия изменена в полёте", "Миссию перезаписали во время Auto; текущая команда перезапущена (или не удалось).", ["Проверь, что загружена нужная миссия."], [], ["mission"], code="ArduCopter/mode_auto.cpp")
V("%s Reached maximum descent", "Достигнут лимит снижения (PayloadPlace)", "В payload place снижение превысило заданный максимум без касания.", ["Проверь высоту, заданную в команде, и PLDP_*."], [], [], code="ArduCopter/mode_auto.cpp, payload_place")
V("%s PLDP_RNG_MAX set and rangefinder not enabled", "PayloadPlace требует дальномер", "PLDP_RNG_MAX задан, но rangefinder не включён.", ["Включи дальномер или PLDP_RNG_MAX=0."], ["PLDP_RNG_MAX", "RNGFND1_TYPE"], ["rngf"], code="ArduCopter/mode_auto.cpp")
V(["Land: no terrain data, using alt-above-home", "PayloadPlace: no terrain data, using alt-above-home", "RTL: no terrain data, using alt-above-home", "RTL: rangefinder unhealthy, using alt-above-home"],
  "Высота над рельефом недоступна — используется высота над Home", "Режим хотел высоту над рельефом/дальномером, данных нет — переключается на высоту над Home.", ["Проверь terrain/rangefinder до полёта."], ["RTL_ALT_TYPE", "TERRAIN_ENABLE"], ["terrain"],
  code="ArduCopter/mode_auto.cpp, mode_rtl.cpp")
V(["SurfaceTracking: no downward rangefinder", "SurfaceTracking: no upward rangefinder"], "Нет дальномера для слежения за поверхностью", "Нет дальномера с ориентацией вниз (PITCH_270) / вверх (PITCH_90).",
  ["Задай RNGFND1_ORIENT=25 (вниз) для слежения за землёй."], ["RNGFND1_ORIENT"], ["rngf"], code="ArduCopter/surface_tracking.cpp")
V(["Takeoff blocked: waiting for ESC RPM", "Takeoff blocked: ESC RPM out of range"], "Взлёт заблокирован: обороты ESC", "Включена проверка оборотов перед взлётом (TKOFF_RPM_MIN/MAX): нет телеметрии оборотов или обороты вне диапазона.",
  ["Проверь телеметрию ESC (BDShot / провод телеметрии).", "Если проверка не нужна — TKOFF_RPM_MIN=0."], ["TKOFF_RPM_MIN", "TKOFF_RPM_MAX"], ["motors"], code="ArduCopter/takeoff_check.cpp")
V(["Parachute: Too low", "Parachute: Landed"], "Парашют не выпущен", "Too low — высота ниже CHUTE_ALT_MIN; Landed — коптер на земле.", ["Проверь CHUTE_ALT_MIN."], ["CHUTE_ALT_MIN"], [], code="ArduCopter/crash_check.cpp, parachute_check")
V("Set FOLL_ENABLE = 1", "Follow отключён", "Режим Follow требует FOLL_ENABLE=1.", ["FOLL_ENABLE=1, перезагрузка, настрой FOLL_SYSID."], ["FOLL_ENABLE"], [], code="ArduCopter/mode_follow.cpp")
V("Turtle: raise throttle to arm", "Turtle: подними газ", "Режим Turtle армится, когда газ поднят.", ["Подними газ."], [], [], code="ArduCopter/mode_turtle.cpp")

# ============================ EKF (в полёте / старт)
V(["EKF3 not enough memory", "NavEKF2: not enough memory available", "EKF3 allocation failed", "NavEKF2: memory allocation failed"], "EKF не хватило памяти",
  "Свободной памяти меньше, чем нужно на ядра EKF (+4096 байт).", ["EK2_ENABLE=0 (EKF2 обычно не нужен).", "Уменьши число ядер (EK3_IMU_MASK).", "SCR_ENABLE=0 или уменьши SCR_HEAP_SIZE."],
  ["EK2_ENABLE", "EK3_IMU_MASK", "SCR_HEAP_SIZE"], ["ekf"], code="libraries/AP_NavEKF3/AP_NavEKF3.cpp, InitialiseFilter()")
V(["EKF3 IMU%u GSF: not enough memory", "EKF3 IMU%uGSF: allocation failed", "EKF2 IMU%u GSF: not enough memory", "EKF2 IMU%uGSF: allocation failed"], "Не хватило памяти на GSF-оценщик курса",
  "Оценщик курса EKF-GSF (аварийный сброс курса) не создан из-за памяти.", ["Освободи память (см. выше)."], ["EK2_ENABLE"], ["ekf"], code="libraries/AP_NavEKF3/AP_NavEKF3_core.cpp")
V("EKF3 waiting for GPS config data", "EKF3 ждёт параметры GPS", "EKF3 ждёт от GPS данных о задержке/конфигурации, чтобы начать использовать его.", ["Подожди; если долго — проверь GPS1_TYPE и соединение."], ["GPS1_TYPE"], ["gps"],
  code="libraries/AP_NavEKF3/AP_NavEKF3_core.cpp")
V(["EKF3 IMU%u emergency yaw reset", "EKF2 IMU%u emergency yaw reset"], "Аварийный сброс курса EKF",
  "Инновации компаса долго большие — EKF сбросил курс по оценщику GSF (по GPS-скорости). Классическая причина — помехи компасу от тока моторов или неправильная ориентация компаса.",
  ["Проверь COMPASS_ORIENT и калибровку.", "Проверь влияние тока на компас (CompassMot, MAG vs BAT.Curr в логе).", "Убери компас от силовых проводов."], ["COMPASS_ORIENT", "EK3_MAG_CAL"], ["compcal", "compassmot"],
  code="libraries/AP_NavEKF3/AP_NavEKF3_MagFusion.cpp")
V(["EKF3 IMU%u MAG%u ground mag anomaly, yaw re-aligned", "EKF2 IMU%u MAG%u ground mag anomaly, yaw re-aligned"], "Магнитная аномалия у земли — курс выровнен",
  "После взлёта курс пересчитан: у земли поле было искажено (металл, арматура).", ["Не взлетай с металлических поверхностей/машин."], [], ["compcal"], code="libraries/AP_NavEKF3/AP_NavEKF3_MagFusion.cpp")
V(["EKF3 IMU%u forced reset", "EKF2 IMU%u forced reset"], "EKF перезапущен на земле", "Фильтр был нездоров > 5 с на земле (disarmed) — принудительный сброс.", ["Подожди; если повторяется — смотри IMU/вибрации."], [], ["ekf"],
  code="libraries/AP_NavEKF3/AP_NavEKF3_core.cpp")
V(["EKF3 IMU%u stopped aiding", "EKF2 IMU%u has stopped aiding"], "EKF перестал использовать внешние данные", "Нет источников позиции/скорости (GPS, flow) — режим AID_NONE.",
  ["В полёте — переходи в AltHold/Stabilize.", "Проверь GPS и источники EK3_SRC*."], ["EK3_SRC1_POSXY"], ["ekf"], code="libraries/AP_NavEKF3/AP_NavEKF3_Control.cpp")
V("EKF3 lane switch %u", "EKF сменил основное ядро", "Условие: есть запасное ядро и у основного ошибка > 1, или оно нездорово, или другое ядро лучше.",
  ["Разовое — не страшно. Частое — проверь вибрации, компас, IMU."], ["EK3_IMU_MASK"], ["ekf"], code="libraries/AP_NavEKF3/AP_NavEKF3.cpp, UpdateFilter()")
V(["EKF3: origin already set", "EKF2 refusing set origin"], "Origin EKF уже задан", "Повторная установка origin отклонена.", ["Ничего; origin сбрасывается только перезагрузкой."], [], [], code="libraries/AP_NavEKF3/AP_NavEKF3.cpp")

# ============================ Компас (калибровка)
V("Mag(%u) bad orientation: %u/%u %.1f", "Калибровка: ориентация внешнего компаса неверна",
  "При калибровке проверка ориентации не прошла: первое число — текущая ориентация (COMPASS_ORIENTn), второе — подобранная лучшая.", ["Поставь COMPASS_ORIENTn = второе число из сообщения или включи COMPASS_AUTO_ROT=2 и перекалибруй."],
  ["COMPASS_ORIENT", "COMPASS_AUTO_ROT"], ["compcal"], code="libraries/AP_Compass/CompassCalibrator.cpp, fix_radius/orientation check")
V("Mag(%u) internal bad orientation: %u %.1f", "Калибровка: ориентация внутреннего компаса неверна", "Для внутреннего компаса подобранная ориентация не совпадает с ожидаемой — обычно неверный AHRS_ORIENTATION платы или компас в помехах.",
  ["Проверь AHRS_ORIENTATION.", "Если внутренний компас в помехах — отключи его."], ["AHRS_ORIENTATION", "COMPASS_USE"], ["compcal"], code="libraries/AP_Compass/CompassCalibrator.cpp")
V("Mag(%u) bad radius %.0f expected %.0f", "Калибровка: модуль поля сильно отличается от ожидаемого", "Масштаб коррекции вне допустимых границ (COMPASS_MIN/MAX_SCALE_FACTOR) — поле искажено или компас неисправен.",
  ["Перекалибруй вдали от металла и машин.", "Проверь, что координаты есть (для ожидаемого поля нужен GPS)."], ["COMPASS_CAL_FIT"], ["compcal"], code="libraries/AP_Compass/CompassCalibrator.cpp, fix_radius()")
V(["Compass cal requires GPS lock", "Mag: no position available"], "Для калибровки нужен GPS", "Калибровке (ожидаемое поле/fixed yaw) нужен GPS-фикс.", [SKY], [], ["compcal"], code="libraries/AP_Compass/AP_Compass_Calibration.cpp")
V(["Mag[%u]: unhealthy ", "Mag[%u]: bad uncorrected field"], "Калибровка по известному курсу: компас нездоров", "Компас N нездоров или нет сырых данных.", ["Проверь подключение компаса."], [], ["compcal"], code="libraries/AP_Compass/AP_Compass_Calibration.cpp")
V(["Mag: Compass #%d with DEVID %lu removed", "Mag: Compass #%d with DEVID %lu replaced"], "Набор компасов изменился", "Ранее сохранённый компас пропал/заменён другим устройством.", ["Откалибруй компасы заново, проверь приоритеты."], ["COMPASS_PRIO1_ID"], ["compcal"],
  code="libraries/AP_Compass/AP_Compass.cpp")

# ============================ Прочее Copter-релевантное
V("Internal Errors 0x%x", "Появились внутренние ошибки", "Маска внутренних ошибок изменилась.", ["Расшифруй маску на вкладке «Коды лога»."], [], ["logs"], code="libraries/AP_Vehicle/AP_Vehicle.cpp")
V("Config Error: fix problem then reboot", "Ошибка конфигурации платы", "AP_BoardConfig в состоянии config error — выше в сообщениях есть точная причина (например неверный параметр или отсутствующий датчик).", ["Найди сообщение перед этим, исправь, перезагрузи."], [], [],
  code="libraries/AP_Vehicle/AP_Vehicle.cpp")
V("Noise %.fdB on motor %u at %.fHz", "Сильный шум на моторе", "Анализ гироскопа нашёл пик > 40 дБ, связанный с мотором N, на частоте F.", ["Проверь мотор N (подшипники, балансировка, проп).", "Настрой Harmonic Notch на эту частоту."], ["INS_HNTCH_ENABLE", "INS_HNTCH_FREQ"], ["vibe"],
  code="libraries/AP_Vehicle/AP_Vehicle.cpp")
V("ESC calibration: Restart board", "Газ был поднят при включении — автопилот ждёт перезагрузки",
  "ArduCopter/esc_calibration.cpp: при ESC_CALIBRATION=0 и газе выше порога на старте прошивка сама ставит ESC_CALIBRATION=1 («калибровка при высоком газе на следующем старте») и блокируется в бесконечном цикле до перезагрузки. Частая ловушка: включил коптер с поднятым стиком газа.",
  ["Если калибровка ESC не нужна: опусти газ, перезагрузи, затем проверь, что ESC_CALIBRATION=0 (иначе при следующем старте с высоким газом начнётся калибровка).", "Если нужна калибровка — сними пропеллеры, перезагрузи с газом вверху и следуй сообщениям.", "Для DShot калибровка не нужна."],
  ["ESC_CALIBRATION"], ["motors"], code="ArduCopter/esc_calibration.cpp, esc_calibration_startup_check()")
V(["ESC calibration: Passing pilot throttle to ESCs", "ESC calibration: Auto calibration", "ESC calibration: Push safety switch", "Reboot rejected, ESC cal on reboot"],
  "Калибровка ESC", "ESC_CALIBRATION: 0 обычный старт, 1 калибровка, если газ высокий на старте, 2 калибровка всегда, 3 автоматическая калибровка, 9 проверка отключена. «Passing pilot throttle» — газ со стика идёт прямо на ESC; «Push safety switch» — нажми safety; «Reboot rejected» — перезагрузка по команде запрещена, пока стоит автокалибровка.",
  ["Сними пропеллеры!", "Для PWM-ESC: ESC_CALIBRATION=3, перезагрузи, следуй сообщениям.", "Для DShot калибровка не нужна."], ["ESC_CALIBRATION"], ["motors"], code="ArduCopter/esc_calibration.cpp; значения @Param ESC_CALIBRATION")
V(["%s: Board initialising", "%s: RC not calibrated", "%s: vehicle not landed", "%s: Safety switch", "%s: Motor Emergency Stopped"], "Мотор-тест / CompassMot не может стартовать",
  "Проверки перед тестом моторов: плата инициализирована, RC откалиброван, коптер на земле, safety switch нажат, нет E-Stop.", ["Выполни условие из текста.", "Пропеллеры сними!"], [], ["mdisc"], code="ArduCopter/motor_test.cpp, mavlink_motor_control_check()")
CMOT = "ArduCopter/compassmot.cpp, mavlink_compassmot()"
V("Compass disabled", "CompassMot: нет ни одного компаса", "Калибровка влияния моторов на компас (CompassMot) запущена, но в системе нет доступного компаса (compass.available() = false): компасы выключены или не найдены.",
  ["Включи компас: COMPASS_ENABLE=1, COMPASS_USE=1.", "Проверь, что компас обнаружен (Setup → Compass), перезагрузи."], ["COMPASS_ENABLE", "COMPASS_USE"], ["compassmot"], code=CMOT)
V("Check compass", "CompassMot: компас нездоров", "Один из компасов не отдаёт данные (compass.healthy() = false) — CompassMot не запускается.",
  ["Проверь подключение внешнего компаса (I2C/CAN, питание GPS-модуля).", "Перезагрузи и убедись, что нет «PreArm: Compass not healthy»."], ["COMPASS_USE"], ["compassmot"], code=CMOT)
V("RC not calibrated", "CompassMot: пульт не откалиброван", "Перед CompassMot проверяется калибровка пульта (те же проверки, что «radio min too high / max too low»): газом нужно будет управлять вручную.",
  ["Сделай Radio Calibration в Mission Planner."], ["RC3_MIN", "RC3_MAX"], ["compassmot", "rc"], code=CMOT)
V("Throttle not zero", "CompassMot: газ не на нуле", "Запуск CompassMot разрешён только при газе в нуле.",
  ["Опусти стик газа полностью и запусти снова."], ["RC3_MIN"], ["compassmot"], code=CMOT)
V("Not landed", "CompassMot: коптер не на земле", "Copter считает, что он не приземлён (land_complete = false) — CompassMot выполняется только на земле.",
  ["Поставь коптер на землю, disarm, подожди пару секунд и запусти снова."], [], ["compassmot"], code=CMOT)
V(["SmartRTL deactivated: %s", "SmartRTL deactivated: init failed"], "SmartRTL отключён в полёте", "Причины в коде: «buffer full» (точки кончились), «bad position» (нет позиции долго), «program error», «init failed» (нет памяти).",
  ["buffer full — увеличь SRTL_POINTS (до 500).", "bad position — проблема GPS.", "init failed — освободи память."], ["SRTL_POINTS", "SRTL_ACCURACY"], ["srtl"], code="libraries/AP_SmartRTL/AP_SmartRTL.cpp")
V("SmartRTL: lost one point", "SmartRTL потерял точку", "Не удалось сохранить точку пути при входе в SmartRTL.", ["Обычно не критично."], ["SRTL_POINTS"], ["srtl"], code="ArduCopter/mode_smart_rtl.cpp")
V("Vehicle breaching %s", "Нарушение geofence", "AC_Fence: нарушены ограничения (%s — какие: Alt max, Circle, Polygon, Alt min). Действие — FENCE_ACTION (0 Report, 1 RTL или Land, 2 Always Land, 3 SmartRTL или RTL или Land, 4 Brake или Land, 5 SmartRTL или Land).",
  ["Верни коптер в зону.", "Проверь FENCE_TYPE (биты: 0 Max alt, 1 Circle, 2 Polygons, 3 Min alt), FENCE_RADIUS, FENCE_ALT_MAX."], ["FENCE_ACTION", "FENCE_TYPE", "FENCE_RADIUS", "FENCE_ALT_MAX", "FENCE_MARGIN"], ["fence"],
  code="libraries/AC_Fence/AC_Fence.cpp; значения @Param FENCE_ACTION (Copter)")
V("Fence requires position", "Fence требует позицию", "Нет позиции относительно Home — fence не может работать.", [SKY], ["FENCE_ENABLE"], ["fence"], code="libraries/AC_Fence/AC_Fence.cpp")
V("Fences enabled, but none selected", "Fence включён, но тип не выбран", "FENCE_ENABLE=1, а FENCE_TYPE не включает ни одного ограничения.", ["Задай FENCE_TYPE (например 7 = alt max + circle + polygon)."], ["FENCE_TYPE"], ["fence"], code="libraries/AC_Fence/AC_Fence.cpp")
V(["Invalid Circle FENCE_RADIUS value", "Circle FENCE_MARGIN is less than FENCE_RADIUS", "Invalid FENCE_ALT_MAX value", "Invalid FENCE_ALT_MIN value", "Invalid FENCE_MARGIN value", "FENCE_ALT_MAX < FENCE_ALT_MIN", "FENCE_MARGIN too big"],
  "Неверные параметры fence", "Проверки AC_Fence::pre_arm_check: FENCE_RADIUS < 0; радиус меньше FENCE_MARGIN; FENCE_ALT_MAX < 0; FENCE_ALT_MIN < −100; FENCE_MARGIN < 0; FENCE_ALT_MAX < FENCE_ALT_MIN; (FENCE_ALT_MAX − FENCE_ALT_MIN) ≤ 2 × FENCE_MARGIN.",
  ["Исправь указанный параметр по условию."], ["FENCE_RADIUS", "FENCE_MARGIN", "FENCE_ALT_MAX", "FENCE_ALT_MIN"], ["fence"], code="libraries/AC_Fence/AC_Fence.cpp, pre_arm_check()")
V(["Polygon fence(s) invalid", "Polygon fence margin is less than inclusion circle radius"], "Полигональный fence некорректен", "Полигоны не загрузились или margin больше inclusion-окружности.", ["Перезагрузи fence из GCS (Plan → GeoFence)."], ["FENCE_MARGIN"], ["fence"],
  code="libraries/AC_Fence/AC_Fence.cpp")
V("FENCE_AUTOENABLE is %u, will be removed in 4.7, use 3", "Устаревшее значение FENCE_AUTOENABLE", "Значение будет удалено в 4.7.", ["Поставь FENCE_AUTOENABLE=3 или 0."], ["FENCE_AUTOENABLE"], ["fence"], code="libraries/AC_Fence/AC_Fence.cpp")
V("Fence breach cleared", "Нарушение fence снято", "Коптер вернулся в разрешённую зону.", ["Ничего."], [], ["fence"], code="ArduCopter/fence.cpp")
V(["PRX%d: No Data", "PRX%d: Not Connected"], "Proximity-датчик не отвечает", "Статус датчика препятствий NoData/NotConnected.", ["Проверь PRX1_TYPE, порт, питание."], ["PRX1_TYPE"], ["oa"], code="libraries/AP_Proximity/AP_Proximity.cpp")
V(["PrecLand: Target Lost", "PrecLand: Init Failed"], "Precision Landing: нет цели", "Target Lost — цель перестала быть видна; Init Failed — нет данных от датчика достаточно долго.",
  ["Проверь датчик (IR-Lock/камера), PLND_TYPE, освещение."], ["PLND_ENABLED", "PLND_TYPE"], ["prec"], code="libraries/AC_PrecLand/AC_PrecLand.cpp")
V(["AutoTune: Failed", "AutoTune: Aborting Test", "AutoTune: Angle P Gain Determination Failed", "AutoTune: Rate P Gain Determination Failed", "AutoTune: Rate D Gain Determination Failed",
   "AutoTune: Twitch Size Determination Failed", "AutoTune: Min Rate D limit reached", "AutoTune: Failed to level, please tune manually"], "AutoTune не удался",
  "AC_AutoTune: Angle/Rate P — коэффициент упёрся в минимум; Rate D — не удалось определить D; Twitch Size — шаг теста стал слишком мал (step_scaler ≤ 0.2); Min Rate D — D упёрся в минимум; Failed to level — коптер не выровнялся за 3 × AUTOTUNE_LEVEL_TIMEOUT; Aborting — тест прерван (обычно вмешательство пилота/наклон).",
  ["Тюнь в безветрие, на высоте и с запасом места.", "Сначала убери вибрации и настрой Harmonic Notch.", "Задай стартовые параметры по размеру пропов (Mission Planner → Initial Tune Parameters).", "Уменьши AUTOTUNE_AGGR (0.05–0.075), тюнь оси по одной (AUTOTUNE_AXES)."],
  ["AUTOTUNE_AGGR", "AUTOTUNE_AXES", "INS_HNTCH_ENABLE"], ["autotune", "vibe"], code="libraries/AC_AutoTune/AC_AutoTune.cpp, AC_AutoTune_Multi.cpp")
V(["PreArm: VisOdom: not healthy", "PreArm: VisOdom: check VISO_ORIENT parameter", "PreArm: VisOdom: roll/pitch diff %4.1f deg (>10)", "PreArm: VisOdom: yaw diff %4.1f deg (>10)", "PreArm: VisOdom: waiting for AHRS attitude", "PreArm: VisOdom: out of memory"],
  "Visual odometry не готова", "Камера VIO нездорова, или её ориентация отличается от AHRS > 10° по крену/тангажу или курсу (Intel T265).", ["Проверь VISO_TYPE, VISO_ORIENT, крепление камеры, связь с компаньоном."], ["VISO_TYPE", "VISO_ORIENT"], ["ekf3src"],
  code="libraries/AP_VisualOdom/AP_VisualOdom_IntelT265.cpp")
V(["PreArm: DroneCAN: Node %d unhealthy!", "PreArm: DroneCAN: Duplicate Node %s../%d!"], "DroneCAN-узел нездоров / дубль ID", "Узел сообщает статус unhealthy или два устройства с одним node ID.",
  ["Подключи DroneCAN GUI Tool / Mission Planner → DroneCAN, посмотри статус узла.", "Задай устройствам разные node ID; проверь терминаторы 120 Ом и питание шины."], ["CAN_P1_DRIVER", "CAN_D1_PROTOCOL"], ["dronecan"], code="libraries/AP_DroneCAN/AP_DroneCAN_DNA_Server.cpp")

# ============================ информационные (не ошибки)
for k in ["EKF3 IMU%u is using GPS", "EKF3 IMU%u origin set", "EKF3 IMU%u tilt alignment complete", "EKF3 IMU%u yaw aligned", "EKF3 IMU%u yaw aligned to GPS velocity", "EKF3 IMU%u yaw aligned using GPS",
          "EKF3 IMU%u is using external nav data", "EKF3 IMU%u is using range beacons", "EKF3 IMU%u fusing optical flow"]:
    V(k, "Нормальное сообщение EKF при старте", "Информационное: ядро EKF прошло этап (выравнивание наклона, курса, начало использования GPS/flow, установка origin). Это не ошибка.",
      ["Ничего делать не нужно. Если какого-то этапа нет — именно он мешает (например нет «is using GPS» → смотри GPS-сообщения)."], [], ["ekf"], code="libraries/AP_NavEKF3/AP_NavEKF3_Control.cpp / _MagFusion.cpp")


import kb_verified2  # noqa: E402,F401  (часть 2 — регистрирует записи через V)
import kb_verified3  # noqa: E402,F401

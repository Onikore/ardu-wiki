# -*- coding: utf-8 -*-
"""Правила, написанные строго по коду Copter-4.6.3 (пороги и условия процитированы из исходников).
Подключаются из kb.py. Каждое правило содержит поле src — откуда взято объяснение."""
from kb import RULES

EKF_GPS_SRC = "libraries/AP_NavEKF3/AP_NavEKF3_VehicleStatus.cpp, calcGpsGoodToAlign()"
SCALE = ("Порог умножается на EK3_CHECK_SCALE/100 (по умолчанию 100 → ×1). После того как проверка один раз прошла, порог временно "
         "увеличивается ×1.3 (гистерезис), поэтому сообщение может то появляться, то пропадать.")
GPSFIX = ["Подожди 2–5 минут под открытым небом, не двигая коптер.", "Убери GPS подальше от видеопередатчика, камеры, USB3, ESC и силовых проводов; поставь на мачту.",
          "Проверь, что включены все созвездия (GPS_GNSS_MODE = 0 — по умолчанию модуля).",
          "Только если причина понятна и полёт безопасен: увеличить EK3_CHECK_SCALE (например 150) или снять нужный бит в EK3_GPS_CHECK."]


def C(rx, t, c, f, p, d, src, causes=(), diag=(), more=(), ignore=""):
    RULES.insert(0, dict(rx=rx, t=t, c=c, f=list(f), p=list(p), d=list(d), src=src,
                         deep=dict(causes=list(causes), diag=list(diag), steps=list(f), more=list(more), ignore=ignore)))


C(r"GPS numsats", "EKF3: мало спутников для старта навигации",
  "EKF3 не начинает использовать GPS, пока число спутников < 6 (жёстко в коде: gps.num_sats() < 6). Проверка включена битом 0 (NSats) в EK3_GPS_CHECK.",
  GPSFIX, ["EK3_GPS_CHECK", "GPS_GNSS_MODE"], ["gps", "ekf"], EKF_GPS_SRC,
  causes=["Закрытое небо, помещение, рядом здания.", "Холодный старт приёмника.", "Помехи от электроники на борту."],
  diag=["Mission Planner HUD: «Sats». В логе GPS.NSats.", "Сравни NSats с выключенными и включёнными моторами/видео — если падает, это помехи."],
  ignore="Бит 0 в EK3_GPS_CHECK можно снять, но тогда EKF примет GPS с плохой геометрией. Не рекомендуется.")
C(r"GPS HDOP .* \(needs 2\.5\)", "EKF3: HDOP хуже 2.5",
  "EKF3 требует HDOP ≤ 2.5 (в коде: gps.get_hdop() > 250, HDOP хранится ×100). Это отдельная проверка от GPS_HDOP_GOOD. Бит 1 (HDoP) в EK3_GPS_CHECK.",
  GPSFIX, ["EK3_GPS_CHECK", "GPS_HDOP_GOOD"], ["gps", "ekf"], EKF_GPS_SRC,
  causes=["Мало спутников / плохая геометрия.", "Помехи."], diag=["Лог GPS.HDop (в логе — уже в нормальных единицах)."])
C(r"GPS horiz error", "EKF3: горизонтальная ошибка GPS слишком большая",
  "Приёмник сам сообщает оценку точности hAcc. EKF3 не стартует, если hAcc > 5 м × EK3_CHECK_SCALE/100. " + SCALE,
  GPSFIX, ["EK3_CHECK_SCALE", "EK3_GPS_CHECK"], ["gps", "ekf"], EKF_GPS_SRC,
  causes=["Приёмник ещё не сошёлся.", "Плохой сигнал / помехи / отражения."], diag=["Лог GPS.HAcc (или GPA.HAcc)."])
C(r"GPS vert error", "EKF3: вертикальная ошибка GPS слишком большая",
  "vAcc от приёмника > 7.5 м × EK3_CHECK_SCALE/100. " + SCALE, GPSFIX, ["EK3_CHECK_SCALE", "EK3_GPS_CHECK"], ["gps", "ekf"], EKF_GPS_SRC,
  diag=["Лог GPA.VAcc."])
C(r"GPS speed error", "EKF3: ошибка скорости GPS слишком большая",
  "Точность скорости от приёмника (sAcc) > 1.0 м/с × EK3_CHECK_SCALE/100. Бит 2 (speed error) в EK3_GPS_CHECK. " + SCALE,
  GPSFIX, ["EK3_CHECK_SCALE", "EK3_GPS_CHECK"], ["gps", "ekf"], EKF_GPS_SRC, diag=["Лог GPA.SAcc."])
C(r"GPS drift", "EKF3: позиция GPS «плывёт» на земле",
  "На земле EKF3 суммирует смещение позиции GPS (с затуханием 10 с). Если накопленный дрейф > 3 м × EK3_CHECK_SCALE/100 — отказ. Проверка работает только если включён бит 5 (pos drift) в EK3_GPS_CHECK; по умолчанию EK3_GPS_CHECK=31 и этот бит выключен.",
  GPSFIX + ["Если коптер стоит на движущейся платформе (лодка, машина) — сними бит 5 в EK3_GPS_CHECK."], ["EK3_GPS_CHECK", "EK3_CHECK_SCALE"], ["gps", "ekf"], EKF_GPS_SRC)
C(r"GPS (vertical|horizontal) speed", "EKF3: GPS показывает движение на земле",
  "На земле отфильтрованная скорость GPS по вертикали или горизонтали > 0.3 м/с × EK3_CHECK_SCALE/100. Биты 6 (vert speed) и 7 (horiz speed) EK3_GPS_CHECK, по умолчанию выключены.",
  GPSFIX + ["Если стартуешь с движущейся платформы — сними биты 6/7 в EK3_GPS_CHECK."], ["EK3_GPS_CHECK", "EK3_CHECK_SCALE"], ["gps", "ekf"], EKF_GPS_SRC)
C(r"Mag yaw error", "EKF3: курс по компасу не сходится",
  "Тест-отношения магнитометра magTestRatio.x/y или yawTestRatio > 1 — показания компаса противоречат модели EKF. Бит 4 (yaw error) в EK3_GPS_CHECK. Если ошибка держится > 5 с на земле, EKF сам запрашивает сброс курса.",
  ["Откалибруй компас вдали от металла и проводов.", "Проверь COMPASS_ORIENT внешнего компаса (стрелка = нос).", "Убери коптер с металлической поверхности / из машины.", "Если внутренний компас мешает — COMPASS_USE2=0 / COMPASS_USE3=0."],
  ["COMPASS_ORIENT", "COMPASS_USE2", "EK3_GPS_CHECK"], ["compcal", "ekf"], EKF_GPS_SRC,
  diag=["Лог XKF3.IMX/IMY/IMZ (инновации магнитометра) и XKF4.SM.", "Сравни MAG.MagX/Y/Z с выключенными/включёнными моторами."])
C(r"EKF starting GPS checks", "EKF3: проверки GPS только начались",
  "Служебное состояние: EKF3 начал проверять качество GPS. Обычно через секунды сменится другим сообщением или пропадёт.", ["Подожди."], [], ["ekf"], EKF_GPS_SRC)
C(r"EKF[23] core %d unhealthy|EKF[23] core \d+ unhealthy", "EKF: ядро (core) нездорово",
  "Ядро EKF считается нездоровым (NavEKF3_core::healthy() в AP_NavEKF3_Outputs.cpp), если: (1) есть внутренние ошибки фильтра (faults: NaN, плохая ковариация); (2) одновременно velTestRatio > 1, posTestRatio > 1 и hgtTestRatio > 1 — скорость, позиция и высота все не сходятся; (3) прошло меньше 1 с после старта EKF; (4) на земле без GPS (режим без внешней позиции) горизонтальная инновация позиции > 1 м или высоты > 1 м — то есть коптер двигали или баро «уплыл».",
  ["Если только что включил — подожди несколько секунд.", "Не двигай коптер на земле до arm, если GPS ещё нет.", "Проверь вибрации (VIBE, Clip) и барометр (закрой поролоном).",
   "Посмотри, какой IMU у этого ядра (EK3_IMU_MASK) — если ядро всегда одно и то же, проблема в этом IMU: отключи его INS_USE2/3=0.", "Перезагрузи автопилот."],
  ["EK3_IMU_MASK", "INS_USE2", "INS_USE3"], ["ekf", "vibe"], "libraries/AP_NavEKF3/AP_NavEKF3_Outputs.cpp, NavEKF3_core::healthy()",
  causes=["Сразу после включения (первая секунда).", "Коптер двигали/несли без GPS.", "Сильные вибрации или неисправный IMU одного ядра.", "Ошибка фильтра (NaN) — смотри Internal Errors."],
  diag=["Лог XKF4.SV/SP/SH (test ratio) для каждого ядра (C=0/1/2): у какого ядра > 1.", "XKF4.FS — faults bitmask, если ≠ 0 — внутренняя ошибка фильтра.", "VIBE.Clip*, IMU/IMU2."],
  more=["Если не уходит после перезагрузки неподвижно на столе — возможен аппаратный дефект IMU."], ignore="Нет: нездоровое ядро — неверная навигация.")
C(r"no EKF3 cores", "EKF3 не создал ни одного ядра",
  "NavEKF3 не смог создать ядра: нехватка памяти или EK3_IMU_MASK не выбирает ни одного IMU.", ["Проверь EK3_ENABLE=1 и EK3_IMU_MASK (≥1).", "Освободи память: EK2_ENABLE=0, отключи Scripting.", "Перезагрузи."],
  ["EK3_ENABLE", "EK3_IMU_MASK", "EK2_ENABLE"], ["ekf"], "libraries/AP_NavEKF3/AP_NavEKF3.cpp, pre_arm_check()")
C(r"PreArm: (Throttle|Collective|X|%s) too high", "Газ не на минимуме при arm",
  "ArduCopter/AP_Arming.cpp, arm_checks(): два условия. (1) В любом режиме: стик газа выше верхней границы мёртвой зоны центра, т.е. get_pilot_desired_climb_rate() > 0 — пилот «просит» набор высоты. (2) В режимах с ручным газом (Stabilize, Acro, Drift): газ должен быть ровно 0. Проверка пропускается при arm из GCS/скрипта в Guided/Auto. Относится к биту «RC Channels» в ARMING_CHECK.",
  ["Опусти стик газа полностью вниз.", "Проверь Radio Calibration: RC3 при минимуме стика должен совпадать с RC3_MIN.", "Если газ «пружинный» (центровка) — для AltHold/Loiter газ должен быть в центре/ниже, для Stabilize — внизу."],
  ["RC3_MIN", "RC3_TRIM"], ["rc"], "ArduCopter/AP_Arming.cpp, arm_checks()")
C(r"Battery %d (below minimum arming|unhealthy|low|critical|capacity failsafe|voltage failsafe)", "Батарея не прошла пре-арм",
  "AP_BattMonitor_Backend::arming_checks(): «unhealthy» — монитор не здоров; «below minimum arming voltage/capacity» — ниже BATT_ARM_VOLT / BATT_ARM_MAH; «low/critical voltage/capacity failsafe» — уже ниже порогов BATT_LOW_*/BATT_CRT_*; «critical >= low» — порог critical не ниже low (перепутаны).",
  ["Зарядить/поменять батарею.", "Сверь напряжение мультиметром и откалибруй BATT_VOLT_MULT (Setup → Optional Hardware → Battery Monitor).",
   "Проверь пороги: BATT_CRT_VOLT < BATT_LOW_VOLT, BATT_CRT_MAH < BATT_LOW_MAH; ориентир для LiPo ~3.5 В/ячейка low, ~3.4 В/ячейка critical.",
   "«unhealthy»: проверь BATT_MONITOR и кабель power module."],
  ["BATT_MONITOR", "BATT_ARM_VOLT", "BATT_ARM_MAH", "BATT_LOW_VOLT", "BATT_CRT_VOLT", "BATT_VOLT_MULT"], ["batt", "fsbatt"],
  "libraries/AP_BattMonitor/AP_BattMonitor_Backend.cpp, arming_checks()")
C(r"^Dead Reckoning (started|stopped|timeout)", "Dead reckoning: EKF летит без внешней позиции",
  "ArduCopter/events.cpp, failsafe_deadreckon_check(): «started» — EKF перешёл в dead reckoning (потерял GPS/внешнюю позицию, оценивает по инерциалке/ветру); «stopped» — позиция вернулась; «timeout» — dead reckoning длится дольше FS_DR_TIMEOUT, после чего срабатывает действие FS_DR_ENABLE.",
  ["Сразу бери управление в AltHold/Stabilize или жди действия failsafe.", "После посадки смотри лог: GPS.Status/NSats в момент начала, XKF4.", "Настрой FS_DR_ENABLE и FS_DR_TIMEOUT."],
  ["FS_DR_ENABLE", "FS_DR_TIMEOUT"], ["fsekf", "gps"], "ArduCopter/events.cpp, failsafe_deadreckon_check()")

C(r"AutoTune: (Failed|Aborting Test|.*Determination Failed|Failed to level|Exceeded frequency range|Step time limit exceeded|Min Rate D limit reached)",
  "AutoTune не удался / прерван",
  "AC_AutoTune: тест «твитча» по оси не дал устойчивого результата (не удалось определить усиление, превышен лимит времени шага, D достиг минимума) либо коптер не смог выровняться перед тестом (Failed to level).",
  ["Лети только в безветрие и на высоте ≥ 10–15 м с запасом места.", "Сначала убери вибрации и настрой Harmonic Notch (INS_HNTCH_*): шум на гироскопе — частая причина провала.",
   "Задай разумные стартовые ATC_RAT_* (или Initial Tune Parameters в Mission Planner по размеру пропов), INS_GYRO_FILTER по размеру коптера.",
   "Уменьши AUTOTUNE_AGGR до 0.05–0.075 и тюнь оси по одной (AUTOTUNE_AXES = 1 roll, 2 pitch, 4 yaw).", "«Failed to level, please tune manually»: коптер не держит горизонт — подбери ATC_ANG_*_P/ATC_RAT_* вручную, проверь центр тяжести."],
  ["AUTOTUNE_AGGR", "AUTOTUNE_AXES", "INS_HNTCH_ENABLE", "INS_GYRO_FILTER"], ["autotune", "vibe"], "libraries/AC_AutoTune/AC_AutoTune*.cpp",
  diag=["Лог ATUN/ATDE — фазы и результаты по осям.", "VIBE и FFT гироскопа (INS_LOG_BAT_MASK) до тюнинга."])

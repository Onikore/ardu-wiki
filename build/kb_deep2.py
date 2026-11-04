# -*- coding: utf-8 -*-
"""Углублённые разборы, часть 2 (подмешиваются к DEEP в build.py)."""

DEEP2 = {
"Ошибки калибровки компаса": dict(
  causes=["Нет GPS-фикса: автокалибровка и WMM требуют позицию.", "Компас нездоров (обрыв I2C).", "Не хватает памяти/потока (редко)."],
  diag=["Messages: «Mag[n]: unhealthy», «Compass cal requires GPS lock»."],
  steps=["Подожди GPS fix 3D и повтори калибровку.", "Проверь соединение внешнего компаса и питание GPS-модуля.", "Калибруй вдали от металла: поворачивай по всем осям (по очереди нос/хвост/бока/верх/низ вниз)."],
  more=["COMPASS_AUTO_ROT=2 чтобы прошивка сама определила ориентацию."], ignore="Нет."),
"Калибровка компаса: неверная ориентация": dict(
  causes=["COMPASS_ORIENT не соответствует реальному повороту модуля.", "Модуль смонтирован под углом, не кратным 45°."],
  diag=["Messages: «Mag(n) bad orientation: A/B x.x» — A текущая, B подобранная ориентация."],
  steps=["Поставь COMPASS_ORIENT (или COMPASS_ORIENT2) по подобранной B-ориентации.", "Или проверь стрелку на модуле: она должна смотреть вперёд, если ORIENT=0.", "Повтори калибровку."],
  more=["COMPASS_AUTO_ROT=2 — автоподбор при калибровке."], ignore="Нет."),
"Калибровка компаса: неверный радиус": dict(
  causes=["Мало поворотов, не охвачены все оси.", "Магнитные помехи рядом (металл, динамики, ток)."],
  diag=["Messages: «Mag(n) bad radius R expected E»."],
  steps=["Перекалибруй на улице подальше от машин/арматуры, плавно вращая по всем осям ≥ 30 с.", "Убери магниты/металл из карманов."],
  more=["COMPASS_CAL_FIT (чем меньше, тем строже; 16 по умолчанию)."], ignore="Нет."),
"Компас откалиброван — нужна перезагрузка": dict(
  causes=["После калибровки/смены приоритета параметры применяются при загрузке."],
  steps=["Перезагрузи автопилот (отключи питание)."], more=[], ignore="Нет.", diag=["Messages: «Compass calibrated requires reboot»."]),
"Идёт калибровка компаса": dict(
  causes=["Калибровка запущена и не завершена (accept/cancel)."],
  steps=["Заверши в Mission Planner (Accept) либо нажми Cancel.", "Перезагрузись."], more=[], ignore="Нет.", diag=[]),
"Основной GPS отключён": dict(
  causes=["GPS_PRIMARY=1, а GPS_TYPE2=0 (или наоборот)."],
  steps=["GPS_PRIMARY=0 если используется только GPS 1.", "Либо задай GPS_TYPE2 для второго GPS."], more=[], ignore="Нет.", diag=["Параметры GPS_PRIMARY, GPS_TYPE, GPS_TYPE2."]),
"Blending без второго GPS": dict(
  causes=["GPS_AUTO_SWITCH=2 (blend) требует двух GPS."],
  steps=["GPS_AUTO_SWITCH=1 (use best) для одного GPS.", "Или подключи второй GPS (GPS_TYPE2)."], more=[], ignore="Нет.", diag=[]),
"Расхождение позиций GPS": dict(
  causes=["Два GPS стоят на крыше помех/в разных местах.", "Один из GPS ещё не сошёлся, потеря фикса."],
  diag=["Лог GPS и GPS2: Lat/Lng, HDop, NSats; расхождение >50 м."],
  steps=["Подожди сходимости, выйди на открытое место.", "Проверь расположение GPS и кабели.", "Отключи проблемный GPS_TYPE2=0, если он плохой."], more=[], ignore="Бит «GPS lock» — только для теста."),
"Failsafe-событие (источник в начале сообщения)": dict(
  causes=["Подсистема в начале сообщения (Radio, Battery, GCS, EKF, Fence, Terrain, …) сообщила failsafe."],
  diag=["Лог ERR: Subsys 5=радио, 6=батарея, 8=GCS, 9=fence, 16/17=EKF…; ECode 1=сработал, 0=снят.", "Смотри MSG выше — там уточнение."],
  steps=["Определи источник по тексту/логу.", "Исправь именно его (см. «Радио failsafe», «Батарея», …).", "Проверь настройки действий FS_*, BATT_FS_*."], more=[], ignore="Нет."),
"Батарея не прошла пре-арм": dict(
  causes=["below minimum arming voltage/capacity — меньше BATT_ARM_VOLT/BATT_ARM_MAH.", "unhealthy — монитор не отвечает.", "low/critical voltage failsafe — ниже BATT_LOW_VOLT/BATT_CRT_VOLT.", "failsafe critical >= low — пороги перепутаны."],
  diag=["Setup → Optional Hardware → Battery Monitor: напряжение/ток.", "Лог BAT: Volt, VoltR, Curr."],
  steps=["Зарядить батарею.", "Проверь BATT_MONITOR (4 = analog V+I, 3 = analog V) и калибровку BATT_VOLT_MULT.", "Исправь пороги: BATT_CRT_VOLT < BATT_LOW_VOLT; BATT_CRT_MAH < BATT_LOW_MAH.", "Для 'unhealthy' проверь кабель power module и BATT_VOLT_PIN/BATT_CURR_PIN."],
  more=["Не повышай BATT_ARM_VOLT выше нужного."], ignore="Бит «Battery Level» — только на стенде."),
"Недопустимый PID/PosControl параметр": dict(
  causes=["Параметр равен нулю или отрицателен (P, I, D для ATC/PSC).", "Сброс параметров/импорт некорректного файла."],
  diag=["В сообщении указан параметр: например ATC_RAT_RLL_P must be > 0."],
  steps=["Верни параметр к дефолту (Mission Planner → Full Parameter List → Reset to default)", "Дефолты Copter: ATC_RAT_RLL_P=0.135, ATC_RAT_PIT_P=0.135, ATC_RAT_YAW_P=0.18, PSC_POSZ_P=1.0, PSC_VELZ_P=5.0, PSC_ACCZ_P=0.3.", "После изменения перезагрузи и повтори arm."],
  more=[], ignore="Нет: нулевые PID дают неуправляемость."),
"EKF не стартовал (память)": dict(
  causes=["Нехватка RAM (EKF2+EKF3, много IMU, скрипты).", "AHRS_EKF_TYPE указывает на отключённый EKF."],
  steps=["AHRS_EKF_TYPE=3, EK3_ENABLE=1, EK2_ENABLE=0.", "Отключи Scripting (SCR_ENABLE=0), лишние логи.", "Замени плату на F7/H7, если RAM мало."], more=[], ignore="Нет.", diag=["Messages: «EKF3 not enough memory / allocation failed»."]),
"Мотор-тест / Compass-Mot отказ": dict(
  causes=["Safety switch не нажат.", "Пульт не откалиброван, газ не 0.", "Коптер не на земле или armed."],
  steps=["Нажми safety switch.", "Откалибруй RC.", "Disarm и повтори тест; пропеллеры снять!"], more=[], ignore="Нет.", diag=[]),
"CompassMot не стартовал": dict(
  causes=["Не откалиброван пульт, газ не 0, compass disabled."],
  steps=["Откалибруй RC, снять пропеллеры, газ вниз, компас включён.", "Mission Planner → Setup → Optional Hardware → Compass/Motor."], more=[], ignore="Нет.", diag=[]),
"GPS: конфигурация": dict(
  causes=["Сообщение показывает автодетект/настройку приёмника.", "Скорость порта не соответствует приёмнику."],
  steps=["Нормально, если сообщение INFO.", "GPS_AUTO_CONFIG=1; SERIALn_BAUD=115 (115200).", "GPS_RATE_MS=200 (5 Гц) для u-blox."], more=[], ignore="INFO-сообщения безопасны.", diag=[]),
"Ошибка полигонов Fence": dict(
  causes=["Fence-данные повреждены/неполные.", "Неверное число вершин (<3).", "Круг с радиусом ≤0."],
  steps=["Mission Planner → Plan → Geo-Fence: очисти и загрузи заново (Upload).", "Проверь FENCE_TYPE и что координаты корректны."], more=[], ignore="Нет.", diag=[]),
"Precision Landing": dict(
  causes=["PLND_ENABLED=0 или неверный PLND_TYPE.", "Цель вне поля зрения камеры/датчика."],
  steps=["PLND_ENABLED=1, PLND_TYPE по датчику (IR-LOCK/Companion).", "Проверь калибровку/освещение и положение датчика.", "PLND_LAND_OFS_X/Y, PLND_ACC_P_NSE при необходимости."], more=[], ignore="Нет.", diag=[]),
"Парашют": dict(
  causes=["CHUTE_ENABLED=1 но не назначен выход/реле.", "Высота ниже CHUTE_ALT_MIN."],
  steps=["Назначь SERVOx_FUNCTION=27 (Parachute) или реле (CHUTE_TYPE=0).", "CHUTE_ALT_MIN задай не ниже 10–30 м."], more=[], ignore="Нет.", diag=[]),
"Optical flow": dict(
  causes=["Датчик не найден (FLOW_TYPE=0).", "Не подключён/неверный порт.", "Недостаточно света/текстуры, высота."],
  steps=["FLOW_TYPE по датчику.", "FLOW_ORIENT_YAW и FLOW_POS_X/Y/Z корректно.", "Для indoor настрой EKF Source (VELXY=5 OptFlow)."], more=[], ignore="Нет.", diag=[]),
"Монитор батареи (I2C)": dict(
  causes=["Датчик INA/LTC не отвечает.", "Неверный BATT_I2C_BUS/BATT_I2C_ADDR."],
  steps=["Проверь I2C-шину и пайку.", "BATT_MONITOR по типу датчика (INA2xx=21…).", "Подключи другой датчик для проверки."], more=[], ignore="Нет.", diag=[]),
"ESC калибровка": dict(
  causes=["ESC_CALIBRATION задан, а последовательность не выполнена.", "Протокол DShot не требует калибровки."],
  steps=["Для PWM ESC: ESC_CALIBRATION=3 (авто) и перезагрузись, подай питание на ESC по инструкции GCS.", "Для DShot калибровка не нужна — MOT_PWM_TYPE=4..7.", "После завершения ESC_CALIBRATION вернётся в 0."], more=["Сняв пропеллеры!"], ignore="Нет.", diag=[]),
"SmartRTL недоступен": dict(
  causes=["Нет GPS fix при взлёте.", "Слишком мало/много точек (SRTL_POINTS).", "Потеря позиции в полёте."],
  steps=["Взлетай с хорошим GPS, дождись «SmartRTL: ready».", "SRTL_POINTS=300 (больше — больше памяти).", "SRTL_ACCURACY=2 м.", "Запасной режим: RTL/Land, настрой FS_THR_ENABLE=5/4."], more=[], ignore="Нет.", diag=[]),
"Terrain": dict(
  causes=["TERRAIN_ENABLE=0, а режим требует terrain.", "Нет места/данных."],
  steps=["TERRAIN_ENABLE=1.", "Подключи GCS (Mission Planner догружает terrain автоматически) или положи файлы на SD /APM/TERRAIN."], more=[], ignore="Нет.", diag=[]),
"Нет дальномера для режима": dict(
  causes=["RNGFND1_TYPE=0 или датчик нездоров."],
  steps=["Настрой RNGFND1_* и проверь показания Rangefinder в Status.", "Или переключи высоту RTL: RTL_ALT_TYPE=0."], more=[], ignore="Нет.", diag=[]),
"DroneCAN узел": dict(
  causes=["Нет терминатора 120 Ом на концах CAN.", "Дребезг питания CAN-устройств.", "Дубли node ID.", "CAN_D1_PROTOCOL=1, CAN_P1_DRIVER=1 не включены."],
  steps=["Включи CAN_P1_DRIVER=1, CAN_D1_PROTOCOL=1, перезагрузись.", "Проверь терминаторы, CAN-H/CAN-L, питание.", "Подключись DroneCAN GUI Tool, проверь узлы."], more=[], ignore="Нет.", diag=[]),
"Неверные SERVOx_MIN/MAX/FUNCTION": dict(
  causes=["MIN ≥ TRIM или MAX ≤ TRIM.", "SERVOx_FUNCTION задан на выход, которого нет/отключён BRD_PWM_COUNT."],
  steps=["Исправь SERVOx_MIN<TRIM<MAX (например 1000/1500/2000).", "Проверь BRD_PWM_COUNT/IO ports.", "Не используй disabled channel."], more=[], ignore="Нет.", diag=[]),
"Нет RPM от ESC": dict(
  causes=["Телеметрия ESC не включена.", "Неверное число полюсов SERVO_BLH_POLES."],
  steps=["Включи SERVO_BLH_AUTO=1 и SERVO_BLH_TRATE, проверь SERVO_BLH_POLES.", "Подключи телеметрию ESC к UART (SERIALn_PROTOCOL=16)."], more=[], ignore="Нет.", diag=[]),
"Конфликт Motor Interlock и E-Stop": dict(
  causes=["Включён Motor E-Stop при включённом Interlock."],
  steps=["Выключи E-Stop.", "Проверь RCx_OPTION=31 и 32 не на одном канале."], more=[], ignore="Нет.", diag=[]),
"Motor Interlock включён при арминге": dict(
  causes=["Тумблер Motor Interlock в положении «разрешено»."],
  steps=["Выключи тумблер.", "Убери функцию RCx_OPTION=32 если Interlock не нужен."], more=[], ignore="Нет.", diag=[]),
"Моторы остановлены E-Stop": dict(
  causes=["Сработал/включён Motor E-Stop."],
  steps=["Выключи тумблер E-Stop.", "Проверь, что канал не залипает."], more=[], ignore="Нет.", diag=[]),
"Система ещё не инициализирована": dict(
  causes=["Идёт загрузка IMU/EKF.", "Ошибка инициализации оборудования."],
  steps=["Подожди 20–30 с.", "Прочитай другие красные сообщения.", "Перезагрузи."], more=[], ignore="Нет.", diag=[]),
"Неверный FRAME_CLASS для мультикоптера": dict(
  causes=["FRAME_CLASS=0 (не задан) или значение не для мультикоптера."],
  steps=["Mandatory Hardware → Frame Type выбери схему.", "FRAME_CLASS: 1=Quad, 2=Hexa, 3=Octa, 4=OctaQuad, 5=Y6, 6=Heli, 7=Tri, 10=Doddecahexa, 12=DecaHexa.", "FRAME_TYPE: 0=Plus, 1=X, 2=V, 3=H…; перезагрузись."], more=[], ignore="Нет.", diag=[]),
"Неверное значение параметра": dict(
  causes=["PID, фильтры или другие параметры вне допустимого диапазона."],
  steps=["Читай, какой параметр назван после «Bad parameter:».", "Верни дефолт."], more=[], ignore="Нет.", diag=[]),
"ANGLE_MAX вне диапазона": dict(
  causes=["ANGLE_MAX <1000 или >8000."], steps=["Поставь 3000 (30°)."], more=[], ignore="Нет.", diag=[]),
"Некорректный FS_THR_VALUE": dict(
  causes=["FS_THR_VALUE <910 или ≥ RC3_MIN."], steps=["Поставь 975, RC3_MIN ≈ 1000, откалибруй пульт."], more=[], ignore="Нет.", diag=[]),
"Режим нельзя armить": dict(
  causes=["Для режима нужен GPS/позиция/миссия."], steps=["Включи Stabilize/AltHold и армь, потом переключи."], more=[], ignore="Нет.", diag=[]),
"Хранилище параметров": dict(
  causes=["Память параметров (FRAM/flash) переполнена или повреждена.", "Много Rally/Fence/Mission."],
  steps=["Reset to default: Mission Planner → Config → Full Parameter List → Reset.", "Очисти fence/mission/rally.", "Проверь питание."], more=[], ignore="Нет.", diag=[]),
"Дубли Aux-функций": dict(
  causes=["Две RCx_OPTION выполняют одно и то же."], steps=["Оставь по одному каналу на функцию."], more=[], ignore="Нет.", diag=[]),
"Канал режимов совпадает с аукс-каналом": dict(
  causes=["FLTMODE_CH совпадает с каналом RCx_OPTION."], steps=["Назначь FLTMODE_CH=5 и RC6+ для аукс."], more=[], ignore="Нет.", diag=[]),
"Несколько портов RC": dict(
  causes=["Два SERIALn_PROTOCOL=23."], steps=["Оставь один."], more=[], ignore="Нет.", diag=[]),
"Проблема логгера": dict(
  causes=["SD-карта заполнена/сбой.", "Флеш-лог переполнен.", "Поток записи завис."],
  steps=["Замени/отформатируй SD.", "Сотри логи (Mission Planner → Download → Erase).", "Снизь LOG_BITMASK."], more=[], ignore="Нет.", diag=[]),
"Дисбаланс по рысканию": dict(
  causes=["CW и CCW моторы выдают разную мощность: разные пропы/моторы, дефект.", "Центр тяжести смещён."],
  steps=["Проверь направления моторов и пропеллеры CW/CCW.", "Сбалансируй центр тяжести.", "Проверь выходы RCOU по лог."], more=[], ignore="Нет.", diag=[]),
"Шум от мотора": dict(
  causes=["Мотор/проп/подшипник даёт резонанс на частоте."],
  steps=["Баланс пропеллера, замена мотора.", "Настрой Harmonic Notch на эту частоту (INS_HNTCH_FREQ)."], more=[], ignore="Нет.", diag=[]),
"Сбрасывался watchdog": dict(
  causes=["Зависание цикла (слишком большая нагрузка, дефект SD/памяти).", "Провалы питания."],
  steps=["Проверь питание, SD-карту.", "Снизь нагрузку (логи/скрипты).", "Расшифруй Internal Errors (вкладка «Коды лога»)."], more=[], ignore="Нет.", diag=[]),
"Dead reckoning — потеря GPS": dict(
  causes=["Нет GPS, EKF летит по инерциалке."],
  steps=["Немедленно садись/RTL вручную.", "FS_DR_ENABLE (1=Land,2=RTL,3=SmartRTL), FS_DR_TIMEOUT."], more=[], ignore="Нет.", diag=[]),
"ARMING_CHECK отключены": dict(
  causes=["ARMING_CHECK=0 — защитные проверки выключены."], steps=["Верни ARMING_CHECK=1."], more=[], ignore="Только для отладки, никогда в полёте.", diag=[]),
"Резервный режим failsafe": dict(
  causes=["Основное действие failsafe невозможно (нет SmartRTL/GPS)."],
  steps=["Определи исходный failsafe выше по логу.", "Проверь GPS/SmartRTL."], more=[], ignore="Нет.", diag=[]),
"Режим недоступен": dict(
  causes=["Режим не поддержан сборкой/конфигурацией."], steps=["Выбери другой режим."], more=[], ignore="Нет.", diag=[]),
"В миссии нет TAKEOFF": dict(
  causes=["Auto на земле без команды взлёта."], steps=["Добавь TAKEOFF первой командой."], more=[], ignore="Нет.", diag=[]),
"Проблема миссии Auto": dict(
  causes=["Неверная команда, нет посадки/маршрута."], steps=["Проверь миссию, команды и порядок."], more=[], ignore="Нет.", diag=[]),
"Напряжение платы/серво вне диапазона": dict(
  causes=["Нестабильное питание, BEC, подпитка серво."],
  steps=["Проверь БП/BEC, подключи 5V стабильно.", "Проверь BRD_VBUS_MIN, BRD_VSERVO_MIN."], more=[], ignore="Нет.", diag=[]),
"Нагреватель IMU": dict(
  causes=["IMU холодная (BRD_HEAT_TARG)."], steps=["Подожди прогрева."], more=[], ignore="Можно отключить: BRD_HEAT_TARG=-1.", diag=[]),
"Препятствие слишком близко (Proximity)": dict(
  causes=["Объект ближе допустимого."], steps=["Отодвинь коптер, проверь PRX1_*."], more=[], ignore="Нет.", diag=[]),
}

# -*- coding: utf-8 -*-
"""Справочные таблицы: ссылки на документацию и расшифровка кодов лога (enum LogErrorSubsystem / LogErrorCode
из libraries/AP_Logger/AP_Logger.h и AP_InternalError::error_t из libraries/AP_InternalError/AP_InternalError.h)."""

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

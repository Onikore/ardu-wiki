# -*- coding: utf-8 -*-
"""Проверенная база, часть 3: служебные и редкие сообщения (сверено с кодом Copter-4.6.3)."""
from kb_verified import V, REBOOT

V(["Tmode: %u FAILED", "Tmode: ACRO is disabled", "Tmode: ALT_HOLD arm failed", "Tmode: Force disarm", "Tmode: GPS armed motors", "Tmode: GPS arming failed", "Tmode: LANDING",
   "Tmode: THROW is disabled", "Tmode: non-GPS armed motors", "Tmode: non-GPS arming failed", "Tmode: sticks not centered", "Tmode: thr mid %d", "Tmode: trim %u %u %u %u"],
  "Toy mode (особая прошивка для игрушечных дронов)", "Сообщения ArduCopter/toy_mode.cpp. Toy mode включается параметрами TMODE_* и используется только на специальных «игрушечных» сборках; на обычном коптере не появляется.",
  ["Если ты не настраивал toy mode — проверь TMODE_ENABLE (должен быть 0)."], ["TMODE_ENABLE"], [], code="ArduCopter/toy_mode.cpp")
V(["ESC %u is hardware inhibited", "ESC %u not detected", "Servo %u not detected"], "PiccoloCAN: ESC/серво не найдено или заблокировано", "ESC/серво на шине PiccoloCAN не отвечает или заблокирован аппаратно (inhibit).",
  ["Проверь CAN-подключение и маски устройств PiccoloCAN."], ["CAN_D1_PROTOCOL"], ["dronecan"], code="libraries/AP_PiccoloCAN/AP_PiccoloCAN.cpp")
V(["TCAL finished all IMUs", "TCAL[%u]: completed calibration tmin=%.1f tmax=%.1f", "TCAL[%u]: started calibration t=%.1fC tmax=%.1fC"], "Температурная калибровка IMU: ход процесса",
  "Информационные сообщения TCAL: начало, завершение по каждому IMU и окончание для всех.", ["После «finished» перезагрузи, параметры INS_TCALn_* сохранены."], ["INS_TCAL1_ENABLE"], [], code="libraries/AP_InertialSensor/AP_InertialSensor_tempcal.cpp")
V("change[%02x] 0x%02x -> 0x%02x", "IMU Invensense: регистр изменился сам", "Драйвер периодически сверяет регистры датчика; значение неожиданно поменялось (помеха на шине или сброс датчика). Драйвер перезаписывает регистр.",
  ["Разово — не страшно. Часто — проверь питание и вибрации платы."], [], [], code="libraries/AP_InertialSensor/AP_InertialSensor_Invensense.cpp")
V(["All parameters reset, reboot board", "Creating internal error", "Creating long loop", "Creating mutex deadlock", "calling AP_HAL::panic(...)", "deadlock passed", "dereferencing a bad thing",
   "entering lockup", "wiping parameter storage header"], "Ответ на специальную команду от GCS",
  "GCS_Common.cpp: реакция на MAVLink-команды перезагрузки/сброса с особыми значениями параметров (сброс всех параметров; отладочные коды 94–100 для тестов сбоев). Сами по себе не появляются — их кто-то отправил.",
  ["Если не ты — проверь, какая GCS/скрипт подключены.", "После «All parameters reset» нужна перезагрузка и заново вся настройка."], [], [], code="libraries/GCS_MAVLink/GCS_Common.cpp")
V("In OSD menu", "OSD в режиме меню", "Arm блокируется, пока на экране OSD открыто меню настройки параметров.", ["Выйди из меню OSD."], [], [], code="libraries/AP_OSD/AP_OSD.cpp")
V("VisOdom: reset", "Visual odometry сброшена", "Камера VIO (T265) сообщила о сбросе позиции.", ["Проверь камеру и компаньон-компьютер, если повторяется."], ["VISO_TYPE"], ["ekf3src"], code="libraries/AP_VisualOdom/AP_VisualOdom_IntelT265.cpp")
V("LTC2946: found monitor on bus %u", "Монитор батареи LTC2946 найден", "Информационное.", ["Ничего."], [], ["batt"], code="libraries/AP_BattMonitor/AP_BattMonitor_LTC2946.cpp")
V("Pong!", "HC-SR04: тестовый ответ", "Служебное сообщение драйвера ультразвукового дальномера.", ["Ничего."], [], ["rngf"], code="libraries/AP_RangeFinder/AP_RangeFinder_HC_SR04.cpp")
V(["Log recovery complete", "No last page of log %d at top=%X or bot=%X"], "Встроенный флеш логов: восстановление", "Логгер на dataflash восстановил структуру после сбоя / не нашёл конец лога.", ["Если повторяется — сотри логи на флеше."], [], ["sd"],
  code="libraries/AP_Logger/AP_Logger_Block.cpp")
V("Motors: unable to setup motor %u", "Скриптовая рама: нет выхода для мотора", "Скрипт 6DoF-рамы не нашёл выход с функцией этого мотора.", ["Назначь SERVOx_FUNCTION для моторов скриптовой рамы."], ["SERVO1_FUNCTION"], ["frame"], code="libraries/AP_Motors/AP_MotorsMatrix_6DoF_Scripting.cpp")
V("Chute is released", "Парашют уже выпущен", "Повторная команда выпуска игнорируется.", ["Ничего."], [], [], code="libraries/AP_Parachute/AP_Parachute.cpp")
V("Bootloader update OK", "Ключи bootloader обновлены", "Информационное (secure boot).", ["Ничего."], [], ["dfu"], code="libraries/AP_CheckFirmware/AP_CheckFirmware_secure_command.cpp")
V(["ADSB Avoidance Enabled", "ADSB Avoidance Disabled"], "Переключатель ADS-B avoidance", "Аукс-функция ADSB Avoidance (RCx_OPTION=38) включила/выключила уклонение.", ["Ничего."], ["RC7_OPTION"], [], code="libraries/RC_Channel/RC_Channel.cpp")
V("%s Failed to Initialize", "DDS/ROS2 клиент не инициализировался", "AP_Vehicle: init_dds_client() не удался (DDS_ENABLE включён).", ["Если ROS2/DDS не нужен — DDS_ENABLE=0."], ["DDS_ENABLE"], [], code="libraries/AP_Vehicle/AP_Vehicle.cpp")
V(["%s device is null!", "%s reset failed", "%s wrong I2C addr of 0x%2X, setting to 0x%2X"], "Датчик температуры TSYS03", "Датчик не найден / не ответил на сброс / задан неверный I2C-адрес (исправлен автоматически).",
  ["Проверь TEMP1_* и подключение датчика."], ["TEMP1_TYPE"], [], code="libraries/AP_TemperatureSensor/AP_TemperatureSensor_TSYS03.cpp")
V("Mission storage OK", "Хранилище снова работает", "После ошибки ввода-вывода хранилище восстановилось.", ["Ничего, но следи за повторениями."], [], [], code="libraries/StorageManager/StorageManager.cpp")

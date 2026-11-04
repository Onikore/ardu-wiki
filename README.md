# ArduCopter Error Wiki

Интерактивный поиск по сообщениям ArduCopter 4.6.3 (PreArm, failsafe, EKF, компас, GPS и др.) с причинами и решениями.
Данные автоматически извлечены из исходников ArduPilot (тег `Copter-4.6.3`), решения написаны вручную.

Сайт: https://onikore.github.io/ardu-wiki/

## Обновление данных

```bash
git clone --depth 1 --branch Copter-4.6.3 --filter=blob:none --sparse https://github.com/ArduPilot/ardupilot.git src/ap
git -C src/ap sparse-checkout set ArduCopter libraries
python build/build.py src/ap site
```

- `build/extract.py` — вытаскивает `GCS_SEND_TEXT`, `send_text`, `check_failed`, `failure_msg` и описания параметров
- `build/kb.py`, `build/kb_more.py` — база знаний (regex → причина/решение)
- `build/build.py` — собирает `site/data.js`

Чтобы улучшить разбор сообщения, добавь правило `R(...)` в `build/kb_more.py`.
Не официальный ресурс ArduPilot. Данные ArduPilot — GPLv3.

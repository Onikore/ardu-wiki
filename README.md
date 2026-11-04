# ArduCopter Error Wiki

Интерактивный поиск по сообщениям ArduCopter 4.6.3 (PreArm, failsafe, EKF, компас, GPS и др.) с причинами и решениями.

Сайт: https://onikore.github.io/ardu-wiki/

## Откуда данные

- **Тексты сообщений, файл/строка, условие `if (…)`, бит `ARMING_CHECK`** — автоматически из исходников тега `Copter-4.6.3` (`build/extract.py`).
- **Параметры** (имена, описания, диапазоны, значения) — из официальной базы `apm.pdef.json`, которую строит генератор ArduPilot `Tools/autotest/param_metadata/param_parse.py`.
- **Технический разбор** — вручную, по коду этой версии (`build/kb_verified*.py`); у каждой записи указана функция-источник. Покрыты все предупреждения и ошибки, актуальные для Copter.
- **Карточка для оператора** (`build/kb_ops.py`) — вердикт (взлёт заблокирован / сажай / внимание / информация) и возможные причины от частой к редкой, у каждой «как проверить» и «как исправить» с путями в Mission Planner.
- При сборке `build/validate.py` проверяет, что каждый упомянутый параметр существует в 4.6.3 и не переименован; иначе сборка падает.

## Обновление данных

```bash
git clone --depth 1 --branch Copter-4.6.3 --filter=blob:none --sparse https://github.com/ArduPilot/ardupilot.git src/ap
git -C src/ap sparse-checkout set ArduCopter libraries Tools/autotest/param_metadata
(cd src/ap && python Tools/autotest/param_metadata/param_parse.py --vehicle ArduCopter --format json)   # -> src/ap/apm.pdef.json
python build/build.py src/ap site
```

Чтобы добавить или исправить разбор, добавь `V("точный текст сообщения", ...)` в `build/kb_verified*.py`.
Не официальный ресурс ArduPilot. Данные ArduPilot — GPLv3.

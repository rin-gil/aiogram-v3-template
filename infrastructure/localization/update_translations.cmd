@echo off

cd ../..

call .venv\Scripts\activate

set "all_locales=en ru"

for %%L in (%all_locales%) do (
    pybabel update ^
    --input-file=./src/tgbot/locales/messages.pot ^
    --output-dir=./src/tgbot/locales ^
    --width=120 ^
    --init-missing ^
    --update-header-comment ^
    --locale=%%L
)

.venv\Scripts\deactivate

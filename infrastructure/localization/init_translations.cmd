@echo off

cd ../..

call .venv\Scripts\activate

set "all_locales=en ru"
for %%L in (%all_locales%) do (
    pybabel init ^
    --input-file="./src/tgbot/locales/messages.pot" ^
    --output-dir="./src/tgbot/locales" ^
    --width=120 ^
    --locale="%%L"
)

.venv\Scripts\deactivate

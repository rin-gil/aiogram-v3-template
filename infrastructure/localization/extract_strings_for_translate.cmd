@echo off

cd ../..

call .venv\Scripts\activate

pybabel extract ^
-F ./infrastructure/localization/babel.cfg ^
--input-dirs=./src/tgbot ^
--output-file=./src/tgbot/locales/messages.pot ^
--width=120 ^
--sort-by-file ^
--project=Telegram-Bot ^
--version=1.0.0

.venv\Scripts\deactivate

#!/bin/bash

cd ../..

source venv/bin/activate

ALL_LOCALES="en ru"

for LOCALE in $ALL_LOCALES; do
    pybabel update \
    --input-file=./src/tgbot/locales/messages.pot \
    --output-dir=./src/tgbot/locales \
    --width=120 \
    --init-missing \
    --update-header-comment \
    --locale="$LOCALE"
done

deactivate

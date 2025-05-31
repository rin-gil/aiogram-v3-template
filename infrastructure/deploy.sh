#!/bin/bash

mkdir /opt/arbitrage-scanner-bot
cd /opt/ || exit
git init
git config core.sparseCheckout true
git remote add origin https://github.com/rin-gil/arbitrage-scanner-bot
echo "src" > .git/info/sparse-checkout
git fetch --depth 1 origin master
git checkout master
rm -r -f .git
mv src/* .
mv src/.env.example .env
rm src -r -f
rm requirements-dev.txt -r -f
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate
( cd .. && rm -f deploy.sh )

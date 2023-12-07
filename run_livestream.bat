@echo off
:loop
python livestream.py
git add .
git commit -m "update json"
git push
timeout /t 60
goto loop
@echo off
:loop
python livestream.py
git rm -r --cached
git add .
git commit -m "update json"
git push
timeout /t 30
goto loop
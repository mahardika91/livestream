@echo off
:loop
python livestream.py
git add .
git commit 'm' 'fixture'
git push
timeout /t 10
goto loop

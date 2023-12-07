@echo off
:loop
python livestream.py
timeout /t 60
goto loop
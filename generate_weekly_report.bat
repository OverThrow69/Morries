@echo off
cd /d "%~dp0"
py pygame_version\generate_weekly_report.py
pause

@echo off
echo Installing dependencies...
pip install -r requirements.txt --quiet
echo.
echo Starting Receipt Splitter server...
echo.
cd /d "%~dp0"
set RECEIPTS_DIR=C:\Users\emily\My Drive\Receipts
python server.py
pause

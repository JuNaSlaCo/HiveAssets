taskkill /f /pid HASRV.exe
cd ../bottle_server
python -m PyInstaller --onefile --add-data "views;views" --add-data "static;static" HASRV.py
pause
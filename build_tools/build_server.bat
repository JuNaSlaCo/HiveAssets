taskkill /f /pid server.exe
cd ../bottle_server
python -m PyInstaller --onefile --add-data "views;views" --add-data "static;static" server.py
pause
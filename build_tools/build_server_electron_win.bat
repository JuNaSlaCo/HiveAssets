taskkill /f /pid server.exe
cd ../bottle_server
python -m PyInstaller --onefile --add-data "views;views" --add-data "static;static" HASRV.py

SET mypath=%~dp0
echo %mypath:~0,-1%
cd %mypath:~0,-1%
cd ..
npx electron-builder --win
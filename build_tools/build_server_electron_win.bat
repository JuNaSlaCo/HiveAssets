taskkill /f /pid HASRV.exe
cd ../bottle_server
python -m PyInstaller --onefile --add-data "views;views" --add-data "static;static" server.py
del ..\bottle_server\dist\HASRV.exe
ren ..\bottle_server\dist\server.exe HASRV.exe

SET mypath=%~dp0
echo %mypath:~0,-1%
cd %mypath:~0,-1%
cd ..
npx electron-builder --win
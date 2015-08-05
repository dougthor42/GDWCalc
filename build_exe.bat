call C:\WinPython27\Scripts\env.bat
cd C:\WinPython27\projects\github\GDWCalc
echo ----- Deleting previous build -----
RMDIR /S /Q C:\WinPython27\projects\github\GDWCalc\build\exe.win32-2.7
echo ----- Running build script -----
python build_exe.py build
echo ----- Launching Application -----
cd .\build\exe.win32-2.7\
GDWCalc.exe
cd ..\..
echo ----- Finished -----
@echo off
set size=0
for /r %%x in (.\build\exe.win32-2.7\*) do set /a size+=%%~zx
set /a mb = %size% / 1000000
echo %size% Bytes
echo %mb% MB
call C:\WinPython3662\Scripts\env.bat
cd C:\gitlab\dthor\GDWCalc

echo ----- Deleting previous build -----
RMDIR /S /Q C:\gitlab\dthor\GDWCalc\build\exe.win-amd64-3.6

echo ----- Running build script -----
python build_exe.py build || goto :build_error

echo ----- Launching Application -----
cd .\build\exe.win-amd64-3.6\
GDWCalc.exe || goto :exe_error
cd ..\..

echo ----- Finished -----
@echo off
set size=0
for /r %%x in (.\build\exe.win-amd64-3.6\*) do set /a size+=%%~zx
set /a mb = %size% / 1000000
echo %size% Bytes
echo %mb% MB
goto :end

:build_error
echo !!!----- Build Failed -----!!!
exit /b %ERRORLEVEL%

:exe_error
echo !!!----- Executable Failed -----!!!
exit /b %ERRORLEVEL%

:end
echo ----- Success! -----

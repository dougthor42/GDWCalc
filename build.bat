SETLOCAL
SET PATH=%PATH%;C:\WinPython27\python-2.7.6;C:\WinPython27\python-2.7.6\Scripts
cxfreeze.bat "GDWCalc.py" --target-dir "dist\GDWCalc v1.5.2" -s --base-name=Win32GUI -O --compress --exclude-modules _gtkagg,_tkagg,bsddb,curses,email,pywin.debugger,pywin.debugger.dbgcon,pywin.dialogs,tcl,Tkconstants,Tkinter,scipy,pil
ENDLOCAL
@echo off
REM Builds Flyerize_gui.exe with PyInstaller and adds it to the Send To menu.
REM Run this once from the folder that contains Flyerize_gui.py.
python -m pip install -q opencv-python-headless numpy pillow pyinstaller
if errorlevel 1 goto fail
REM '-w' is '--windowed' which is the same as '--noconsole'
python -m PyInstaller -F -w -y -n Flyerize_gui Flyerize_gui.py
if errorlevel 1 goto fail
powershell -NoProfile -Command "$s=(New-Object -ComObject WScript.Shell).CreateShortcut([Environment]::GetFolderPath('SendTo')+'\Flyerize_gui.lnk'); $s.TargetPath=(Resolve-Path 'dist\Flyerize_gui.exe').Path; $s.Save()"
echo.
echo Done. Right-click a photo or folder, then Send to, then Flyerize_gui.
certutil -hashfile dist\Flyerize_gui.exe SHA256
rem pause
exit /b 0
:fail
echo.
echo Build failed. Check the messages above.
pause
exit /b 1

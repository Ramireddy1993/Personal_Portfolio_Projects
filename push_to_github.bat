@echo off
set "PATH=C:\Users\arami\AppData\Local\Programs\Git\cmd;%PATH%"
cd /d "%~dp0"
echo ===================================================
echo Pushing Personal_Portfolio_Projects to GitHub...
echo Target: https://github.com/Ramireddy1993/Personal_Portfolio_Projects.git
echo ===================================================
echo.
git push -u origin main
echo.
if %errorlevel% equ 0 (
    echo [SUCCESS] Code pushed successfully to GitHub!
) else (
    echo [ERROR] Push failed. If prompted for password, use a GitHub Personal Access Token.
)
pause

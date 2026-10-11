@echo off
set "PATH=C:\Users\Lucian Dan\AppData\Local\Programs\Git\cmd;%PATH%"
cd /d "c:\Users\Lucian Dan\Desktop\geo-attribute-llm"
echo [INFO] Pushing GeoAttribute-LLM to GitHub (origin main)...
git push -u origin main
if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================================
    echo [SUCCESS] Repository successfully pushed to GitHub!
    echo Check it out at: https://github.com/GhileaLucian/geo-attribute-llm
    echo ========================================================
) else (
    echo.
    echo [NOTE] If this is your first push, please make sure you created
    echo the empty repository at: https://github.com/new (named geo-attribute-llm)
)
pause

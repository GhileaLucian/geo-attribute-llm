@echo off
setlocal
cd /d "%~dp0"
where git >nul 2>nul
if errorlevel 1 (
    echo Git is not on PATH. Install Git for Windows or use Git Bash.
    exit /b 1
)
git diff --quiet
if errorlevel 1 goto uncommitted
git diff --cached --quiet
if errorlevel 1 goto uncommitted
git status --porcelain | findstr /r "." >nul
if not errorlevel 1 goto uncommitted
echo Pushing the current branch to origin...
git push -u origin HEAD
exit /b %errorlevel%

:uncommitted
echo There are uncommitted files. Review and commit the project first.
git status --short
echo Follow docs/GITHUB_UPLOAD_RO.md, then run this script again.
exit /b 1

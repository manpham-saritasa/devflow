@echo off
cd /d "%~dp0..\..\.."
echo Starting md-view server at http://localhost:8080
echo Open: http://localhost:8080/.ai/skills/md-view/viewer.html
echo Press Ctrl+C to stop
echo.
start http://localhost:8080/.ai/skills/md-view/viewer.html?file=.ai/skills/md-view/README.md
py.exe -m http.server 8080
pause

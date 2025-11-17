@echo off

rem echo {"jsonrpc": "2.0", "id": 1, "method": "tools/list"} | uv run weather.py

(
  timeout /t 1 >nul
  echo {"jsonrpc":"2.0","id":0,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"cmd-client","version":"1.0"}}}
  timeout /t 1 >nul
  echo {"jsonrpc":"2.0","method":"notifications/initialized","params":null}
  timeout /t 1 >nul
  echo {"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": null}
) | uv run ..\src\weather.py
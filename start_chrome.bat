@echo off
echo 启动调试版 Chrome...
start "" "C:\Users\admin\AppData\Local\Google\Chrome\Application\chrome.exe" ^
--remote-debugging-port=9222 ^
--user-data-dir="C:\selenium\ChromeData" ^
--disable-web-security ^
--allow-insecure-localhost ^
--no-first-run
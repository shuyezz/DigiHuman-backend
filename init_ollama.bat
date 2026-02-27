@echo off

REM 设置下载文件的 URL 和本地文件名
set url="https://ollama.com/download/OllamaSetup.exe"
set filename=OllamaSetup.exe

REM 设置安装目录
set install_dir=%~dp0\InstallFolder

REM 使用 PowerShell 命令下载文件并显示进度
powershell -command "& { $webClient = New-Object System.Net.WebClient; $webClient.DownloadFile('%url%', '%filename%'); }"

REM 等待下载完成
ping 127.0.0.1 -n 10 > nul

REM 创建安装目录
if not exist "%install_dir%" (
    mkdir "%install_dir%"
    echo 安装文件夹已创建
) else (
    echo 安装文件夹已存在
)

REM 切换到安装目录
cd /d "%install_dir%"

REM 运行下载的 exe 文件
start %~dp0\%filename%

pause
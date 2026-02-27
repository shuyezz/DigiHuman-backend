@echo off

REM 设置下载文件的 URL 和本地文件名
set url="https://ollama.com/download/OllamaSetup.exe"
set filename=OllamaSetup.exe

REM 设置安装目录
set install_dir=%~dp0\InstallFolder

REM 使用 BITSAdmin 下载文件并显示进度
bitsadmin /transfer myDownloadJob /download /priority normal %url% %install_dir%\%filename%

REM 等待下载完成
:CheckComplete
bitsadmin /complete myDownloadJob 2>nul || (
    timeout /t 1 /nobreak >nul
    goto CheckComplete
)

REM 创建安装目录
if not exist "%install_dir%" (
    mkdir "%install_dir%"
    echo 安装文件夹已创建
) else (
    echo 安装文件夹已存在
)

REM 运行下载的 exe 文件
start %install_dir%\%filename%

pause

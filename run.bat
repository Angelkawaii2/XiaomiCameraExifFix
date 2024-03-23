@echo off
rem 激活虚拟环境
call %~dp0venv\Scripts\activate.bat
rem 运行python脚本，传入命令行参数
python %~dp0main.py --dng-dir=%1 --jpg-dir=%2
rem 关闭虚拟环境
deactivate
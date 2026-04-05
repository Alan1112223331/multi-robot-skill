@echo off
REM Multi-Robot Skill 自动安装脚本 (Windows)
REM 适用于 OpenClaw 或其他 AI Agent

echo ==========================================
echo Multi-Robot Skill 安装程序 (Windows)
echo ==========================================

REM 获取脚本所在目录
cd /d "%~dp0"

echo.
echo 项目目录: %CD%

REM 检查 Python
echo.
echo 检查 Python 版本...
python --version
if errorlevel 1 (
    echo 错误: Python 未安装或不在 PATH 中
    pause
    exit /b 1
)

REM 检查 pip
echo.
echo 检查 pip...
pip --version
if errorlevel 1 (
    echo 错误: pip 未安装
    pause
    exit /b 1
)

REM 安装依赖
echo.
echo 安装依赖...
if exist requirements.txt (
    pip install -r requirements.txt
) else (
    echo 警告: requirements.txt 不存在，跳过依赖安装
)

REM 安装包（开发模式）
echo.
echo 安装 multi_robot_skill 包（开发模式）...
pip install -e .

REM 验证安装
echo.
echo 验证安装...
python -c "from multi_robot_skill import MultiRobotSkill; print('✓ 导入成功')" 2>nul
if errorlevel 1 (
    echo.
    echo ==========================================
    echo ✗ 安装失败
    echo ==========================================
    echo.
    echo 请检查错误信息并重试
    pause
    exit /b 1
)

echo.
echo ==========================================
echo ✓ 安装成功！
echo ==========================================
echo.
echo 现在你可以使用：
echo   from multi_robot_skill import MultiRobotSkill
echo.
echo 快速开始：
echo   python quick_start.py
echo.
echo 查看示例：
echo   python examples\mycobot_example.py
echo.
pause

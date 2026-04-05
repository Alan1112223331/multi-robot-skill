#!/bin/bash
# Multi-Robot Skill 自动安装脚本
# 适用于 OpenClaw 或其他 AI Agent

set -e  # 遇到错误立即退出

echo "=========================================="
echo "Multi-Robot Skill 安装程序"
echo "=========================================="

# 获取脚本所在目录（项目根目录）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo ""
echo "项目目录: $SCRIPT_DIR"

# 检查 Python 版本
echo ""
echo "检查 Python 版本..."
PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
echo "当前 Python 版本: $PYTHON_VERSION"

# 检查 pip
echo ""
echo "检查 pip..."
if ! command -v pip &> /dev/null; then
    echo "错误: pip 未安装"
    exit 1
fi
echo "pip 版本: $(pip --version)"

# 安装依赖
echo ""
echo "安装依赖..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo "警告: requirements.txt 不存在，跳过依赖安装"
fi

# 安装包（开发模式）
echo ""
echo "安装 multi_robot_skill 包（开发模式）..."
pip install -e .

# 验证安装
echo ""
echo "验证安装..."
if python -c "from multi_robot_skill import MultiRobotSkill; print('✓ 导入成功')" 2>/dev/null; then
    echo ""
    echo "=========================================="
    echo "✓ 安装成功！"
    echo "=========================================="
    echo ""
    echo "现在你可以使用："
    echo "  from multi_robot_skill import MultiRobotSkill"
    echo ""
    echo "快速开始："
    echo "  python quick_start.py"
    echo ""
    echo "查看示例："
    echo "  python examples/mycobot_example.py"
    echo ""
else
    echo ""
    echo "=========================================="
    echo "✗ 安装失败"
    echo "=========================================="
    echo ""
    echo "请检查错误信息并重试"
    exit 1
fi

# 安装指南

## 问题说明

如果你遇到 `ModuleNotFoundError: No module named 'multi_robot_skill'` 错误，这是因为 Python 无法找到这个包。

## 解决方案

### 方法 1：开发模式安装（推荐）

在项目根目录下运行：

```bash
pip install -e .
```

这会将项目安装为可编辑模式，你可以修改代码并立即生效。

### 方法 2：正式安装

```bash
pip install .
```

### 方法 3：从 GitHub 直接安装

```bash
pip install git+https://github.com/Alan1112223331/multi-robot-skill.git
```

### 方法 4：手动添加到 Python 路径（临时方案）

在你的脚本开头添加：

```python
import sys
import os

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 现在可以导入了
from multi_robot_skill import MultiRobotSkill
```

## 验证安装

安装完成后，运行以下命令验证：

```python
python -c "from multi_robot_skill import MultiRobotSkill; print('安装成功！')"
```

## OpenClaw 用户特别说明

如果你在 OpenClaw 中使用这个 skill：

1. **确保在 OpenClaw 的 Python 环境中安装**：
   ```bash
   # 激活 OpenClaw 的虚拟环境（如果有）
   source /path/to/openclaw/venv/bin/activate  # Linux/Mac
   # 或
   .\path\to\openclaw\venv\Scripts\activate  # Windows
   
   # 然后安装
   pip install -e /path/to/multi-robot-skill
   ```

2. **或者让 OpenClaw Agent 自动处理**：
   告诉 OpenClaw：
   > "帮我安装这个 skill：https://github.com/Alan1112223331/multi-robot-skill.git"
   
   Agent 会自动执行 `pip install` 命令。

## 常见问题

### Q: 为什么需要安装？
A: Python 需要知道在哪里找到你的包。安装会将包注册到 Python 的 site-packages 目录。

### Q: 开发模式和正式安装有什么区别？
A: 开发模式（`-e`）创建符号链接，修改代码立即生效；正式安装会复制文件，需要重新安装才能看到更改。

### Q: 我可以不安装直接使用吗？
A: 可以，但需要手动管理 Python 路径（方法 4），不推荐。

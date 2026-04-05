# OpenClaw 用户故障排查指南

## 问题：`ModuleNotFoundError: No module named 'multi_robot_skill'`

这是最常见的问题，原因是 Python 无法找到 `multi_robot_skill` 包。

### 根本原因

Python 的模块导入系统需要知道在哪里找到你的包。有三种方式让 Python 找到包：

1. **安装到 site-packages**（推荐）
2. **添加到 sys.path**（临时方案）
3. **设置 PYTHONPATH 环境变量**（全局方案）

### 解决方案

#### 方案 1：正确安装包（最推荐）

在项目根目录运行：

```bash
pip install -e .
```

这会：
- 将包注册到 Python 的 site-packages
- 创建符号链接，修改代码立即生效
- 让所有 Python 脚本都能导入这个包

**验证安装：**

```bash
python -c "from multi_robot_skill import MultiRobotSkill; print('安装成功！')"
```

#### 方案 2：让 OpenClaw Agent 自动安装

告诉 OpenClaw：

```
帮我安装这个 skill：
cd /path/to/multi-robot-skill
pip install -e .
```

Agent 会自动执行命令。

#### 方案 3：使用 quick_start.py（无需安装）

我们提供了一个自动处理路径的脚本：

```bash
python quick_start.py
```

这个脚本会自动添加项目路径到 `sys.path`，无需安装。

#### 方案 4：手动修复导入路径（临时）

如果你在自己的脚本中使用，在文件开头添加：

```python
import sys
import os

# 添加 multi-robot-skill 目录到 Python 路径
project_root = "/path/to/multi-robot-skill"  # 修改为实际路径
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 现在可以导入了
from multi_robot_skill import MultiRobotSkill
```

## 问题：相对导入错误 `attempted relative import with no known parent package`

### 原因

当你直接运行包内部的文件时（如 `python skill.py`），Python 不知道这个文件属于哪个包。

### 解决方案

**不要直接运行包内部的文件！** 应该：

1. **安装包后导入使用**（推荐）：
   ```bash
   pip install -e .
   python -c "from multi_robot_skill import MultiRobotSkill; skill = MultiRobotSkill()"
   ```

2. **使用提供的示例脚本**：
   ```bash
   python examples/mycobot_example.py
   ```

3. **使用 quick_start.py**：
   ```bash
   python quick_start.py
   ```

## 问题：OpenClaw 找不到适配器

### 症状

```
ERROR: 未知的机器人类型: mycobot，请使用 register_adapter() 注入自定义适配器
```

### 原因

`MultiRobotSkill` 只内置了 `vansbot` 和 `puppypi` 两种机器人类型。

### 解决方案

#### 方法 1：使用 `register_adapter()` 注入自定义适配器

```python
from multi_robot_skill import MultiRobotSkill
from examples.mycobot_example import MyCobotAdapter  # 使用我们提供的示例

skill = MultiRobotSkill()

# 创建适配器
mycobot = MyCobotAdapter("mycobot", "http://192.168.1.100:5000")

# 注册适配器
skill.register_adapter(mycobot)
```

#### 方法 2：让 AI Agent 生成适配器

告诉 OpenClaw：

```
我有一个 MyCobot 机械臂，API 文档如下：
[粘贴你的 API 文档]

请帮我创建一个适配器，参考 examples/mycobot_example.py 的格式。
```

Agent 会自动生成适配器代码。

#### 方法 3：参考示例修改

查看 `examples/mycobot_example.py`，这是一个完整的 MyCobot 适配器示例。你可以：

1. 复制这个文件
2. 修改 API 端点和动作实现
3. 在你的脚本中导入使用

## 问题：网络连接失败

### 症状

```
ERROR: 连接失败: [Errno 111] Connection refused
```

### 排查步骤

1. **检查机器人是否在线**：
   ```bash
   ping 192.168.1.100
   ```

2. **检查 API 服务是否运行**：
   ```bash
   curl http://192.168.1.100:5000/api/status
   ```

3. **检查防火墙设置**：
   确保端口没有被防火墙阻止。

4. **检查 IP 地址和端口**：
   确认你使用的 IP 和端口是正确的。

## 问题：任务执行失败

### 症状

```
✗ 任务 1: 执行失败: [错误信息]
```

### 排查步骤

1. **启用详细日志**：
   ```python
   skill = MultiRobotSkill(log_level="DEBUG")
   ```

2. **检查机器人状态**：
   ```python
   robot = skill.get_robot("mycobot")
   state = robot.get_state()
   print(state)
   ```

3. **单独测试每个动作**：
   ```python
   result = robot.execute_action("move_to", {"x": 100, "y": 200, "z": 150})
   print(result)
   ```

4. **检查参数格式**：
   确保传递的参数符合 API 要求。

## 完整的工作流程示例

### 1. 安装

```bash
cd /path/to/multi-robot-skill
pip install -e .
```

### 2. 创建适配器（如果需要）

参考 `examples/mycobot_example.py` 创建你的适配器。

### 3. 编写控制脚本

```python
from multi_robot_skill import MultiRobotSkill
from your_adapter import YourRobotAdapter

# 初始化
skill = MultiRobotSkill()

# 注册机器人
robot = YourRobotAdapter("robot1", "http://192.168.1.100:5000")
skill.register_adapter(robot)

# 创建任务
plan = skill.create_plan("测试任务")
task = skill.create_task("robot1", "move_to", {"x": 100, "y": 200})
plan.add_task(task)

# 执行
results = skill.execute_plan(plan)
print(results)
```

### 4. 运行

```bash
python your_script.py
```

## 还是不行？

如果以上方法都不能解决问题，请：

1. **检查 Python 版本**：
   ```bash
   python --version  # 需要 >= 3.8
   ```

2. **检查依赖是否安装**：
   ```bash
   pip install -r requirements.txt
   ```

3. **提供完整的错误信息**：
   包括完整的堆栈跟踪（traceback）

4. **提交 Issue**：
   https://github.com/Alan1112223331/multi-robot-skill/issues

## 快速参考

| 问题 | 解决方案 |
|------|---------|
| 找不到模块 | `pip install -e .` |
| 相对导入错误 | 不要直接运行 `skill.py`，使用示例脚本 |
| 找不到适配器 | 使用 `register_adapter()` 注入 |
| 连接失败 | 检查 IP、端口、防火墙 |
| 任务失败 | 启用 DEBUG 日志，检查参数 |

## 联系支持

- GitHub Issues: https://github.com/Alan1112223331/multi-robot-skill/issues
- 文档: [README.md](README.md), [SKILL.md](SKILL.md)

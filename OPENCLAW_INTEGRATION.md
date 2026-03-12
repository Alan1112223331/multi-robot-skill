# OpenClaw 集成指南

本文档说明如何将 Multi-Robot Skill 集成到 OpenClaw 框架中。

## 📦 什么是 OpenClaw？

OpenClaw 是基于 Anthropic Claude 的 AI Agent 框架，支持通过即时通讯（微信、WhatsApp 等）控制各种系统。

## 🔗 集成方式

### 方式 1: 作为 OpenClaw Skill 使用

将本项目打包为 OpenClaw Skill，让 OpenClaw Agent 可以直接调用。

#### 步骤 1: 创建 Skill 元数据

在项目根目录创建 `skill.json`:

```json
{
  "name": "multi-robot-coordination",
  "version": "1.0.0",
  "description": "多机器人协同控制技能",
  "author": "Your Name",
  "main": "skill.py",
  "dependencies": {
    "python": ">=3.8",
    "packages": ["requests>=2.28.0"]
  },
  "capabilities": [
    "robot_control",
    "multi_agent_coordination",
    "task_planning"
  ]
}
```

#### 步骤 2: 创建 OpenClaw 包装器

创建 `openclaw_wrapper.py`:

```python
"""
OpenClaw Skill 包装器
"""

from multi_robot_skill import MultiRobotSkill

# 全局 Skill 实例
_skill = None

def initialize(config: dict) -> dict:
    """
    初始化 Skill

    OpenClaw 会在加载 Skill 时调用此函数
    """
    global _skill
    _skill = MultiRobotSkill(
        max_workers=config.get("max_workers", 4),
        log_level=config.get("log_level", "INFO")
    )

    # 注册机器人
    robots = config.get("robots", [])
    for robot in robots:
        _skill.register_robot(
            name=robot["name"],
            endpoint=robot["endpoint"],
            robot_type=robot.get("type", "auto"),
            **robot.get("config", {})
        )

    return {
        "status": "initialized",
        "robots": _skill.list_robots()
    }

def execute(command: str, params: dict = None) -> dict:
    """
    执行命令

    OpenClaw 会调用此函数来执行用户命令
    """
    global _skill
    if not _skill:
        return {"error": "Skill not initialized"}

    params = params or {}

    # 根据命令类型执行不同操作
    if command == "create_plan":
        plan = _skill.create_plan(
            name=params.get("name", "任务"),
            description=params.get("description", "")
        )
        return {"plan_id": plan.id}

    elif command == "add_task":
        plan_id = params.get("plan_id")
        plan = _skill.planner.get_plan(plan_id)
        if not plan:
            return {"error": "Plan not found"}

        task = _skill.create_task(
            robot=params["robot"],
            action=params["action"],
            params=params.get("params", {}),
            **params.get("task_config", {})
        )
        plan.add_task(task)
        return {"task_id": task.id}

    elif command == "execute_plan":
        plan_id = params.get("plan_id")
        plan = _skill.planner.get_plan(plan_id)
        if not plan:
            return {"error": "Plan not found"}

        results = _skill.execute_plan(plan)
        return {
            "success": all(r.success for r in results),
            "results": [r.to_dict() for r in results]
        }

    elif command == "get_status":
        return _skill.get_status()

    else:
        return {"error": f"Unknown command: {command}"}

def shutdown():
    """
    关闭 Skill

    OpenClaw 会在卸载 Skill 时调用此函数
    """
    global _skill
    if _skill:
        _skill.shutdown()
        _skill = None
```

#### 步骤 3: 配置文件

创建 `openclaw_config.yaml`:

```yaml
skill:
  name: multi-robot-coordination
  enabled: true

  config:
    max_workers: 4
    log_level: INFO

    robots:
      - name: vansbot
        endpoint: http://192.168.3.113:5000
        type: vansbot

      - name: dog1
        endpoint: http://localhost:8000
        type: puppypi
        config:
          robot_id: 1

      - name: dog2
        endpoint: http://localhost:8000
        type: puppypi
        config:
          robot_id: 2
```

#### 步骤 4: 安装到 OpenClaw

```bash
# 方法 1: 通过 ClawHub 安装（如果已发布）
npx skills add multi-robot-coordination

# 方法 2: 本地安装
cp -r multi_robot_skill ~/.openclaw/skills/multi-robot-coordination
```

### 方式 2: 直接在 OpenClaw Agent 中使用

如果你的 OpenClaw Agent 是用 Python 编写的，可以直接导入使用：

```python
from multi_robot_skill import MultiRobotSkill

class MyOpenClawAgent:
    def __init__(self):
        self.robot_skill = MultiRobotSkill()

        # 注册机器人
        self.robot_skill.register_robot("vansbot", "http://192.168.3.113:5000")
        self.robot_skill.register_robot("dog1", "http://localhost:8000", robot_type="puppypi", robot_id=1)

    def handle_user_command(self, command: str):
        """处理用户命令"""
        # 使用 LLM 理解命令并生成任务计划
        plan = self.parse_command_to_plan(command)

        # 执行计划
        results = self.robot_skill.execute_plan(plan)

        return results

    def parse_command_to_plan(self, command: str):
        """使用 LLM 将自然语言命令转换为任务计划"""
        # 这里可以调用 Claude API 来理解命令
        # 然后创建相应的任务计划

        plan = self.robot_skill.create_plan("用户任务")

        # 示例：如果命令是"让机械臂抓取物体"
        if "抓取" in command:
            detect = self.robot_skill.create_task("vansbot", "detect_objects")
            grab = self.robot_skill.create_task("vansbot", "grab", depends_on=[detect.id])
            plan.add_task(detect)
            plan.add_task(grab)

        return plan
```

## 🎯 使用示例

### 通过 OpenClaw 即时通讯控制

用户在微信中发送：
```
让机械臂抓取绿色方块放到狗1的篮筐里，然后让狗1运送到卸货区
```

OpenClaw Agent 处理流程：
1. 接收用户消息
2. 使用 Claude 理解任务意图
3. 调用 Multi-Robot Skill 创建任务计划
4. 执行任务计划
5. 返回执行结果给用户

### 代码示例

```python
# OpenClaw Agent 代码
from openclaw import Agent
from multi_robot_skill import MultiRobotSkill

class RobotCoordinationAgent(Agent):
    def __init__(self):
        super().__init__()
        self.skill = MultiRobotSkill()
        self.setup_robots()

    def setup_robots(self):
        """设置机器人"""
        self.skill.register_robot("vansbot", "http://192.168.3.113:5000")
        self.skill.register_robot("dog1", "http://localhost:8000", robot_type="puppypi", robot_id=1)

    async def on_message(self, message: str, platform: str):
        """处理用户消息"""
        # 使用 Claude 理解任务
        task_plan = await self.understand_task(message)

        # 执行任务
        results = self.skill.execute_plan(task_plan)

        # 返回结果
        if all(r.success for r in results):
            await self.reply("✅ 任务完成！")
        else:
            await self.reply("❌ 任务执行失败，请检查机器人状态")

    async def understand_task(self, message: str):
        """使用 Claude 理解任务并生成计划"""
        # 调用 Claude API
        response = await self.claude.complete(
            prompt=f"""
            用户说：{message}

            请分析这个任务，并生成机器人任务计划。
            可用的机器人：
            - vansbot (机械臂): detect_objects, grab, release, move_to_place
            - dog1 (机器狗): move_to_zone, load, unload

            请返回 JSON 格式的任务计划。
            """
        )

        # 解析 Claude 的响应并创建任务计划
        plan = self.skill.create_plan("用户任务")
        # ... 根据 Claude 的响应添加任务

        return plan

# 启动 Agent
agent = RobotCoordinationAgent()
agent.run()
```

## 🔧 高级配置

### 自定义事件处理

```python
# 在 OpenClaw Agent 中监听事件
skill.on_event("task_started", lambda e:
    openclaw.send_message(f"🔄 开始执行: {e['task_name']}")
)

skill.on_event("task_completed", lambda e:
    openclaw.send_message(f"✅ 完成: {e['task_name']}")
)

skill.on_event("task_failed", lambda e:
    openclaw.send_message(f"❌ 失败: {e['error']}")
)
```

### 错误处理

```python
# 配置错误处理策略
skill.configure_error_handling({
    "max_retries": 3,
    "retry_delay": 1.0,
    "default_strategy": "retry"
})

# 注册错误回调
def on_error(error_info):
    openclaw.send_message(f"⚠️ 错误: {error_info['error']}")
    openclaw.send_message("正在重试...")

skill.error_handler.config.on_error_callback = on_error
```

## 📚 参考资源

- [Multi-Robot Skill 文档](README.md)
- [OpenClaw 官方文档](https://github.com/openclaw/openclaw)
- [使用指南](USAGE_GUIDE.md)
- [示例代码](examples/)

## 🤝 贡献

欢迎为 OpenClaw 集成贡献代码和文档！

## 📄 许可证

MIT License

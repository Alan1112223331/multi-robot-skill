---
name: multi-robot
description: "多机器人协同控制 Skill。让 AI Agent 具备感知反馈、动态适配、并行调度多种机器人的能力。支持机械臂、四足机器人等任意 HTTP API 机器人。"
metadata: {
  "openclaw": {
    "emoji": "🤖",
    "requires": {
      "python": ">=3.8",
      "pip": ["requests>=2.28.0"]
    }
  }
}
---

# Multi-Robot Coordination Skill

## 首次使用必读

**⚠️ 重要：第一次使用前必须重命名目录！**

如果你的 skill 目录名是 `multi-robot`（带连字符），必须先重命名为 `multi_robot_skill`（下划线）：

```bash
# 在 skills 目录下执行
mv multi-robot multi_robot_skill
# 或 Windows PowerShell
Rename-Item multi-robot multi_robot_skill
```

**然后安装 Skill：**

如果你遇到 `ModuleNotFoundError: No module named 'multi_robot_skill'` 错误，有两种安装方式：

### 方式 1：一键安装（推荐）

```bash
# Windows 用户
./install.bat

# Linux/Mac 用户
bash install.sh
```

### 方式 2：手动安装

```bash
# 进入项目根目录（SKILL.md 所在目录）
cd /path/to/multi_robot_skill

# 安装包（开发模式，修改代码立即生效）
pip install -e .
```

**验证安装：**

```bash
python -c "from multi_robot_skill import MultiRobotSkill; print('✓ 安装成功')"
```

如果验证失败，检查：
1. Python 版本 >= 3.8
2. pip 是否可用
3. 是否在正确的虚拟环境中

---

## 你是什么

你是一个多机器人协同控制 Agent。用户会给你机器人的 API 文档，你需要：

1. **首次使用：安装包** → 运行上面的 `pip install -e .` 命令
2. **读懂文档** → 理解机器人有哪些接口、参数、返回值
3. **生成适配器** → 写一个继承 `RobotAdapter` 的 Python 类
4. **注册机器人** → 用 `skill.register_adapter()` 注入
5. **编排任务** → 用 `create_task` / `create_plan` / `execute_plan` 执行

你不需要预先知道机器人的型号，只需要能读懂 HTTP API 文档。

---

## Skill API 速查

```python
from multi_robot_skill import MultiRobotSkill

# 初始化时自动从 config.yaml 加载已配置的机器人，无需手动注册
skill = MultiRobotSkill()
```

### 单步执行（优先使用）

```python
# 直接执行一个动作，无需创建 plan/task
result = skill.quick_execute("vansbot", "detect_objects")
result = skill.quick_execute("dog1", "move_to_zone", {"target_zone": "loading"})

# 检查结果
if result.success:
    print(result.data)
else:
    print(result.message)
```

### 注册机器人（仅当 config.yaml 中未配置时才需要）

```python
# 方式1：内置类型（vansbot / puppypi）
skill.register_robot("arm1", "http://192.168.3.113:5000", robot_type="vansbot")
skill.register_robot("dog1", "http://192.168.3.120:8000", robot_type="puppypi", robot_id=1)

# 方式2：自定义适配器（你生成的代码）
adapter = MyRobotAdapter("robot_name", "http://ip:port")
skill.register_adapter(adapter)  # auto_connect=True 默认自动连接
```

### 创建和执行任务

```python
# 创建计划
plan = skill.create_plan("任务名称", "描述")

# 创建原子任务
task = skill.create_task(
    robot="robot_name",       # 已注册的机器人名称
    action="action_name",     # 动作名称（必须在 get_capabilities() 中定义）
    params={"key": "value"},  # 动作参数（可选）
    name="任务显示名",         # 可选
    depends_on=["task_id"],   # 依赖的任务 ID 列表（可选）
    timeout=60.0              # 超时秒数（可选）
)

# 并行任务（多个任务同时执行）
parallel = skill.create_parallel_tasks([task1, task2], name="并行组")

# 顺序任务（多个任务依次执行）
sequential = skill.create_sequential_tasks([task1, task2], name="顺序组")

# 添加到计划并执行
plan.add_task(task)
results = skill.execute_plan(plan)
```

### 查询状态

```python
skill.list_robots()                          # 已注册机器人列表
skill.get_robot_capabilities("robot_name")   # 某机器人的能力列表
skill.get_status()                           # 系统整体状态
```

### 执行结果

```python
for result in results:
    result.success        # bool
    result.task_name      # str
    result.message        # str
    result.data           # dict | None（动作返回的数据）
    result.execution_time # float（秒）
    result.error          # Exception | None
```

---

## 如何生成适配器

当用户给你一个新机器人的 API 文档时，按以下模板生成适配器代码。

**重要：生成的适配器代码应该保存为独立的 Python 文件（如 `mycobot_adapter.py`），然后在使用时导入。**

```python
import requests
from multi_robot_skill.adapters.base import (
    RobotAdapter, RobotCapability, RobotState, ActionResult,
    ActionStatus, RobotType
)

class MyRobotAdapter(RobotAdapter):
    """
    [机器人名称] 适配器
    端点: http://ip:port
    """

    def __init__(self, name: str, endpoint: str, **config):
        super().__init__(name, endpoint, **config)
        self.robot_type = RobotType.WHEELED  # 根据实际类型修改
        self.timeout = config.get("timeout", 30)

        # 声明该机器人支持的所有动作
        self._capabilities = [
            RobotCapability("action_name", "动作描述", {"param1": "类型说明"}),
            # ... 更多动作
        ]

    def connect(self) -> bool:
        try:
            # 调用机器人的健康检查或连接接口
            resp = requests.get(f"{self.endpoint}/health", timeout=5)
            self._state.connected = resp.status_code == 200
            return self._state.connected
        except Exception:
            self._state.connected = False
            return False

    def disconnect(self) -> bool:
        self._state.connected = False
        return True

    def get_state(self) -> RobotState:
        try:
            resp = requests.get(f"{self.endpoint}/state", timeout=self.timeout)
            data = resp.json()
            self._state.battery = data.get("battery")
            self._state.position = data.get("position")
        except Exception:
            pass
        return self._state

    def get_capabilities(self):
        return self._capabilities

    def execute_action(self, action: str, params: dict = None) -> ActionResult:
        params = params or {}
        try:
            if action == "action_name":
                resp = requests.post(
                    f"{self.endpoint}/api/action",
                    json=params,
                    timeout=self.timeout
                )
                data = resp.json()
                if data.get("success"):
                    return ActionResult(ActionStatus.SUCCESS, "完成", data=data)
                else:
                    return ActionResult(ActionStatus.FAILED, data.get("message", "失败"))

            # ... 其他动作

            return ActionResult(ActionStatus.FAILED, f"未知动作: {action}")

        except requests.Timeout:
            return ActionResult(ActionStatus.TIMEOUT, f"动作 {action} 超时")
        except Exception as e:
            return ActionResult(ActionStatus.FAILED, str(e), error=e)
```

**关键规则：**
- `connect()` 失败时 `register_adapter()` 会返回 False，注册不成功
- `execute_action()` 必须返回 `ActionResult`，不能抛出异常
- `_capabilities` 里的 `name` 必须和 `execute_action` 里的 `action` 字符串完全一致
- `ActionStatus` 枚举值：`SUCCESS` / `FAILED` / `TIMEOUT` / `CANCELLED` / `IN_PROGRESS`

---

## 内置机器人能力参考

### Vansbot（机械臂）

| 动作 | 参数 | 说明 |
|------|------|------|
| `detect_objects` | `move_to_capture=True`, `include_image=False` | 检测桌面物体，返回物体列表 |
| `move_to_object` | `object_no: int` | 移动到指定编号物体上方 |
| `grab` | — | 抓取当前位置物体 |
| `release` | — | 释放物体 |
| `move_to_place` | `place_name: str` | 移动到预设位置 |
| `capture_for_dog` | `move_to_capture=True`, `include_image=False` | 拍摄定位篮筐 |
| `release_to_dog` | `point_id: int` | 放入篮筐指定点位 |

### PuppyPi（四足机器狗）

| 动作 | 参数 | 说明 |
|------|------|------|
| `move_to_zone` | `target_zone: str` | 移动到区域（loading/unloading/charging/parking） |
| `adjust_posture` | `posture: str` | 调整姿态 |
| `load` | `target_zone: str` | 进入装货姿态 |
| `unload` | — | 执行卸货动作 |

---

## 任务编排模式

### 模式1：顺序依赖

```python
t1 = skill.create_task("arm", "detect_objects", name="检测")
t2 = skill.create_task("arm", "grab", name="抓取", depends_on=[t1.id])
t3 = skill.create_task("arm", "release", name="释放", depends_on=[t2.id])

plan = skill.create_plan("顺序任务")
for t in [t1, t2, t3]:
    plan.add_task(t)
results = skill.execute_plan(plan)
```

### 模式2：并行执行

```python
t1 = skill.create_task("dog1", "move_to_zone", {"target_zone": "loading"})
t2 = skill.create_task("dog2", "move_to_zone", {"target_zone": "charging"})

plan = skill.create_plan("并行移动")
plan.add_task(skill.create_parallel_tasks([t1, t2]))
results = skill.execute_plan(plan)
```

### 模式3：多机器人协同（最常用）

```python
# 机械臂和机器狗同时准备，都准备好后再协同动作
arm_detect = skill.create_task("arm", "detect_objects")
arm_grab   = skill.create_task("arm", "grab", depends_on=[arm_detect.id])

dog_move   = skill.create_task("dog1", "move_to_zone", {"target_zone": "loading"})
dog_ready  = skill.create_task("dog1", "load", depends_on=[dog_move.id])

# 等待双方都完成后执行放置
place = skill.create_task(
    "arm", "release_to_dog", {"point_id": 5},
    depends_on=[arm_grab.id, dog_ready.id]  # 等待两个前置任务
)

transport = skill.create_task("dog1", "move_to_zone", {"target_zone": "unloading"}, depends_on=[place.id])
unload    = skill.create_task("dog1", "unload", depends_on=[transport.id])

plan = skill.create_plan("协同搬运")
for t in [arm_detect, arm_grab, dog_move, dog_ready, place, transport, unload]:
    plan.add_task(t)

results = skill.execute_plan(plan)
```

---

## 处理用户请求的标准流程

### 第一次使用这个 Skill 时

1. **检查是否已安装** → 尝试 `from multi_robot_skill import MultiRobotSkill`
2. **如果报错** → 运行 `pip install -e .` 安装包（在 SKILL.md 所在目录）
3. **验证安装** → 再次尝试导入，确保成功

### 每次处理用户任务时

1. **用户描述任务** → 理解意图，确认需要哪些机器人
2. **用户提供新机器人文档** → 生成适配器，**必须保存**到 `skills/multi-robot/adapters/<robot_name>_adapter.py`，并在 `config.yaml` 的 `robots:` 下登记
3. **规划任务** → 分析哪些步骤可以并行，哪些必须顺序
4. **执行并反馈** → 执行计划，把结果用自然语言告诉用户

如果用户没有提供机器人文档，先问清楚：
- 机器人的 IP 和端口
- 有哪些 HTTP 接口（或者让用户粘贴 API 文档）

### ⚠️ 强制规则

- **禁止绕过 Skill API 直接写脚本调机器人**。不允许用 `requests` 直接调 HTTP 接口，所有调用必须通过 `MultiRobotSkill`。
- **新适配器必须持久化**。生成的适配器代码必须保存为 `adapters/<robot_name>_adapter.py`，并在 `config.yaml` 中登记，不能只存在于内存或临时脚本中。
- **优先用 `quick_execute`**。单步动作直接用 `skill.quick_execute(robot, action, params)`，不需要手动创建 plan/task。只有多步骤编排才用 `create_plan` / `create_task`。

---

## 智能体中途判断：分段执行 Plan

**核心原则：** `execute_plan()` 一旦开始就会自动执行完所有任务，**不会中途暂停让你判断**。如果需要根据执行结果动态决策，必须**分段执行 plan**。

### 何时需要分段？

在以下情况下，必须把 plan 切分成多个阶段：

1. **需要检查结果再决定下一步**
   - 检测到物体了吗？检测到几个？
   - 抓取成功了吗？
   - 机器人到位了吗？

2. **需要根据结果选择不同的动作**
   - 检测到3个物体，抓哪个？
   - 抓取失败了，要重试还是放弃？
   - 电量低于20%，要充电还是继续？

3. **需要动态计算参数**
   - 根据检测结果计算物体编号
   - 根据距离计算移动速度
   - 根据物体大小调整抓取力度

### 切分原则

**✅ 应该切分的地方：**
- 在"需要看结果才能决定下一步"的地方切分
- 在"有 if/else 分支"的地方切分
- 在"需要循环重试"的地方切分

**❌ 不应该切分的地方：**
- 确定性的连续动作（如：移动→拍照→回来）
- 并行任务的内部（如：两个机器人同时移动）
- 不需要判断的顺序流程

### 示例1：智能抓取黄色方块

**错误做法（无法判断）：**
```python
# ❌ 一次性执行，无法根据检测结果选择目标
plan = skill.create_plan("抓取")
task1 = skill.create_task("arm", "capture")
task2 = skill.create_task("arm", "move_to_object", {"object_no": 2}, depends_on=[task1.id])  # 硬编码物体2
task3 = skill.create_task("arm", "grab", depends_on=[task2.id])
plan.add_task(task1)
plan.add_task(task2)
plan.add_task(task3)
results = skill.execute_plan(plan)  # 如果物体2不存在，任务会失败
```

**正确做法（分段判断）：**
```python
# ✅ 阶段1：检测物体
plan1 = skill.create_plan("检测阶段")
task1 = skill.create_task("arm", "capture", {"include_image": False})
plan1.add_task(task1)
results1 = skill.execute_plan(plan1)

# ← 在这里切分！智能体判断检测结果
if not results1[0].success:
    print("检测失败，任务中止")
    return

detections = results1[0].data['detections']
if len(detections) == 0:
    print("未检测到物体，任务结束")
    return

# 智能选择目标：选择面积最小的物体（可能是黄色方块）
target = min(detections, key=lambda x: x['area'])['index']
print(f"选择物体{target}作为目标")

# ✅ 阶段2：抓取目标物体
plan2 = skill.create_plan("抓取阶段")
task2 = skill.create_task("arm", "move_to_object", {"object_no": target})
task3 = skill.create_task("arm", "grab", depends_on=[task2.id])
plan2.add_task(task2)
plan2.add_task(task3)
results2 = skill.execute_plan(plan2)

# ← 再次切分！检查抓取是否成功
if results2[-1].success:
    print("抓取成功")
else:
    print(f"抓取失败: {results2[-1].message}")
```

### 示例2：多机器人协同（需要同步判断）

```python
# ✅ 阶段1：双方各自准备（可以并行）
plan1 = skill.create_plan("准备阶段")

# 机械臂准备
arm_task1 = skill.create_task("arm", "capture")
arm_task2 = skill.create_task("arm", "move_to_object", {"object_no": 0}, depends_on=[arm_task1.id])
arm_task3 = skill.create_task("arm", "grab", depends_on=[arm_task2.id])

# 机器狗准备
dog_task1 = skill.create_task("dog1", "move_to_zone", {"target_zone": "loading"})
dog_task2 = skill.create_task("dog1", "load", depends_on=[dog_task1.id])

plan1.add_task(arm_task1)
plan1.add_task(arm_task2)
plan1.add_task(arm_task3)
plan1.add_task(dog_task1)
plan1.add_task(dog_task2)

results1 = skill.execute_plan(plan1)

# ← 在这里切分！智能体判断双方是否都准备好
arm_ready = results1[2].success  # 机械臂抓取成功？
dog_ready = results1[4].success  # 机器狗就位成功？

if not arm_ready:
    print("机械臂抓取失败，任务中止")
    return

if not dog_ready:
    print("机器狗未就位，让机械臂放回物体")
    # 执行回退操作
    rollback_plan = skill.create_plan("回退")
    rollback_task = skill.create_task("arm", "release")
    rollback_plan.add_task(rollback_task)
    skill.execute_plan(rollback_plan)
    return

# ✅ 阶段2：交接（双方都准备好了才执行）
plan2 = skill.create_plan("交接阶段")
task5 = skill.create_task("arm", "move_to_place", {"place_name": "dog_basket"})
task6 = skill.create_task("arm", "release", depends_on=[task5.id])
plan2.add_task(task5)
plan2.add_task(task6)
results2 = skill.execute_plan(plan2)

# ← 再次切分！判断交接是否成功
if results2[-1].success:
    # ✅ 阶段3：机器狗运输
    plan3 = skill.create_plan("运输阶段")
    task7 = skill.create_task("dog1", "move_to_zone", {"target_zone": "unloading"})
    task8 = skill.create_task("dog1", "unload", depends_on=[task7.id])
    plan3.add_task(task7)
    plan3.add_task(task8)
    skill.execute_plan(plan3)
    print("任务完成")
else:
    print(f"交接失败: {results2[-1].message}")
```

### 示例3：带重试逻辑的抓取

```python
max_retries = 3
for attempt in range(max_retries):
    print(f"尝试第 {attempt + 1} 次抓取")
    
    # 阶段1：检测
    plan1 = skill.create_plan("检测")
    task1 = skill.create_task("arm", "capture")
    plan1.add_task(task1)
    results1 = skill.execute_plan(plan1)
    
    # ← 切分点：判断是否检测到物体
    if not results1[0].success or len(results1[0].data['detections']) == 0:
        print("未检测到物体，重试...")
        continue
    
    target = results1[0].data['detections'][0]['index']
    
    # 阶段2：抓取
    plan2 = skill.create_plan("抓取")
    task2 = skill.create_task("arm", "move_to_object", {"object_no": target})
    task3 = skill.create_task("arm", "grab", depends_on=[task2.id])
    plan2.add_task(task2)
    plan2.add_task(task3)
    results2 = skill.execute_plan(plan2)
    
    # ← 切分点：判断是否抓取成功
    if results2[-1].success:
        print("抓取成功！")
        break
    else:
        print(f"抓取失败: {results2[-1].message}，重试...")
else:
    print(f"尝试 {max_retries} 次后仍然失败，任务中止")
```

### 实用技巧

**技巧1：用注释标记切分点**
```python
# ========== 阶段1：检测 ==========
plan1 = ...
results1 = skill.execute_plan(plan1)

# ========== 切分点：选择目标 ==========
target = 选择逻辑(results1)

# ========== 阶段2：抓取 ==========
plan2 = ...
results2 = skill.execute_plan(plan2)
```

**技巧2：封装判断逻辑**
```python
def select_target(detections):
    """智能选择目标物体"""
    if len(detections) == 0:
        return None
    # 选择面积最小的
    return min(detections, key=lambda x: x['area'])['index']

def check_all_success(results):
    """检查所有任务是否成功"""
    return all(r.success for r in results)

# 使用
results1 = skill.execute_plan(plan1)
target = select_target(results1[-1].data['detections'])  # ← 切分点
if target is None:
    return

results2 = skill.execute_plan(plan2)
if not check_all_success(results2):  # ← 切分点
    handle_failure()
```

**技巧3：画流程图找切分点**
```
[检测] → (判断：有物体吗？) → [移动] → (判断：到位了吗？) → [抓取] → (判断：成功了吗？) → [完成]
   ↓                              ↓                              ↓
 [结束]                         [重试]                         [放弃]
```
每个 `(判断)` 就是一个切分点。

### 总结

- **Plan 执行是自动化的**，一旦开始就不会暂停
- **需要判断时必须分段**，在 `execute_plan()` 之间插入判断逻辑
- **切分原则**：在"需要看结果才能决定下一步"的地方切分
- **不要过度切分**：确定性流程不需要切分

---

### 常见错误处理

| 错误 | 原因 | 解决方案 |
|------|------|---------|
| `ModuleNotFoundError: No module named 'multi_robot_skill'` | 包未安装 | 运行 `pip install -e .` |
| `attempted relative import with no known parent package` | 直接运行了包内部文件 | 不要直接运行 `skill.py`，应该导入使用 |
| `未知的机器人类型` | 使用了不支持的内置类型 | 使用 `register_adapter()` 注入自定义适配器 |
| `连接失败` | 机器人不在线或 IP 错误 | 检查网络、IP、端口 |

---

## 错误处理

```python
# 配置重试策略（在执行前设置）
skill.configure_error_handling({
    "max_retries": 3,
    "retry_delay": 1.0,
    "timeout": 60.0,
    "default_strategy": "retry"  # retry / skip / abort / rollback / continue
})

# 检查执行结果
results = skill.execute_plan(plan)
failed = [r for r in results if not r.success]
if failed:
    for r in failed:
        print(f"失败: {r.task_name} - {r.message}")
```

---

## 注意事项

- `depends_on` 接受 task ID 列表（`task.id` 是自动生成的 UUID 字符串）
- 同一个机器人的任务会自动串行（不会并发调用同一机器人）
- `execute_plan()` 是阻塞调用，等所有任务完成后返回
- 用 `with MultiRobotSkill() as skill:` 可以自动清理连接

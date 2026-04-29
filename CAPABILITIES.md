# Robot Capabilities

*自动生成于: 2026-04-29 18:01:20*

本文档列出了所有已配置机器人的能力。

---

## 目录

- [mycobot_arm](#mycobot_arm)

---

## mycobot_arm

**类型**: manipulator

**端点**: `http://192.168.50.120:5000`

**状态**: ✓ 在线

### 可用动作 (11 个)

#### `capture`

捕获图像并检测物体，返回检测到的物体列表

**参数:**

| 参数名 | 说明 |
|--------|------|
| `move_to_capture` | bool (默认true) |
| `include_image` | bool (默认false) |

**CLI 示例:**

```bash
python cli.py execute mycobot_arm capture move_to_capture=true include_image=true
```

#### `get_detections`

获取最近一次捕获的物体检测数据

*无参数*

**CLI 示例:**

```bash
python cli.py execute mycobot_arm get_detections
```

#### `describe_image`

使用VLM描述最新标注图像

*无参数*

**CLI 示例:**

```bash
python cli.py execute mycobot_arm describe_image
```

#### `move_to_object`

移动机械臂到指定检测物体位置

**参数:**

| 参数名 | 说明 |
|--------|------|
| `object_no` | int (必需，物体索引) |
| `speed` | int (可选，移动速度) |

**CLI 示例:**

```bash
python cli.py execute mycobot_arm move_to_object object_no=0 speed=50
```

#### `move_to_place`

移动机械臂到预定义命名位置

**参数:**

| 参数名 | 说明 |
|--------|------|
| `place_name` | str (必需: capture/drop/dog_basket) |
| `speed` | int (可选) |

**CLI 示例:**

```bash
python cli.py execute mycobot_arm move_to_place place_name=example speed=50
```

#### `grab`

抓取物体（启动吸盘）

**参数:**

| 参数名 | 说明 |
|--------|------|
| `speed` | int (可选) |

**CLI 示例:**

```bash
python cli.py execute mycobot_arm grab speed=50
```

#### `release`

释放物体（关闭吸盘）

**参数:**

| 参数名 | 说明 |
|--------|------|
| `speed` | int (可选) |

**CLI 示例:**

```bash
python cli.py execute mycobot_arm release speed=50
```

#### `head_shake`

执行摇头动作

*无参数*

**CLI 示例:**

```bash
python cli.py execute mycobot_arm head_shake
```

#### `head_dance`

执行舞蹈动作

*无参数*

**CLI 示例:**

```bash
python cli.py execute mycobot_arm head_dance
```

#### `head_nod`

执行点头动作

*无参数*

**CLI 示例:**

```bash
python cli.py execute mycobot_arm head_nod
```

#### `hit`

执行击打动作

*无参数*

**CLI 示例:**

```bash
python cli.py execute mycobot_arm hit
```

---

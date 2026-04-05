"""
MyCobot 机械臂使用示例

这个示例展示如何使用 multi_robot_skill 控制 MyCobot 机械臂。
"""

import sys
import os

# 添加项目根目录到 Python 路径（如果未安装包）
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from multi_robot_skill import MultiRobotSkill, RobotAdapter, RobotCapability, ActionResult, RobotType, ActionStatus
import requests
from typing import Dict, Any, List


class MyCobotAdapter(RobotAdapter):
    """
    MyCobot 机械臂适配器

    根据你提供的 API 文档自动生成的适配器。
    """

    def __init__(self, name: str, endpoint: str, **config):
        """
        初始化 MyCobot 适配器

        Args:
            name: 机器人名称
            endpoint: API 端点 (例如: http://192.168.1.100:5000)
            **config: 其他配置参数
        """
        super().__init__(name, endpoint, RobotType.MANIPULATOR, **config)
        self.timeout = config.get('timeout', 30)

    def connect(self) -> bool:
        """连接到 MyCobot"""
        try:
            # 测试连接
            response = requests.get(f"{self.endpoint}/api/status", timeout=5)
            return response.status_code == 200
        except Exception as e:
            self.logger.error(f"连接失败: {e}")
            return False

    def disconnect(self) -> bool:
        """断开连接"""
        return True

    def execute_action(self, action: str, params: Dict[str, Any]) -> ActionResult:
        """
        执行动作

        支持的动作:
        - move_to: 移动到指定位置
        - grab: 抓取
        - release: 释放
        - home: 回到初始位置
        """
        try:
            if action == "move_to":
                return self._move_to(params)
            elif action == "grab":
                return self._grab(params)
            elif action == "release":
                return self._release(params)
            elif action == "home":
                return self._home()
            else:
                return ActionResult(
                    success=False,
                    message=f"未知动作: {action}",
                    status=ActionStatus.FAILED
                )
        except Exception as e:
            self.logger.error(f"执行动作失败: {action}, 错误: {e}")
            return ActionResult(
                success=False,
                message=str(e),
                status=ActionStatus.ERROR
            )

    def _move_to(self, params: Dict[str, Any]) -> ActionResult:
        """移动到指定位置"""
        # 根据你的 API 文档调整
        response = requests.post(
            f"{self.endpoint}/api/move",
            json=params,
            timeout=self.timeout
        )

        if response.status_code == 200:
            return ActionResult(
                success=True,
                message="移动成功",
                status=ActionStatus.COMPLETED,
                data=response.json()
            )
        else:
            return ActionResult(
                success=False,
                message=f"移动失败: {response.text}",
                status=ActionStatus.FAILED
            )

    def _grab(self, params: Dict[str, Any]) -> ActionResult:
        """抓取"""
        response = requests.post(
            f"{self.endpoint}/api/grab",
            json=params,
            timeout=self.timeout
        )

        if response.status_code == 200:
            return ActionResult(
                success=True,
                message="抓取成功",
                status=ActionStatus.COMPLETED
            )
        else:
            return ActionResult(
                success=False,
                message=f"抓取失败: {response.text}",
                status=ActionStatus.FAILED
            )

    def _release(self, params: Dict[str, Any]) -> ActionResult:
        """释放"""
        response = requests.post(
            f"{self.endpoint}/api/release",
            json=params,
            timeout=self.timeout
        )

        if response.status_code == 200:
            return ActionResult(
                success=True,
                message="释放成功",
                status=ActionStatus.COMPLETED
            )
        else:
            return ActionResult(
                success=False,
                message=f"释放失败: {response.text}",
                status=ActionStatus.FAILED
            )

    def _home(self) -> ActionResult:
        """回到初始位置"""
        response = requests.post(
            f"{self.endpoint}/api/home",
            timeout=self.timeout
        )

        if response.status_code == 200:
            return ActionResult(
                success=True,
                message="归位成功",
                status=ActionStatus.COMPLETED
            )
        else:
            return ActionResult(
                success=False,
                message=f"归位失败: {response.text}",
                status=ActionStatus.FAILED
            )

    def get_state(self) -> Dict[str, Any]:
        """获取机器人状态"""
        try:
            response = requests.get(f"{self.endpoint}/api/status", timeout=5)
            if response.status_code == 200:
                return response.json()
            return {"error": "无法获取状态"}
        except Exception as e:
            return {"error": str(e)}

    def get_capabilities(self) -> List[RobotCapability]:
        """获取机器人能力"""
        return [
            RobotCapability(
                name="move_to",
                description="移动到指定位置",
                parameters={
                    "x": "X 坐标",
                    "y": "Y 坐标",
                    "z": "Z 坐标"
                }
            ),
            RobotCapability(
                name="grab",
                description="抓取物体",
                parameters={}
            ),
            RobotCapability(
                name="release",
                description="释放物体",
                parameters={}
            ),
            RobotCapability(
                name="home",
                description="回到初始位置",
                parameters={}
            ),
        ]


def main():
    """主函数 - 使用示例"""

    # 1. 初始化 Skill
    print("初始化 Multi-Robot Skill...")
    skill = MultiRobotSkill()

    # 2. 创建并注册 MyCobot 适配器
    print("\n注册 MyCobot 机械臂...")
    mycobot_endpoint = "http://192.168.1.100:5000"  # 修改为你的实际 IP
    mycobot = MyCobotAdapter("mycobot", mycobot_endpoint)

    if skill.register_adapter(mycobot):
        print("✓ MyCobot 注册成功")
    else:
        print("✗ MyCobot 注册失败")
        return

    # 3. 创建任务计划
    print("\n创建任务计划...")
    plan = skill.create_plan("MyCobot 测试任务")

    # 4. 添加任务
    print("添加任务...")

    # 任务 1: 移动到位置 A
    task1 = skill.create_task(
        robot="mycobot",
        action="move_to",
        params={"x": 100, "y": 200, "z": 150},
        name="移动到位置 A"
    )
    plan.add_task(task1)

    # 任务 2: 抓取
    task2 = skill.create_task(
        robot="mycobot",
        action="grab",
        name="抓取物体",
        depends_on=[task1.id]
    )
    plan.add_task(task2)

    # 任务 3: 移动到位置 B
    task3 = skill.create_task(
        robot="mycobot",
        action="move_to",
        params={"x": 300, "y": 200, "z": 150},
        name="移动到位置 B",
        depends_on=[task2.id]
    )
    plan.add_task(task3)

    # 任务 4: 释放
    task4 = skill.create_task(
        robot="mycobot",
        action="release",
        name="释放物体",
        depends_on=[task3.id]
    )
    plan.add_task(task4)

    # 任务 5: 回到初始位置
    task5 = skill.create_task(
        robot="mycobot",
        action="home",
        name="回到初始位置",
        depends_on=[task4.id]
    )
    plan.add_task(task5)

    # 5. 执行计划
    print("\n执行任务计划...")
    print("=" * 60)

    try:
        results = skill.execute_plan(plan)

        # 6. 显示结果
        print("\n任务执行结果:")
        print("=" * 60)
        for i, result in enumerate(results, 1):
            status = "✓" if result.success else "✗"
            print(f"{status} 任务 {i}: {result.message}")
            if result.data:
                print(f"   数据: {result.data}")

        print("=" * 60)
        print("所有任务执行完成！")

    except Exception as e:
        print(f"\n执行失败: {e}")

    finally:
        # 7. 清理
        skill.shutdown()


if __name__ == "__main__":
    main()

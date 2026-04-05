"""
快速启动脚本 - 无需安装即可使用

这个脚本会自动处理 Python 路径问题，让你可以直接运行示例。
"""

import sys
import os

# 自动添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 现在可以导入了
from multi_robot_skill import MultiRobotSkill

def main():
    """快速启动示例"""
    print("=" * 60)
    print("Multi-Robot Skill - 快速启动")
    print("=" * 60)

    # 初始化 Skill
    print("\n1. 初始化 Skill...")
    skill = MultiRobotSkill()
    print("   ✓ Skill 初始化成功")

    # 注册机器人示例
    print("\n2. 注册机器人示例:")
    print("   请根据你的实际情况修改以下代码：")
    print()
    print("   # 注册 MyCobot 机械臂")
    print("   skill.register_robot('mycobot', 'http://192.168.1.100:5000')")
    print()
    print("   # 注册第二个机器人")
    print("   skill.register_robot('robot2', 'http://192.168.1.101:5000')")
    print()

    # 显示使用方法
    print("\n3. 使用方法:")
    print("   # 创建任务计划")
    print("   plan = skill.create_plan('测试任务')")
    print()
    print("   # 添加任务")
    print("   task1 = skill.create_task('mycobot', 'move_to', {'x': 100, 'y': 200})")
    print("   plan.add_task(task1)")
    print()
    print("   # 执行计划")
    print("   results = skill.execute_plan(plan)")
    print()

    # 显示自定义适配器方法
    print("\n4. 如果你的机器人不是内置类型，需要创建自定义适配器:")
    print("   参考 adapters/base.py 中的 RobotAdapter 基类")
    print("   或者让 AI Agent 根据你的机器人 API 文档自动生成")
    print()

    print("=" * 60)
    print("准备就绪！现在你可以开始使用 Multi-Robot Skill 了")
    print("=" * 60)

    return skill

if __name__ == "__main__":
    skill = main()

    # 保持 skill 对象可用，方便交互式使用
    print("\n提示: skill 对象已创建，你可以在交互式环境中使用它")
    print("例如: skill.register_robot('mycobot', 'http://192.168.1.100:5000')")

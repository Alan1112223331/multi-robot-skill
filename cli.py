#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Multi-Robot Skill CLI 工具

用法:
    python cli.py list                              # 列出所有机器人
    python cli.py capabilities <robot_name>         # 查看机器人能力
    python cli.py execute <robot_name> <action> [params...]  # 执行动作
    
示例:
    python cli.py list
    python cli.py capabilities mycobot_arm
    python cli.py execute mycobot_arm head_nod
    python cli.py execute mycobot_arm move_to_place --place_name capture --speed 50
"""

import sys
import os
import argparse
import json
from typing import Dict, Any

# 设置 UTF-8 输出（Windows 兼容）
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 添加 skills 父目录到 Python 路径
skills_parent = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, skills_parent)

from multi_robot_skill.skill import MultiRobotSkill


def format_table(headers, rows):
    """格式化表格输出"""
    # 计算每列的最大宽度
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))
    
    # 打印表头
    header_line = " | ".join(h.ljust(w) for h, w in zip(headers, col_widths))
    print(header_line)
    print("-" * len(header_line))
    
    # 打印数据行
    for row in rows:
        print(" | ".join(str(cell).ljust(w) for cell, w in zip(row, col_widths)))


def cmd_list(skill: MultiRobotSkill, args):
    """列出所有机器人"""
    robots = skill.list_robots()
    
    if args.json:
        print(json.dumps({"robots": robots}, indent=2, ensure_ascii=False))
        return
    
    if not robots:
        print("没有找到任何机器人配置")
        return
    
    print(f"\n找到 {len(robots)} 个机器人:\n")
    
    # 获取每个机器人的详细信息
    rows = []
    for robot_name in robots:
        adapter = skill.coordinator.robots.get(robot_name)
        if adapter:
            robot_type = adapter.robot_type.value if hasattr(adapter.robot_type, 'value') else str(adapter.robot_type)
            endpoint = adapter.endpoint
            connected = "✓" if adapter._state.connected else "✗"
            rows.append([robot_name, robot_type, endpoint, connected])
    
    format_table(["机器人名称", "类型", "端点", "连接"], rows)
    print()


def cmd_capabilities(skill: MultiRobotSkill, args):
    """查看机器人能力"""
    robot_name = args.robot_name
    robots = skill.list_robots()
    
    if robot_name not in robots:
        print(f"错误: 机器人 '{robot_name}' 不存在")
        print(f"可用的机器人: {', '.join(robots)}")
        sys.exit(1)
    
    adapter = skill.coordinator.robots.get(robot_name)
    if not adapter:
        print(f"错误: 无法获取机器人 '{robot_name}' 的适配器")
        sys.exit(1)
    
    capabilities = adapter.get_capabilities()
    
    if args.json:
        caps_data = [
            {
                "name": cap.name,
                "description": cap.description,
                "parameters": cap.parameters
            }
            for cap in capabilities
        ]
        print(json.dumps({
            "robot": robot_name,
            "capabilities": caps_data
        }, indent=2, ensure_ascii=False))
        return
    
    print(f"\n机器人: {robot_name}")
    print(f"类型: {adapter.robot_type.value if hasattr(adapter.robot_type, 'value') else str(adapter.robot_type)}")
    print(f"端点: {adapter.endpoint}")
    print(f"\n可用动作 ({len(capabilities)} 个):\n")
    
    for cap in capabilities:
        print(f"  • {cap.name}")
        print(f"    {cap.description}")
        if cap.parameters:
            print(f"    参数: {cap.parameters}")
        print()


def cmd_execute(skill: MultiRobotSkill, args):
    """执行机器人动作"""
    robot_name = args.robot_name
    action = args.action
    
    # 检查机器人是否存在
    robots = skill.list_robots()
    if robot_name not in robots:
        print(f"错误: 机器人 '{robot_name}' 不存在")
        print(f"可用的机器人: {', '.join(robots)}")
        sys.exit(1)
    
    # 解析参数
    params = {}
    if args.params:
        for param in args.params:
            if '=' not in param:
                print(f"错误: 参数格式错误 '{param}'，应该是 key=value")
                sys.exit(1)
            key, value = param.split('=', 1)
            # 尝试解析为 JSON（支持数字、布尔值等）
            try:
                params[key] = json.loads(value)
            except json.JSONDecodeError:
                # 如果不是有效的 JSON，就当作字符串
                params[key] = value
    
    # 执行动作
    print(f"执行: {robot_name}.{action}({params})")
    print()
    
    result = skill.quick_execute(robot_name, action, params)
    
    if args.json:
        print(json.dumps({
            "success": result.success,
            "message": result.message,
            "execution_time": result.execution_time,
            "data": result.data,
            "error": str(result.error) if result.error else None
        }, indent=2, ensure_ascii=False))
        return
    
    if result.success:
        print(f"✓ 成功: {result.message}")
        print(f"  耗时: {result.execution_time:.2f}秒")
        if result.data:
            print(f"  数据: {json.dumps(result.data, indent=2, ensure_ascii=False)}")
    else:
        print(f"✗ 失败: {result.message}")
        if result.error:
            print(f"  错误: {result.error}")
        sys.exit(1)


def cmd_run(skill: MultiRobotSkill, args):
    """执行 JSON 任务配置文件"""
    task_file = args.task_file
    
    # 读取 JSON 文件
    if not os.path.exists(task_file):
        print(f"错误: 文件不存在 '{task_file}'")
        sys.exit(1)
    
    try:
        with open(task_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        print(f"错误: JSON 格式错误: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"错误: 读取文件失败: {e}")
        sys.exit(1)
    
    # 验证配置格式
    if 'tasks' not in config:
        print("错误: JSON 配置缺少 'tasks' 字段")
        sys.exit(1)
    
    tasks = config['tasks']
    mode = config.get('mode', 'sequential')  # sequential / parallel
    
    if not isinstance(tasks, list) or len(tasks) == 0:
        print("错误: 'tasks' 必须是非空数组")
        sys.exit(1)
    
    print(f"加载任务配置: {task_file}")
    print(f"任务数量: {len(tasks)}")
    print(f"执行模式: {mode}")
    print()
    
    # 创建任务计划
    from multi_robot_skill.core.task_planner import TaskPlanner, Task, TaskType, TaskPlan
    
    planner = TaskPlanner()
    plan = TaskPlan(
        name=config.get('description', 'Task Plan'),
        description=config.get('description', '')
    )
    
    for i, task_config in enumerate(tasks):
        # 验证任务配置
        if 'robot' not in task_config or 'action' not in task_config:
            print(f"错误: 任务 {i} 缺少 'robot' 或 'action' 字段")
            sys.exit(1)
        
        robot_name = task_config['robot']
        action = task_config['action']
        params = task_config.get('params', {})
        depends_on = task_config.get('depends_on', [])
        
        # 创建任务对象
        task = Task(
            id=f"task_{i}",
            name=f"{robot_name}.{action}",
            robot=robot_name,
            action=action,
            params=params,
            task_type=TaskType.ATOMIC,
            depends_on=depends_on
        )
        plan.add_task(task)
        
        print(f"  [{i}] {robot_name}.{action}({params})")
        if depends_on:
            print(f"      依赖: {depends_on}")
    
    print()
    
    # 执行计划
    print("开始执行任务...")
    print()
    
    results = skill.coordinator.execute_plan(plan)
    
    # 输出结果
    if args.json:
        results_data = [r.to_dict() for r in results]
        print(json.dumps({
            "total": len(results),
            "success": sum(1 for r in results if r.success),
            "failed": sum(1 for r in results if not r.success),
            "results": results_data
        }, indent=2, ensure_ascii=False))
        return
    
    # 统计结果
    success_count = sum(1 for r in results if r.success)
    failed_count = len(results) - success_count
    total_time = sum(r.execution_time for r in results)
    
    print("\n" + "="*60)
    print("执行完成")
    print("="*60)
    print(f"总任务数: {len(results)}")
    print(f"成功: {success_count}")
    print(f"失败: {failed_count}")
    print(f"总耗时: {total_time:.2f}秒")
    print()
    
    # 详细结果
    for i, result in enumerate(results):
        status = "✓" if result.success else "✗"
        print(f"{status} [{i}] {result.task_name}")
        print(f"    消息: {result.message}")
        print(f"    耗时: {result.execution_time:.2f}秒")
        if not result.success and result.error:
            print(f"    错误: {result.error}")
    
    if failed_count > 0:
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Multi-Robot Skill CLI 工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s list
  %(prog)s capabilities mycobot_arm
  %(prog)s execute mycobot_arm head_nod
  %(prog)s execute mycobot_arm move_to_place place_name=capture speed=50
        """
    )
    
    parser.add_argument('--json', action='store_true', help='以 JSON 格式输出')
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # list 命令
    subparsers.add_parser('list', help='列出所有机器人')
    
    # capabilities 命令
    cap_parser = subparsers.add_parser('capabilities', help='查看机器人能力')
    cap_parser.add_argument('robot_name', help='机器人名称')
    
    # execute 命令
    exec_parser = subparsers.add_parser('execute', help='执行机器人动作')
    exec_parser.add_argument('robot_name', help='机器人名称')
    exec_parser.add_argument('action', help='动作名称')
    exec_parser.add_argument('params', nargs='*', help='参数 (格式: key=value)')
    
    # run 命令
    run_parser = subparsers.add_parser('run', help='执行 JSON 任务配置文件')
    run_parser.add_argument('task_file', help='JSON 任务配置文件路径')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # 初始化 Skill
    try:
        skill = MultiRobotSkill()
    except Exception as e:
        print(f"错误: 初始化 MultiRobotSkill 失败: {e}")
        sys.exit(1)
    
    # 执行命令
    if args.command == 'list':
        cmd_list(skill, args)
    elif args.command == 'capabilities':
        cmd_capabilities(skill, args)
    elif args.command == 'execute':
        cmd_execute(skill, args)
    elif args.command == 'run':
        cmd_run(skill, args)


if __name__ == '__main__':
    main()

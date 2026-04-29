#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成 CAPABILITIES.md 文档

自动从 config.yaml 加载所有机器人，并生成能力文档。
"""

import sys
import os
from datetime import datetime

# 设置 UTF-8 输出（Windows 兼容）
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 添加 skills 父目录到 Python 路径
skills_parent = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, skills_parent)

from multi_robot_skill.skill import MultiRobotSkill


def generate_capabilities_md(output_path: str = "CAPABILITIES.md"):
    """生成 CAPABILITIES.md 文档"""
    
    print("初始化 Multi-Robot Skill...")
    skill = MultiRobotSkill()
    
    robots = skill.list_robots()
    
    if not robots:
        print("错误: 没有找到任何机器人配置")
        sys.exit(1)
    
    print(f"找到 {len(robots)} 个机器人")
    print()
    
    # 生成 Markdown 内容
    lines = []
    lines.append("# Robot Capabilities")
    lines.append("")
    lines.append(f"*自动生成于: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
    lines.append("")
    lines.append("本文档列出了所有已配置机器人的能力。")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # 目录
    lines.append("## 目录")
    lines.append("")
    for robot_name in robots:
        lines.append(f"- [{robot_name}](#{robot_name})")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # 每个机器人的详细信息
    for robot_name in robots:
        adapter = skill.coordinator.robots.get(robot_name)
        if not adapter:
            continue
        
        print(f"处理机器人: {robot_name}")
        
        robot_type = adapter.robot_type.value if hasattr(adapter.robot_type, 'value') else str(adapter.robot_type)
        endpoint = adapter.endpoint
        connected = "✓ 在线" if adapter._state.connected else "✗ 离线"
        
        lines.append(f"## {robot_name}")
        lines.append("")
        lines.append(f"**类型**: {robot_type}")
        lines.append("")
        lines.append(f"**端点**: `{endpoint}`")
        lines.append("")
        lines.append(f"**状态**: {connected}")
        lines.append("")
        
        # 获取能力
        capabilities = adapter.get_capabilities()
        
        if capabilities:
            lines.append(f"### 可用动作 ({len(capabilities)} 个)")
            lines.append("")
            
            for cap in capabilities:
                lines.append(f"#### `{cap.name}`")
                lines.append("")
                lines.append(f"{cap.description}")
                lines.append("")
                
                if cap.parameters:
                    lines.append("**参数:**")
                    lines.append("")
                    lines.append("| 参数名 | 说明 |")
                    lines.append("|--------|------|")
                    for param_name, param_desc in cap.parameters.items():
                        lines.append(f"| `{param_name}` | {param_desc} |")
                    lines.append("")
                else:
                    lines.append("*无参数*")
                    lines.append("")
                
                # CLI 使用示例
                lines.append("**CLI 示例:**")
                lines.append("")
                if cap.parameters:
                    # 生成示例参数
                    example_params = []
                    for param_name in cap.parameters.keys():
                        # 简单的参数值推断
                        if 'speed' in param_name.lower():
                            example_params.append(f"{param_name}=50")
                        elif 'name' in param_name.lower():
                            example_params.append(f"{param_name}=example")
                        elif 'no' in param_name.lower() or 'index' in param_name.lower():
                            example_params.append(f"{param_name}=0")
                        elif 'bool' in str(cap.parameters[param_name]).lower():
                            example_params.append(f"{param_name}=true")
                        else:
                            example_params.append(f"{param_name}=value")
                    
                    params_str = " ".join(example_params)
                    lines.append(f"```bash")
                    lines.append(f"python cli.py execute {robot_name} {cap.name} {params_str}")
                    lines.append(f"```")
                else:
                    lines.append(f"```bash")
                    lines.append(f"python cli.py execute {robot_name} {cap.name}")
                    lines.append(f"```")
                lines.append("")
        else:
            lines.append("*无可用动作*")
            lines.append("")
        
        lines.append("---")
        lines.append("")
    
    # 写入文件
    content = "\n".join(lines)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print()
    print(f"✓ 成功生成: {output_path}")
    print(f"  总机器人数: {len(robots)}")
    
    total_actions = sum(
        len(skill.coordinator.robots[name].get_capabilities())
        for name in robots
        if skill.coordinator.robots.get(name)
    )
    print(f"  总动作数: {total_actions}")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description="生成机器人能力文档")
    parser.add_argument('-o', '--output', default='CAPABILITIES.md', help='输出文件路径')
    
    args = parser.parse_args()
    
    generate_capabilities_md(args.output)

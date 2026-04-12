"""
MyCobot 机械臂 + 机械狗群协同示例

演示如何使用两个适配器实现：
1. 机械臂抓取物体
2. 放置到机械狗背篮
3. 机械狗运输到目标点
4. 机械狗卸货
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from multi_robot_skill import MultiRobotSkill
from adapters.mycobot_adapter import MyCobotAdapter
from adapters.dogfleet_adapter import DogFleetAdapter


def delivery_workflow():
    """完整的物流配送工作流程"""
    
    # 初始化 skill
    skill = MultiRobotSkill()
    
    # 注册机械臂
    mycobot = MyCobotAdapter(
        name="mycobot_arm",
        endpoint="http://192.168.50.120:5000"
    )
    skill.register_adapter(mycobot)
    
    # 注册机械狗群（控制0号狗）
    dogfleet = DogFleetAdapter(
        name="dog_0",
        endpoint="http://localhost:8000",
        dog_id=0
    )
    skill.register_adapter(dogfleet)
    
    print("=" * 60)
    print("物流配送工作流程开始")
    print("=" * 60)
    
    # ========== 阶段1: 机械臂抓取物体 ==========
    print("\n[阶段1] 机械臂抓取物体")
    print("-" * 60)
    
    # 1.1 捕获图像并检测物体
    print("1.1 捕获图像...")
    result = skill.quick_execute("mycobot_arm", "capture", {
        "move_to_capture": True,
        "include_image": False
    })
    if not result.success:
        print(f"❌ 捕获失败: {result.message}")
        return
    
    detections = result.data.get("detections", [])
    print(f"✓ 检测到 {len(detections)} 个物体")
    
    if len(detections) == 0:
        print("❌ 没有检测到物体，退出")
        return
    
    # 1.2 移动到第一个物体
    print(f"1.2 移动到物体 0...")
    result = skill.quick_execute("mycobot_arm", "move_to_object", {
        "object_no": 0,
        "speed": 40
    })
    if not result.success:
        print(f"❌ 移动失败: {result.message}")
        return
    print("✓ 移动到物体成功")
    
    # 1.3 抓取物体
    print("1.3 抓取物体...")
    result = skill.quick_execute("mycobot_arm", "grab", {"speed": 35})
    if not result.success:
        print(f"❌ 抓取失败: {result.message}")
        return
    print("✓ 抓取成功")
    
    # ========== 阶段2: 放置到机械狗背篮 ==========
    print("\n[阶段2] 放置到机械狗背篮")
    print("-" * 60)
    
    # 2.1 机械狗移动到装货区并趴下
    print("2.1 机械狗前往装货区...")
    result = skill.quick_execute("dog_0", "goto", {
        "dog_id": 0,
        "target_name": "装货区"
    })
    if not result.success:
        print(f"❌ 导航失败: {result.message}")
        return
    
    print("2.2 等待机械狗到达...")
    result = skill.quick_execute("dog_0", "wait_until_idle", {
        "dog_id": 0,
        "timeout": 60
    })
    if not result.success:
        print(f"❌ 等待超时: {result.message}")
        return
    print("✓ 机械狗到达装货区")
    
    print("2.3 机械狗趴下...")
    result = skill.quick_execute("dog_0", "lie_down", {"dog_id": 0})
    if not result.success:
        print(f"❌ 趴下失败: {result.message}")
        return
    print("✓ 机械狗已趴下")
    
    # 2.2 机械臂移动到狗背篮上方
    print("2.4 机械臂移动到狗背篮上方...")
    result = skill.quick_execute("mycobot_arm", "move_to_place", {
        "place_name": "dog_basket",
        "speed": 40
    })
    if not result.success:
        print(f"❌ 移动失败: {result.message}")
        return
    print("✓ 移动到狗背篮上方成功")
    
    # 2.3 释放物体
    print("2.5 释放物体...")
    result = skill.quick_execute("mycobot_arm", "release", {"speed": 35})
    if not result.success:
        print(f"❌ 释放失败: {result.message}")
        return
    print("✓ 物体已放入背篮")
    
    # 2.4 机械臂回到安全位置
    print("2.6 机械臂回到捕获位置...")
    result = skill.quick_execute("mycobot_arm", "move_to_place", {
        "place_name": "capture",
        "speed": 40
    })
    print("✓ 机械臂已回到安全位置")
    
    # ========== 阶段3: 机械狗运输 ==========
    print("\n[阶段3] 机械狗运输到卸货区")
    print("-" * 60)
    
    print("3.1 机械狗前往卸货区...")
    result = skill.quick_execute("dog_0", "goto", {
        "dog_id": 0,
        "target_name": "卸货区"
    })
    if not result.success:
        print(f"❌ 导航失败: {result.message}")
        return
    
    print("3.2 等待机械狗到达...")
    result = skill.quick_execute("dog_0", "wait_until_idle", {
        "dog_id": 0,
        "timeout": 60
    })
    if not result.success:
        print(f"❌ 等待超时: {result.message}")
        return
    print("✓ 机械狗到达卸货区")
    
    # ========== 阶段4: 卸货 ==========
    print("\n[阶段4] 卸货")
    print("-" * 60)
    
    print("4.1 执行卸货动作...")
    result = skill.quick_execute("dog_0", "unload", {"dog_id": 0})
    if not result.success:
        print(f"❌ 卸货失败: {result.message}")
        return
    print("✓ 卸货完成")
    
    # ========== 阶段5: 返回充电站 ==========
    print("\n[阶段5] 机械狗返回充电站")
    print("-" * 60)
    
    print("5.1 前往充电站...")
    result = skill.quick_execute("dog_0", "goto", {
        "dog_id": 0,
        "target_name": "充电站"
    })
    if not result.success:
        print(f"❌ 导航失败: {result.message}")
        return
    
    print("5.2 等待机械狗到达...")
    result = skill.quick_execute("dog_0", "wait_until_idle", {
        "dog_id": 0,
        "timeout": 60
    })
    if not result.success:
        print(f"❌ 等待超时: {result.message}")
        return
    print("✓ 机械狗已返回充电站")
    
    print("\n" + "=" * 60)
    print("✅ 物流配送工作流程完成！")
    print("=" * 60)


if __name__ == "__main__":
    try:
        delivery_workflow()
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断")
    except Exception as e:
        print(f"\n\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()

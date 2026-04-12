"""
机械狗群导航系统适配器
端点: http://localhost:8000
API: 机械狗导航系统 REST API
"""

import requests
from typing import Any, Dict, List, Optional
import time

from .base import (
    RobotAdapter, RobotCapability, RobotState, ActionResult,
    ActionStatus, RobotType
)


class DogFleetAdapter(RobotAdapter):
    """
    机械狗群导航系统适配器
    支持多只机械狗的导航、装卸货等操作
    """

    def __init__(self, name: str, endpoint: str, **config):
        super().__init__(name, endpoint, **config)
        self.robot_type = RobotType.QUADRUPED
        self.timeout = config.get("timeout", 10)
        self.dog_id = config.get("dog_id", 0)  # 默认控制0号狗

        self._capabilities = [
            RobotCapability(
                "get_status",
                "获取系统状态和所有机械狗的实时信息"
            ),
            RobotCapability(
                "add_dog",
                "添加并初始化一只机械狗",
                {"dog_id": "int (必需)", "ip": "str (必需，机械狗IP)"}
            ),
            RobotCapability(
                "remove_dog",
                "删除已保存的机械狗配置",
                {"dog_id": "int (必需)"}
            ),
            RobotCapability(
                "get_configs",
                "获取所有已保存的机械狗配置"
            ),
            RobotCapability(
                "lie_down",
                "命令机械狗趴下，准备装货",
                {"dog_id": "int (可选，默认使用初始化时的dog_id)"}
            ),
            RobotCapability(
                "goto",
                "命令机械狗自动导航到指定目标点",
                {"dog_id": "int (可选)", "target_name": "str (必需，目标点名称)"}
            ),
            RobotCapability(
                "unload",
                "命令机械狗执行卸货（倒物）动作",
                {"dog_id": "int (可选)"}
            ),
            RobotCapability(
                "stop",
                "立即停止机械狗的当前任务",
                {"dog_id": "int (可选)"}
            ),
            RobotCapability(
                "get_targets",
                "获取所有可用的目标点列表"
            ),
            RobotCapability(
                "wait_until_idle",
                "等待机械狗完成当前任务（阻塞）",
                {"dog_id": "int (可选)", "timeout": "int (可选，秒，默认120)", "poll_interval": "float (可选，秒，默认1.0)"}
            ),
        ]

    def connect(self) -> bool:
        try:
            resp = requests.get(f"{self.endpoint}/api/status", timeout=5)
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
            resp = requests.get(f"{self.endpoint}/api/status", timeout=self.timeout)
            data = resp.json()
            
            self._state.connected = True
            self._state.custom_data["running"] = data.get("running", False)
            self._state.custom_data["map_loaded"] = data.get("map_loaded", False)
            self._state.custom_data["dogs"] = data.get("dogs", {})
            
            # 如果有指定dog_id，提取该狗的状态
            dog_id_str = str(self.dog_id)
            if dog_id_str in data.get("dogs", {}):
                dog_data = data["dogs"][dog_id_str]
                self._state.position = {
                    "x": dog_data.get("position", [0, 0])[0],
                    "y": dog_data.get("position", [0, 0])[1]
                }
                self._state.custom_data["heading"] = dog_data.get("heading")
                self._state.custom_data["state"] = dog_data.get("state")
                self._state.custom_data["target"] = dog_data.get("target")
                self._state.busy = dog_data.get("state") not in ["idle", None]
        except Exception as e:
            self._state.connected = False
            self._state.error_message = str(e)
        
        return self._state

    def get_capabilities(self) -> List[RobotCapability]:
        return self._capabilities

    def execute_action(self, action: str, params: Optional[Dict[str, Any]] = None) -> ActionResult:
        params = params or {}
        dog_id = params.get("dog_id", self.dog_id)
        
        try:
            if action == "get_status":
                resp = requests.get(f"{self.endpoint}/api/status", timeout=self.timeout)
                data = resp.json()
                if resp.status_code == 200:
                    return ActionResult(ActionStatus.SUCCESS, "获取状态成功", data=data)
                return ActionResult(ActionStatus.FAILED, "获取状态失败")

            elif action == "add_dog":
                if "dog_id" not in params or "ip" not in params:
                    return ActionResult(ActionStatus.FAILED, "缺少必需参数: dog_id 和 ip")
                body = {"dog_id": params["dog_id"], "ip": params["ip"]}
                resp = requests.post(f"{self.endpoint}/api/dogs/add", json=body, timeout=60)
                data = resp.json()
                if resp.status_code == 200 and data.get("success"):
                    return ActionResult(ActionStatus.SUCCESS, f"添加机械狗 {params['dog_id']} 成功", data=data)
                return ActionResult(ActionStatus.FAILED, data.get("error", "添加失败"))

            elif action == "remove_dog":
                if "dog_id" not in params:
                    return ActionResult(ActionStatus.FAILED, "缺少必需参数: dog_id")
                body = {"dog_id": params["dog_id"]}
                resp = requests.post(f"{self.endpoint}/api/dogs/remove", json=body, timeout=self.timeout)
                data = resp.json()
                if resp.status_code == 200 and data.get("success"):
                    return ActionResult(ActionStatus.SUCCESS, f"删除机械狗 {params['dog_id']} 成功", data=data)
                return ActionResult(ActionStatus.FAILED, data.get("error", "删除失败"))

            elif action == "get_configs":
                resp = requests.get(f"{self.endpoint}/api/dogs/configs", timeout=self.timeout)
                data = resp.json()
                if resp.status_code == 200:
                    return ActionResult(ActionStatus.SUCCESS, "获取配置成功", data=data)
                return ActionResult(ActionStatus.FAILED, "获取配置失败")

            elif action == "lie_down":
                body = {"dog_id": dog_id}
                resp = requests.post(f"{self.endpoint}/api/command/lie_down", json=body, timeout=self.timeout)
                data = resp.json()
                if resp.status_code == 200 and data.get("success"):
                    return ActionResult(ActionStatus.SUCCESS, f"机械狗 {dog_id} 趴下成功", data=data)
                return ActionResult(ActionStatus.FAILED, data.get("error", "趴下失败"))

            elif action == "goto":
                if "target_name" not in params:
                    return ActionResult(ActionStatus.FAILED, "缺少必需参数: target_name")
                body = {"dog_id": dog_id, "target_name": params["target_name"]}
                resp = requests.post(f"{self.endpoint}/api/command/goto", json=body, timeout=self.timeout)
                data = resp.json()
                if resp.status_code == 200 and data.get("success"):
                    return ActionResult(ActionStatus.SUCCESS, f"机械狗 {dog_id} 开始前往 {params['target_name']}", data=data)
                return ActionResult(ActionStatus.FAILED, data.get("error", "导航失败"))

            elif action == "unload":
                body = {"dog_id": dog_id}
                resp = requests.post(f"{self.endpoint}/api/command/unload", json=body, timeout=self.timeout)
                data = resp.json()
                if resp.status_code == 200 and data.get("success"):
                    return ActionResult(ActionStatus.SUCCESS, f"机械狗 {dog_id} 卸货成功", data=data)
                return ActionResult(ActionStatus.FAILED, data.get("error", "卸货失败"))

            elif action == "stop":
                body = {"dog_id": dog_id}
                resp = requests.post(f"{self.endpoint}/api/command/stop", json=body, timeout=self.timeout)
                data = resp.json()
                if resp.status_code == 200 and data.get("success"):
                    return ActionResult(ActionStatus.SUCCESS, f"机械狗 {dog_id} 停止成功", data=data)
                return ActionResult(ActionStatus.FAILED, data.get("error", "停止失败"))

            elif action == "get_targets":
                resp = requests.get(f"{self.endpoint}/api/targets", timeout=self.timeout)
                data = resp.json()
                if resp.status_code == 200:
                    targets = data.get("targets", [])
                    return ActionResult(ActionStatus.SUCCESS, f"获取到 {len(targets)} 个目标点", data=data)
                return ActionResult(ActionStatus.FAILED, "获取目标点失败")

            elif action == "wait_until_idle":
                timeout_sec = params.get("timeout", 120)  # 默认120秒
                poll_interval = params.get("poll_interval", 1.0)  # 默认1秒轮询一次
                start_time = time.time()
                last_state = None
                while time.time() - start_time < timeout_sec:
                    try:
                        status_resp = requests.get(f"{self.endpoint}/api/status", timeout=self.timeout)
                        status_data = status_resp.json()
                        dog_state = status_data.get("dogs", {}).get(str(dog_id), {}).get("state")
                        
                        # 记录状态变化用于调试
                        if dog_state != last_state:
                            last_state = dog_state
                        
                        if dog_state == "idle":
                            return ActionResult(ActionStatus.SUCCESS, f"机械狗 {dog_id} 已完成任务", data={"final_state": dog_state})
                    except Exception as e:
                        # 网络错误不应该导致整个等待失败，继续重试
                        pass
                    
                    time.sleep(poll_interval)
                
                # 超时时返回最后的状态信息
                return ActionResult(ActionStatus.TIMEOUT, f"等待超时（{timeout_sec}秒），最后状态: {last_state}")

            else:
                return ActionResult(ActionStatus.FAILED, f"未知动作: {action}")

        except requests.Timeout:
            return ActionResult(ActionStatus.TIMEOUT, f"请求超时: {action}")
        except Exception as e:
            return ActionResult(ActionStatus.FAILED, f"执行失败: {str(e)}", error=e)

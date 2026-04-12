"""
MyCobot 机械臂适配器
端点: http://192.168.50.120:5000
API: Flask Server (MyCobot Flask Server API)
"""

import requests
from typing import Any, Dict, List, Optional

from .base import (
    RobotAdapter, RobotCapability, RobotState, ActionResult,
    ActionStatus, RobotType
)


class MyCobotAdapter(RobotAdapter):
    """
    MyCobot 机械臂适配器
    支持物体检测、抓取、放置等操作
    """

    def __init__(self, name: str, endpoint: str, **config):
        super().__init__(name, endpoint, **config)
        self.robot_type = RobotType.MANIPULATOR
        self.timeout = config.get("timeout", 30)

        self._capabilities = [
            RobotCapability(
                "capture",
                "捕获图像并检测物体，返回检测到的物体列表",
                {"move_to_capture": "bool (默认true)", "include_image": "bool (默认false)"}
            ),
            RobotCapability(
                "get_detections",
                "获取最近一次捕获的物体检测数据"
            ),
            RobotCapability(
                "describe_image",
                "使用VLM描述最新标注图像"
            ),
            RobotCapability(
                "move_to_object",
                "移动机械臂到指定检测物体位置",
                {"object_no": "int (必需，物体索引)", "speed": "int (可选，移动速度)"}
            ),
            RobotCapability(
                "move_to_place",
                "移动机械臂到预定义命名位置",
                {"place_name": "str (必需: capture/drop/dog_basket)", "speed": "int (可选)"}
            ),
            RobotCapability(
                "grab",
                "抓取物体（启动吸盘）",
                {"speed": "int (可选)"}
            ),
            RobotCapability(
                "release",
                "释放物体（关闭吸盘）",
                {"speed": "int (可选)"}
            ),
            RobotCapability(
                "head_shake",
                "执行摇头动作"
            ),
            RobotCapability(
                "head_dance",
                "执行舞蹈动作"
            ),
            RobotCapability(
                "head_nod",
                "执行点头动作"
            ),
            RobotCapability(
                "hit",
                "执行击打动作"
            ),
        ]

    def connect(self) -> bool:
        try:
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
            resp = requests.get(f"{self.endpoint}/health", timeout=self.timeout)
            data = resp.json()
            self._state.connected = data.get("status") == "ok"
            self._state.custom_data["captured_at"] = data.get("captured_at")
            self._state.custom_data["detections_available"] = data.get("detections_available", False)
        except Exception:
            pass
        return self._state

    def get_capabilities(self) -> List[RobotCapability]:
        return self._capabilities

    def execute_action(self, action: str, params: Optional[Dict[str, Any]] = None) -> ActionResult:
        params = params or {}
        try:
            if action == "capture":
                body = {
                    "move_to_capture": params.get("move_to_capture", True),
                    "include_image": params.get("include_image", False),
                }
                resp = requests.post(f"{self.endpoint}/capture", json=body, timeout=self.timeout)
                data = resp.json()
                if resp.status_code == 200:
                    return ActionResult(ActionStatus.SUCCESS, f"检测到 {len(data.get('detections', []))} 个物体", data=data)
                return ActionResult(ActionStatus.FAILED, data.get("error", "捕获失败"))

            elif action == "get_detections":
                resp = requests.get(f"{self.endpoint}/detections", timeout=self.timeout)
                data = resp.json()
                if resp.status_code == 200:
                    return ActionResult(ActionStatus.SUCCESS, "获取检测数据成功", data=data)
                return ActionResult(ActionStatus.FAILED, data.get("error", "获取失败"))

            elif action == "describe_image":
                resp = requests.get(f"{self.endpoint}/describe_annotated_image", timeout=self.timeout)
                data = resp.json()
                if resp.status_code == 200:
                    return ActionResult(ActionStatus.SUCCESS, data.get("description", ""), data=data)
                return ActionResult(ActionStatus.FAILED, data.get("error", "描述失败"))

            elif action == "move_to_object":
                if "object_no" not in params:
                    return ActionResult(ActionStatus.FAILED, "缺少必需参数: object_no")
                body = {"object_no": params["object_no"]}
                if "speed" in params:
                    body["speed"] = params["speed"]
                resp = requests.post(f"{self.endpoint}/robot/move_to_object", json=body, timeout=self.timeout)
                data = resp.json()
                if resp.status_code == 200 and data.get("status") == "ok":
                    return ActionResult(ActionStatus.SUCCESS, "移动到物体成功", data=data)
                return ActionResult(ActionStatus.FAILED, data.get("error", "移动失败"))

            elif action == "move_to_place":
                if "place_name" not in params:
                    return ActionResult(ActionStatus.FAILED, "缺少必需参数: place_name")
                body = {"place_name": params["place_name"]}
                if "speed" in params:
                    body["speed"] = params["speed"]
                resp = requests.post(f"{self.endpoint}/robot/move_to_place", json=body, timeout=self.timeout)
                data = resp.json()
                if resp.status_code == 200 and data.get("status") == "ok":
                    return ActionResult(ActionStatus.SUCCESS, f"移动到 {params['place_name']} 成功", data=data)
                return ActionResult(ActionStatus.FAILED, data.get("error", "移动失败"))

            elif action == "grab":
                body = {}
                if "speed" in params:
                    body["speed"] = params["speed"]
                resp = requests.post(f"{self.endpoint}/robot/grab", json=body, timeout=self.timeout)
                data = resp.json()
                if resp.status_code == 200 and data.get("status") == "ok":
                    return ActionResult(ActionStatus.SUCCESS, "抓取成功", data=data)
                return ActionResult(ActionStatus.FAILED, data.get("error", "抓取失败"))

            elif action == "release":
                body = {}
                if "speed" in params:
                    body["speed"] = params["speed"]
                resp = requests.post(f"{self.endpoint}/robot/release", json=body, timeout=self.timeout)
                data = resp.json()
                if resp.status_code == 200 and data.get("status") == "ok":
                    return ActionResult(ActionStatus.SUCCESS, "释放成功", data=data)
                return ActionResult(ActionStatus.FAILED, data.get("error", "释放失败"))

            elif action in ("head_shake", "head_dance", "head_nod", "hit"):
                endpoint_map = {
                    "head_shake": "/robot/head_shake",
                    "head_dance": "/robot/head_dance",
                    "head_nod": "/robot/head_nod",
                    "hit": "/robot/hit",
                }
                resp = requests.post(f"{self.endpoint}{endpoint_map[action]}", timeout=self.timeout)
                data = resp.json()
                if resp.status_code == 200 and data.get("status") == "ok":
                    return ActionResult(ActionStatus.SUCCESS, f"{action} 执行成功", data=data)
                return ActionResult(ActionStatus.FAILED, data.get("error", f"{action} 失败"))

            return ActionResult(ActionStatus.FAILED, f"未知动作: {action}")

        except requests.Timeout:
            return ActionResult(ActionStatus.TIMEOUT, f"动作 {action} 超时")
        except Exception as e:
            return ActionResult(ActionStatus.FAILED, str(e), error=e)

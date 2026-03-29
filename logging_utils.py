"""
Logging utilities for Email Triage.
"""
import logging
import json
from typing import Any, Dict

class StructuredLogger:
    def __init__(self, name: str = "email_triage", debug: bool = False):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG if debug else logging.INFO)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
        self.logger.handlers = [handler]
        self.debug = debug

    def log(self, msg: str, data: Dict[str, Any] = None, level: str = "info"):
        entry = {"msg": msg}
        if data:
            entry.update(data)
        if level == "debug":
            self.logger.debug(json.dumps(entry))
        elif level == "warning":
            self.logger.warning(json.dumps(entry))
        elif level == "error":
            self.logger.error(json.dumps(entry))
        else:
            self.logger.info(json.dumps(entry))

    def trace_step(self, step: int, action: Any, obs: Any, reward: Any, info: Any):
        self.log("step_trace", {
            "step": step,
            "action": str(action),
            "observation": str(obs),
            "reward": str(reward),
            "info": str(info)
        }, level="debug")

    def state_diff(self, before: Any, after: Any):
        self.log("state_diff", {
            "before": str(before),
            "after": str(after)
        }, level="debug")

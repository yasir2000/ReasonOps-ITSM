"""
Simple in-memory publish/subscribe event bus for ReasonOps ITSM.
"""
from __future__ import annotations
from typing import Callable, Dict, List, Any
import logging

class EventBus:
    def __init__(self) -> None:
        self._subscribers: Dict[str, List[Callable[[Dict[str, Any]], None]]] = {}
        self.logger = logging.getLogger(__name__)

    def subscribe(self, event_name: str, callback: Callable[[Dict[str, Any]], None]) -> None:
        self._subscribers.setdefault(event_name, []).append(callback)

    def publish(self, event_name: str, payload: Dict[str, Any]) -> None:
        for cb in self._subscribers.get(event_name, []):
            try:
                cb(payload)
            except Exception as e:
                self.logger.exception(f"Event handler failed for {event_name}: {e}")

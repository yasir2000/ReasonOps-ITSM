"""
Simple JSON persistence for orchestrator events (penalties, chargebacks, KPIs).
Serializes datetimes to ISO strings and Decimals to strings.
"""
from __future__ import annotations
import json
import os
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


def _ensure_dir() -> None:
    os.makedirs(DATA_DIR, exist_ok=True)


def _default(o: Any):
    if isinstance(o, datetime):
        return o.isoformat()
    if isinstance(o, Decimal):
        return str(o)
    # dataclasses
    if hasattr(o, "__dict__"):
        return o.__dict__
    return str(o)


def _collection_path(collection: str) -> str:
    return os.path.join(DATA_DIR, f"{collection}.json")


def append_record(collection: str, record: Dict[str, Any]) -> None:
    _ensure_dir()
    path = _collection_path(collection)
    data: List[Dict[str, Any]] = []
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = []
    data.append(record)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, default=_default, indent=2)


def read_all(collection: str) -> List[Dict[str, Any]]:
    _ensure_dir()
    path = _collection_path(collection)
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def query(collection: str, limit: Optional[int] = None, **filters) -> List[Dict[str, Any]]:
    """Query collection with optional filters and limit"""
    data = read_all(collection)
    
    # Apply filters
    if filters:
        filtered_data = []
        for record in data:
            match = True
            for key, value in filters.items():
                if record.get(key) != value:
                    match = False
                    break
            if match:
                filtered_data.append(record)
        data = filtered_data
    
    # Apply limit
    if limit is not None:
        data = data[:limit]
    
    return data


def save(collection: str, data: List[Dict[str, Any]]) -> None:
    """Save complete data to collection"""
    _ensure_dir()
    path = _collection_path(collection)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, default=_default, indent=2)


def get_agent_decisions(limit: Optional[int] = None, event_type: Optional[str] = None, agent_name: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get agent decisions with optional filtering"""
    filters = {}
    if event_type:
        filters["event_type"] = event_type
    if agent_name:
        filters["agent_name"] = agent_name
    
    return query("agent_decisions", limit=limit, **filters)


def month_key(dt: datetime) -> str:
    return dt.strftime("%Y-%m")


def rollup_monthly(collection: str, date_field: str, sum_fields: List[str], group_by: Optional[List[str]] = None) -> Dict[str, Any]:
    rows = read_all(collection)
    rollup: Dict[str, Any] = {}
    for r in rows:
        ts_str = r.get(date_field)
        if not ts_str:
            continue
        try:
            ts = datetime.fromisoformat(ts_str)
        except Exception:
            continue
        mk = month_key(ts)
        if group_by:
            group_key = tuple(r.get(g) for g in group_by)
            R = rollup.setdefault(mk, {})
            G = R.setdefault(group_key, {k: 0.0 for k in sum_fields})
            for k in sum_fields:
                try:
                    G[k] += float(r.get(k, 0) or 0)
                except Exception:
                    pass
        else:
            R = rollup.setdefault(mk, {k: 0.0 for k in sum_fields})
            for k in sum_fields:
                try:
                    R[k] += float(r.get(k, 0) or 0)
                except Exception:
                    pass
    return rollup

# -*- coding:utf-8 -*-
"""
*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*
Author: Zack
Create Date: 2025/7/23
Description:
*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*
"""
import threading
from typing import List, Dict, Union
from contextvars import ContextVar
import traceback

progress_context: ContextVar[List[dict]] = ContextVar("progress_context", default=[])


def safe_single_instance(cls):
    _instances = {}
    _lock = threading.Lock()

    def wrapper(*args, **kwargs):
        if cls not in _instances:
            with _lock:
                if cls not in _instances:
                    _instances[cls] = cls(*args, **kwargs)
        else:
            _instances[cls]._init_instance(*args, **kwargs)
        return _instances[cls]
    return wrapper


@safe_single_instance
class ProgressShareInstance:
    def __init__(self, *args, **kwargs):
        self._lock = threading.RLock()
        self.scale = 1
        self.speed = 0
        self._init_instance(*args, **kwargs)
        self.text_stack = []

    def _init_instance(self, scale=1):
        self.scale = scale
        self.spare_space = 100 / self.scale

    @property
    def progress_dict(self) -> List[dict]:
        return progress_context.get()

    def append_record(self, config_item: dict):
        with self._lock:
            records = self.progress_dict.copy()
            records.append(config_item)
            progress_context.set(records)

    def make_progress(self, final=False) -> str:
        try:
            with self._lock:
                records = self.progress_dict
                if not records:
                    return ""
                if not final:
                    records[-1]['count'] += 1
                return self._refresh(final)
        except Exception:
            traceback.print_exc()

    def _refresh(self, final=False):
        _str = f"\r |"
        space = self.spare_space
        records = self.progress_dict
        for index, item in enumerate(records):
            strip = (space / self.scale) * ((item['count'] - 1) / item['total']) if index != len(records) - 1 else (space / self.scale) * (item['count'] / item['total'])
            item['strip'] = strip
            space -= strip
            _str += item['body'] * int(strip)
        _str += records[-1]['head']
        _str += " " * int((100 - sum([int(item['strip']) for item in records])) / self.scale)
        _str += f"|  {records[-1]['count'] / records[-1]['total'] * 100 :.2f}%  "
        return _str

    def finished_progress(self):
        with self._lock:
            records = self.progress_dict.copy()
            if len(self.text_stack) != 0:
                self.text_stack.pop()
            if records:
                records.pop()
                progress_context.set(records)
            if not records:
                print()

    def set_speed(self, speed):
        self.speed = speed

    def get_speed(self):
        return self.speed

    def set_scale(self, scale):
        self.scale = scale

    def get_scale(self):
        return self.scale

    def append_text(self, text):
        if len(self.progress_dict) > len(self.text_stack):
            self.text_stack.append(text)
        else:
            self.text_stack.pop()
            self.text_stack.append(text)

    def pop_text(self):
        self.text_stack.pop()

    def text_top(self):
        return self.text_stack[-1] if len(self.text_stack) != 0 else ""

    def get_text_stack(self):
        return self.text_stack

    def __del__(self):
        self.finished_progress()
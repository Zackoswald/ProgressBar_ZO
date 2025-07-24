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
from ProgressBar_ZO._exceptions.ScaleResetException import ScaleResetException

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
        self.speed = 0
        self.scale = 1
        self.scale_flag = False
        self._init_instance(*args, **kwargs)
        self.text_stack = []

    def _init_instance(self):
        self.spare_space = 100

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
        left_space = self.spare_space * self.scale
        _str = [f"\r | "]
        for index, item in enumerate(self.progress_dict):
            self.progress_dict[index]['percentage'] = (item['count'] - 1) / item['total'] if index != len(self.progress_dict) - 1 else item['count'] / item['total']
            self.progress_dict[index]['strip'] = left_space * self.progress_dict[index]['percentage']
            left_space = (1 - self.progress_dict[index]['percentage']) * left_space
            _str.append(self.progress_dict[index]['body'] * int(self.progress_dict[index]['strip']))
        _str.append(self.progress_dict[-1]['head'])
        _str.append(int(left_space) * " ")
        _str.append(f"|  {self.progress_dict[-1]['count'] / self.progress_dict[-1]['total'] * 100 :.2f}%  ")
        return "".join(_str)



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
        if not self.scale_flag:
            self.scale = scale
            self.scale_flag = True
        # else:
        #     raise ScaleResetException(self.scale, scale)

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
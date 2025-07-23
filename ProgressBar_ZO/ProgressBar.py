# -*- coding:utf-8 -*-
"""
*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*
Author: Zack
Create Date: 2025/7/16
Description:  Simple ProgressBar
*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*
"""
import asyncio
import time
import random
import re
from ._utils.ProgressShareInstance import ProgressShareInstance
from concurrent.futures import ThreadPoolExecutor
from collections.abc import Iterable


class ProgressBar:
    """
    Construct ProgressBar:
    """
    default_pattern = [
        {'body': '=', 'head': '>'},
        {'body': '-', 'head': '>'},
        {'body': '~', 'head': '>'}
    ]

    def __init__(self, data: Iterable, body: str = "", head: str = "", scale: int = 1, track: bool = True, text: str = ""):
        self.data = data
        self.body_pattern = body
        self.head_pattern = head
        self.track = track
        self.scale = scale
        self.text = text
        self.index = 0
        self.timer = None
        self.timer_sleep = 0.01
        self._pattern_instance = ProgressShareInstance()

        pattern_idx = len(self._pattern_instance.progress_dict)
        self._pattern_instance.append_record({
            'total': len(list(data)),
            'count': 0,
            'strip': 0,
            'body': body if body else self.default_pattern[pattern_idx % len(self.default_pattern)]['body'],
            'head': head if head else self.default_pattern[pattern_idx % len(self.default_pattern)]['head'],
        })
        self._pattern_instance.set_scale(self.scale)

    def __iter__(self):
        return self._sync_iter()

    def generate_text(self, item=None, last=False):
        if isinstance(item, tuple):
            tar_text = self.text
            for param_index, replacement in enumerate(re.findall(r'\$[1-2]', self.text)):
                idx = int(replacement.replace('$', '')) - 1
                if idx < len(item):
                    self._pattern_instance.append_text(tar_text.replace(replacement, str(item[idx])))
        elif item is not None:
            match = re.search(r'\$[1-2]', self.text)
            if match:
                self._pattern_instance.append_text(self.text.replace(match.group(), str(item)))
        tar_text = ' | '.join(self._pattern_instance.get_text_stack())
        # self._pattern_instance.pop_text() if not last and len(self._pattern_instance.get_text_stack()) != 0 else [self._pattern_instance.pop_text() for _ in range(2)]
        return tar_text

    def _sync_iter(self):
        if isinstance(self.data, dict):
            iterable = self.data.items()
        else:
            iterable = self.data

        for index, item in enumerate(iterable):
            # print(self._pattern_instance.get_text_stack())
            # if len(self._pattern_instance.get_text_stack()) != 0:
            #     self._pattern_instance.pop_text()
            if index % max(1, int(len(self.data) * self.timer_sleep)) == 0 and self.timer is None:
                self.timer = time.perf_counter()
            elif self.timer is not None:
                self._pattern_instance.set_speed(1 / (time.perf_counter() - self.timer))
                self.timer = None
            if self.track:
                print(f"{self._pattern_instance.make_progress()} {self._pattern_instance.get_speed():.2f}/s | {self.generate_text(item)}", end="")
            yield item
        if self.track:
            print(f"{self._pattern_instance.make_progress(final=True)} {self._pattern_instance.get_speed():.2f}/s | {self.generate_text()}", end="")
        self._pattern_instance.finished_progress()

    async def __aiter__(self):
        return self._async_iter()

    async def _async_iter(self):
        if isinstance(self.data, dict):
            iterable = self.data.items()
        else:
            iterable = self.data

        for index, item in enumerate(iterable):
            if isinstance(item, tuple):
                tar_text = self.text
                for param_index, replacement in enumerate(re.findall(r'\$[1-2]', self.text)):
                    idx = int(replacement.replace('$', '')) - 1
                    if idx < len(item):
                        tar_text = tar_text.replace(replacement, str(item[idx]))
            else:
                match = re.search(r'\$[1-2]', self.text)
                if match:
                    tar_text = self.text.replace(match.group(), str(item))

            if index % max(1, int(len(self.data) * self.timer_sleep)) == 0 and self.timer is None:
                self.timer = time.perf_counter()
            elif self.timer is not None:
                self._pattern_instance.set_speed(1 / (time.perf_counter() - self.timer))
                self.timer = None

            if self.track:
                print(
                    f"{self._pattern_instance.make_progress()} {self._pattern_instance.get_speed():.2f}/s | {tar_text}",
                    end="")

            yield item
            await asyncio.sleep(0)

        if self.track:
            print(
                f"{self._pattern_instance.make_progress(final=True)} {self._pattern_instance.get_speed():.2f}/s | {self.generate_text()}",
                end="")
        self._pattern_instance.finished_progress()
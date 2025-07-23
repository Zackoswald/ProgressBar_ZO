# -*- coding:utf-8 -*-
"""
*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*
Author: Zack
Create Date: 2025/7/16
Description:  进度条组件，注意不要嵌套元任务，遍历完成时间少于0.01s的任务列表将会使终端io无法跟上完成任务导致控制台字符串滞留造成内存泄漏
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
            # 文本生成逻辑（与同步模式一致）
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

            # 计时和速度计算逻辑（与同步模式一致）
            if index % max(1, int(len(self.data) * self.timer_sleep)) == 0 and self.timer is None:
                self.timer = time.perf_counter()
            elif self.timer is not None:
                self._pattern_instance.set_speed(1 / (time.perf_counter() - self.timer))
                self.timer = None

            # 进度跟踪输出（与同步模式一致）
            if self.track:
                print(
                    f"{self._pattern_instance.make_progress()} {self._pattern_instance.get_speed():.2f}/s | {tar_text}",
                    end="")

            yield item
            await asyncio.sleep(0)  # 关键点：保持异步特性

        # 最终进度完成标记（与同步模式一致）
        if self.track:
            print(
                f"{self._pattern_instance.make_progress(final=True)} {self._pattern_instance.get_speed():.2f}/s | {self.generate_text()}",
                end="")
        self._pattern_instance.finished_progress()




def exsub(item):
    time.sleep(random.uniform(0, 1))


def sub(item):
    with ThreadPoolExecutor(max_workers=4) as w:
        tasks = [exsub(v) for k, v in ProgressBar({'a': 1, 'b': 2, 'c': 3, 'd': 4}.items(), text="正在处理值$1")]


async def async_sub():
    for i in ProgressBar(range(20), text="正在处理值$1"):
        await asyncio.sleep(random.uniform(1, 2))

if __name__ == "__main__":
    # for k, v in ProgressBar({'a': 1, 'b': 2}.items(), text='1正在处理值$1'):
    #     for k2, v2 in ProgressBar({'a': 1, 'b': 2}.items(), text='2正在处理值$1'):
    #         for k3, v3 in ProgressBar({'a': 1, 'b': 2}.items(), text='3正在处理值$1'):
    #             time.sleep(2)
    # with ProcessPoolExecutor(max_workers=3) as p:
    #     tasks = [sub(i) for i in ProgressBar(range(10), text="1正在处理$1")]
    asyncio.run(async_sub())

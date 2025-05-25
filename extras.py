from pathlib import Path
from time import time
from collections import deque

import constants as const

from typing import Generator

#helper functions
def choose_correct_path(*args: Path) -> Path | None:
    for path in args:
        if path.exists():
            return path
        
    return None

#TODO: Save file to mega
def save_to_mega(file: Path | tuple[Path, ...] | Generator[Path, None, None]) -> None: # TODO: save to mega
    if isinstance(file, Path): # gurantees it to be a tuple of path
        file = file,

    print(file)

#TODO: Fetch file from mega
def fetch_from_mega(name: str | tuple[str, ...]): # TODO: get file from mega
    if isinstance(name, str):
        name = name,

def clear_cache(uploads: deque[tuple[str, float]]):
    cur_time: float = time()

    #60 seconds -> 1min
    #3600 seconds -> 1hr
    #86400 seconds -> 24hrs -> 1day

    for _ in range(len(uploads)):

        upload: tuple[str, float] = uploads.pop()
        time_passed = cur_time - upload[1]

        if time_passed < const.TIME_LIMIT:
            print(f"cleared cache for {upload}")
            uploads.appendleft(upload)

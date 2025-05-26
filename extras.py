from pathlib import Path
from time import time
from collections import deque
from typing import Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from uuid import uuid4 # for random files

import constants as const

#helper functions
def deque_to_list(deq: deque[const.Upload]):
    lst: list[const.Upload] = []

    for upload in deq:
        lst.append(upload)

    return lst

def choose_correct_path(*args: Path) -> Optional[Path]:
    for path in args:
        if path.exists():
            return path
        
    return None

def upload(path: str) -> tuple[str, bool, Optional[str]]:
    try:
        file = const.CLIENT.upload(path) #type:ignore
        if not file:
            raise Exception("Failed to upload")
        
        # FOR LATER!!!
        # link = const.CLIENT.get_upload_link(file)
        return (path, True, None)
    except Exception as e:
        return (path, False, str(e))

#TODO: Save file to mega
def save_to_mega(files: Path | list[Path]) -> list[tuple[str, bool, Optional[str]]]: # TODO: save to mega
    if isinstance(files, Path): # gurantees it to be a list of path
        files = [files]

    results: list[tuple[str, bool, Optional[str]]] = []
    with ThreadPoolExecutor() as executor:
        future_to_path = {
            executor.submit(upload, path.as_posix()):
            path
            for path in files
        }

        for future in as_completed(future_to_path):
            results.append(future.result())
    
    return results

def fetch_from_mega(dest: Path, name: str) -> Optional[Path]:
    if file:=const.CLIENT.find(name): # type: ignore
        return const.CLIENT.download(file, dest_path=dest) # type: ignore

def generate_unique_name(dir: Path, suffix: str = "") -> Path:
    return dir / f"{uuid4().hex}{suffix}"

def get_uploads_size():
    total_size = 0

    for video in const.VIDEO.iterdir():  # Recursively iterate over all files
        total_size += video.stat().st_size  # size in bytes
    for image in const.IMAGE.iterdir():
        total_size += image.stat().st_size

    return total_size / (1024 * 1024)  # convert bytes to MB

#clear cache (if right_now, entire cache is cleared on demand)
def clear_cache(right_now: bool=False):

    with const.CUR_UPLOADS_LOCK:
        cur_time: float = time()

        while const.CUR_UPLOADS:
            time_passed = cur_time - const.CUR_UPLOADS[-1].timestamp

            if time_passed < const.CACHE_TIME_LIMIT and not right_now:
                break


            expired = const.CUR_UPLOADS.pop()
            print(f"Cleared cache for {expired.name}")

            Path(expired.name).unlink(missing_ok=True)

    with const.SPACE_TAKEN_LOCK:
        const.SPACE_TAKEN = get_uploads_size()

#upload things in the upload queue
def upload_periodically():
    with const.UPLOAD_QUEUE_LOCK:
        upload_batch = const.UPLOAD_QUEUE.copy()
        const.UPLOAD_QUEUE.clear()

    const.logger.info(f"Saving {len(upload_batch)} files to mega!")
    results = save_to_mega(upload_batch)

    for path, success, info in results:
        if success:
            const.logger.info(f"✅ {path} uploaded to mega")
        else:
            const.logger.error(f"❌ {path} failed due to: {info}")
from pathlib import Path
from time import time
from collections import deque
from typing import Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

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

def upload(path: str, i: int) -> tuple[str, bool, str]:
    try:
        file = const.CLIENT.upload(path)
        if not file:
            raise Exception("Failed to upload")
        
        # FOR LATER!!!
        # link = const.CLIENT.get_upload_link(file)
        return (path, True, "")
    except Exception as e:
        return (path, False, str(e))

#TODO: Save file to mega
def save_to_mega(files: Path | list[Path]): # TODO: save to mega
    if isinstance(files, Path): # gurantees it to be a list of path
        files = [files]

    results: list[tuple[str, bool, str]] = []
    with ThreadPoolExecutor() as executor:
        future_to_path = {
            executor.submit(upload, path.as_posix(), i):
            path
            for i, path in enumerate(files, start=1)
        }

        for future in as_completed(future_to_path):
            results.append(future.result())

        
    for path, success, info in results:
        if success:
            print(f"✅ {path} uploaded: {info}")
        else:
            print(f"❌ {path} failed: {info}")

def fetch_from_mega(dest: Path, name: str) -> Optional[Path]:
    if file:=const.CLIENT.find(name): # type: ignore
        return const.CLIENT.download(file, dest_path=dest) # type: ignore

def clear_cache():
    uploads = const.CUR_UPLOADS

    cur_time: float = time()

    #60 seconds -> 1min
    #3600 seconds -> 1hr
    #86400 seconds -> 24hrs -> 1day

    while uploads:
        time_passed = cur_time - uploads[-1].timestamp

        if time_passed < const.TIME_LIMIT:
            break

        expired = uploads.pop()
        print(f"Cleared cache for {expired.name}")

        Path(expired.name).unlink(missing_ok=True)

        #TODO: Delete the files linked to them.


# save_to_mega(const.IMAGE.iterdir())
# result = fetch_from_mega(Path("Images"), "images.png")

# print(result)
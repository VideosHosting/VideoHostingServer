from pathlib import Path
from mega import Mega #type: ignore
from dotenv import load_dotenv
from os import getenv
from typing import NamedTuple
from collections import deque
from time import time

load_dotenv("secrets.env") # load up our envs

#constants
VIDEO = Path("Videos")
IMAGE = Path("Images")
VIDEO.mkdir(exist_ok=True)
IMAGE.mkdir(exist_ok=True)

Upload = NamedTuple('Upload', [('name', str), ('timestamp', float)])

VIDEO_EXT: set[str] = {'.mp4', '.webm', '.mov'} # supported image extensions
IMAGE_EXT: set[str] = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.avif'}

# 24 hours (in seconds)
TIME_LIMIT = 86_400

#not dealing with circular imports
def _get_current_uploads() -> deque[Upload]:
    return  deque([
        Upload(name=str(path), timestamp=time())
        for folder in (VIDEO, IMAGE)
        for path in folder.iterdir()
    ])

CUR_UPLOADS: deque[Upload] = _get_current_uploads()

CLIENT = Mega().login(getenv("EMAIL"), getenv("PASS"))
if not CLIENT or not hasattr(CLIENT, 'get_user'):
    raise Exception("❌ Mega login failed — check your EMAIL or PASS in environment variables.")


'''
    TODO: DevLog 1
        * change CUR_UPLOAD to a file
        * Its only accessed once a day so its fine.

        * implemenet fetch_from_mega and save_to_mega
        * remove ALL_UPLOADS
            * Its pointless. May change later on
            * Could use it to bring back files for a day. just NRN

        * Also Fix code base. I swear it looks like shit.
        * Save to mega every 12 hours (as It'll be slow if I do it every upload)
        * Should also probably switch to Async for speed boosts
'''
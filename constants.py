from pathlib import Path
from mega import Mega #type: ignore
from dotenv import load_dotenv
from os import getenv
from typing import NamedTuple
from collections import deque
from time import time
from threading import Lock
import logging

load_dotenv("secrets.env") # load up our envs

#logging
logger = logging.getLogger("server_logger")
logger.setLevel(logging.INFO)

if not logger.handlers:
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')

    file_handler = logging.FileHandler("server.log")
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

#constants
VIDEO = Path("Videos")
IMAGE = Path("Images")
VIDEO.mkdir(exist_ok=True)
IMAGE.mkdir(exist_ok=True)

Upload = NamedTuple('Upload', [('name', str), ('timestamp', float)])

VIDEO_EXT: set[str] = {'.mp4', '.webm', '.mov'} # supported image extensions
IMAGE_EXT: set[str] = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.avif'}

# 24 hours (in seconds)
CACHE_TIME_LIMIT = 86_400
UPLOAD_TIME_LIMIT = 43_200 # half a day

# current space taken in MB
SPACE_TAKEN = 0
SPACE_TAKEN_LOCK = Lock() # probably not needed but I'm willing to avoid a headache

#not dealing with circular imports
def _get_current_uploads() -> deque[Upload]:
    return  deque([
        Upload(name=str(path), timestamp=time())
        for folder in (VIDEO, IMAGE)
        for path in folder.iterdir()
    ])

CUR_UPLOADS: deque[Upload] = _get_current_uploads()
UPLOAD_QUEUE: list[Path] = list()

CUR_UPLOADS_LOCK = Lock()
UPLOAD_QUEUE_LOCK = Lock()

CLIENT = Mega().login(getenv("EMAIL"), getenv("PASS")) #type:ignore
if not CLIENT or not hasattr(CLIENT, 'get_user'):
    raise Exception("❌ Mega login failed — check your EMAIL or PASS in environment variables.")

'''
    * TODO:
        * Add removing images/videos
        * Add authentication (So no one but ME uses it)
'''
from pathlib import Path
from mega import Mega #type: ignore
from dotenv import load_dotenv
from os import getenv
from time import time
from threading import Lock
from concurrent.futures import ThreadPoolExecutor
from apscheduler.executors.pool import ThreadPoolExecutor as APSchedulerThreadPoolExecutor
import logging

# from modules.file import File, Upload

from modules.file import File, Upload

load_dotenv("secrets.env") # load up our envs

#not dealing with circular imports
def _get_current_uploads() -> list[Upload]:
    return  [
        Upload(name=str(path), timestamp=time())
        for folder in (VIDEO, IMAGE)
        for path in folder.iterdir()
    ]

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

_ASSETS = Path("Assets") # this is a private folder

#constants
VIDEO = _ASSETS / "Videos"
IMAGE = _ASSETS / "Images"
JSON  = _ASSETS / "Json"

#make the directories
_ASSETS.mkdir(exist_ok=True)
VIDEO.mkdir(exist_ok=True)
IMAGE.mkdir(exist_ok=True)
JSON.mkdir(exist_ok=True)

VIDEO_EXT: set[str] = {'.mp4', '.webm', '.mov'} # supported image extensions
IMAGE_EXT: set[str] = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.avif'}

# 24 hours (in seconds)
CACHE_TIME_LIMIT = 86_400
UPLOAD_TIME_LIMIT = 28800 # 1/3 of the day in seconds

# current space taken in MB
SPACE_TAKEN = 0
SPACE_TAKEN_LOCK = Lock() # probably not needed but I'm willing to avoid a headache

CUR_UPLOADS = File.from_json(JSON / "CUR_UPLOADS.json",
    _get_current_uploads()
)
UPLOAD_QUEUE = File(JSON / "UPLOAD_QUEUE.json")

EXECUTOR = ThreadPoolExecutor(max_workers=3) # for async uploads
SCHEDULER_EXECUTOR = APSchedulerThreadPoolExecutor(max_workers=2) # for periodic tasks

logger.info(f"Logging in mega with {getenv('EMAIL') = } and {getenv('PASS') = }")
CLIENT = Mega().login(getenv("EMAIL"), getenv("PASS")) #type:ignore
if not CLIENT or not hasattr(CLIENT, 'get_user'):
    raise RuntimeError("Mega login failed.")

'''
    * TODO:
        * Add removing images/videos
        * Add authentication (So no one but ME uses it)

    TODO:
        * Migrate CUR_UPLOADS/UPLOAD_QUEUE to a file
        * The cache gets cleared when It goes to sleep
        * So everything goes to shit

    TODO:
        * Add chunk uploads
        * Using /start_upload /finish_upload
        * When calling /start_upload, It should have metadata about the file
            * File size (overall size)
            * Number of chunks

'''
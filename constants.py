from pathlib import Path
from mega import Mega
from dotenv import load_dotenv
from os import getenv
from collections import deque

load_dotenv("secrets.env") # load up our envs

#constants
VIDEO = Path("Videos")
IMAGE = Path("Images")

VIDEO_EXT: set[str] = {'.mp4', '.webm', '.mov'} # supported image extensions
IMAGE_EXT: set[str] = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.avif'}

# 24 hours (in seconds)
TIME_LIMIT = 86_400

ALL_UPLOADES: list[str] = [
    #"Images/image.png"
    #"Videos/video.mp4
    # "
    str(p)
    for p in VIDEO.iterdir()
] + [ str(p) for p in IMAGE.iterdir() ]
 # every single file (optimize later, could be a waste of space tbf)
CUR_UPLOADES: deque[tuple[str, float]] = deque(
    #("Images/image.png", time)
) # files that are currently in the cache

CLIENT = Mega().login(getenv("EMAIL"), getenv("PASS"))

VIDEO.mkdir(exist_ok=True)
IMAGE.mkdir(exist_ok=True)

# if not all([VIDEO.is_dir(), IMAGE.is_dir()]):
#     raise FileNotFoundError(f"Folder {VIDEO} or {IMAGE} do not exist")

'''
    TODO:
        * change CUR_UPLOAD to a file
        * Its only accessed once a day so its fine.

        * implemenet fetch_from_mega and save_to_mega
        * remove ALL_UPLOADS
            * Its pointless. May change later on
            * Could use it to bring back files for a day. just NRN

        * Also Fix code base. I swear it looks like shit.
        * Save to mega every 12 hours (as It'll be slow if I do it every upload)
        * Should also probably switch to Async for speed boosts
        * When I wake up, push it onto github!! git push
'''
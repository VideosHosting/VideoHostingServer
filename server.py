from flask import Flask, request, jsonify, send_file
from pathlib import Path
from werkzeug.datastructures import ImmutableMultiDict, FileStorage
from collections import deque
from time import time
from typing import Any

#our own python files. We'll use names as a namespace.
import constants as const
import extras

app = Flask(__name__)

#routes
@app.route("/")
def home():
    return "Home"

@app.route("/upload", methods=['POST'])
def upload_files():
    files: ImmutableMultiDict[str, FileStorage] = request.files

    if not files:
        return jsonify({
            "ERROR": "No videos/images to upload"
        }), 422

    for name, file in files.items():
        filename: str | None = file.filename

        if not filename or filename == '':
            return jsonify({
                "ERROR": f"Image '{name}' does not have a filename"
            }), 404
        
        filename_path = Path(filename)
        suffix = filename_path.suffix.lower()

        if suffix in const.VIDEO_EXT: # Its a video
            filename_path = const.VIDEO / filename_path
        elif suffix in const.IMAGE_EXT:
            filename_path = const.IMAGE / filename_path
        else:
            return jsonify({
                "ERROR": f"File '{filename}' suffix '{suffix}' is NOT supported"
            }), 404
        
        if filename_path.is_file():
            return jsonify({
                "ERROR": f"File '{filename}' already exists. Choose a different name"
            })
        
        file.save(filename_path)
        const.CUR_UPLOADES.appendleft((str(filename_path), time()))

    # Can change this later to save to mega a day (saving like this can be slow)
    extras.save_to_mega((
        Path(file.filename)
        
        for file in files.values()
        if file.filename
    ))

    return jsonify({
        "SUCCESS": f"Uploaded {len(files)} file(s) Successfully"
    }), 201

@app.route("/attachments/<file_id>", methods=['GET'])
def serve_attachment(file_id: str):
    path: Path | None = extras.choose_correct_path(const.VIDEO / file_id, const.IMAGE / file_id)
    if not path:
        return jsonify({
            "ERROR": f"File '{file_id}' does not exist"
        }), 404
    
    return send_file(path)

def deque_to_list(deq: deque[Any]):
    lst: list[Any] = []

    while deq:
        lst.append(deq.pop())

    return lst

@app.route("/list", methods=['GET'])
def list_files():
    files: dict[str, list[str]] = {
        "Images": [],
        "Videos": [],
        "CUR_UPLOADS": deque_to_list(const.CUR_UPLOADES),
        "ALL_UPLOADS": const.ALL_UPLOADES
    }

    for images in const.IMAGE.iterdir():
        files["Images"].append(images.name)

    for videos in const.VIDEO.iterdir():
        files["Videos"].append(videos.name)
    
    return jsonify(files), 200

app.run(host='0.0.0.0', port=8080, debug=True)
from flask import Flask, request, jsonify, send_file
from apscheduler.schedulers.background import BackgroundScheduler # type:ignore
from pathlib import Path
from werkzeug.datastructures import ImmutableMultiDict, FileStorage
from time import time

import atexit

#our own python files. Not gonna wild card import but use it as a namespace
import constants as const
import extras

app = Flask(__name__)

#we'll use this to clean up
scheduler: BackgroundScheduler = BackgroundScheduler()
scheduler.add_job(func=extras.clear_cache, trigger='interval', seconds=const.TIME_LIMIT+1) #type: ignore
scheduler.start() #type:ignore

atexit.register(lambda: scheduler.shutdown()) #type:ignore

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

    saved_paths: list[Path] = []
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
        const.CUR_UPLOADS.appendleft(const.Upload(
            name=filename,
            timestamp=time()
        ))

        saved_paths.append(filename_path)

    extras.save_to_mega(saved_paths)

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
    
    return send_file(path, as_attachment=False, conditional=True)

@app.route("/list", methods=['GET'])
def list_files():
    return jsonify(extras.deque_to_list(const.CUR_UPLOADS))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(const.getenv("PORT", 10_000)), debug=True)
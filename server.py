from flask import Flask, request, jsonify, send_file
from apscheduler.schedulers.background import BackgroundScheduler # type:ignore
from pathlib import Path
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from time import time

import atexit

#our own python files. Not gonna wild card import but use it as a namespace
import modules.constants as const
import modules.extras as extras

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 1024

# print(f'{const._get_uploads_size():.2f}MB')

#limiter
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["10 per minute"],
    storage_uri="memory://"
)

#Update it before starting
const.SPACE_TAKEN = extras.get_uploads_size()

#we'll use this to clean up
scheduler: BackgroundScheduler = BackgroundScheduler(executors={"default": const.SCHEDULER_EXECUTOR  })
scheduler.add_job(func=extras.clear_cache, trigger='interval', seconds=const.CACHE_TIME_LIMIT+1) #type: ignore
scheduler.add_job(func=extras.upload_periodically, trigger='interval', seconds=const.UPLOAD_TIME_LIMIT+1)#type:ignore
scheduler.start() #type:ignore

atexit.register(lambda: scheduler.shutdown()) #type:ignore

#routes
@app.route("/")
def home():
    return "Home"

@app.route("/upload", methods=['POST'])
def upload_files():
    files = request.files

    if not files:
        return jsonify({
            "ERROR": "No videos/images to upload"
        }), 422

    saved_paths: list[Path] = []

    #we'll use key as a filename
    for file in files.values():
        filename = file.filename

        if not filename:
            return jsonify({
                "ERROR": f"One of the Images/Videos does not have a proper filename"
            }), 400
        
        suffix = Path(filename).suffix.lower()

        if suffix not in const.VIDEO_EXT and suffix not in const.IMAGE_EXT:
            return jsonify({
                "ERROR": f"File '{filename}' with suffix '{suffix}' is NOT supported"
            }), 400
        
        filename_path: Path = extras.generate_unique_name(
            const.VIDEO if suffix in const.VIDEO_EXT else const.IMAGE,
            suffix
        )
        
        # lock space on 800 MB (better to keep 200MB for extra space)
        with const.SPACE_TAKEN_LOCK:
            if const.SPACE_TAKEN >= 800:
                const.logger.error("Space limit reached!")

                const.EXECUTOR.submit(
                    extras.upload_periodically
                )
                const.EXECUTOR.submit(
                    extras.clear_cache, True
                )
                # Thread(target=extras.upload_periodically, daemon=True).start()
                # Thread(target=extras.clear_cache, args=(True,), daemon=True).start()
        
        try:
            file.save(filename_path)
        except Exception as e:
            #lingering data left behind
            if filename_path.is_file():
                filename_path.unlink()

            const.logger.error(f"Failed to save {filename} due to: {e}")
            return jsonify({"ERROR": f"Failed to save file '{filename}'"}), 500
        
        const.CUR_UPLOADS.set(const.Upload(
            name=filename_path.as_posix(),
            timestamp=time()
        ))

        const.logger.info(f"Successfully uploaded {filename_path}")
        with const.SPACE_TAKEN_LOCK:
            #so apparently calculations are kinda fucked
            const.SPACE_TAKEN = extras.get_uploads_size()

        saved_paths.append(filename_path)

    for file in saved_paths:
        const.UPLOAD_QUEUE.set(const.Upload(
            name=str(file),
            timestamp=0.0
        ))
    
    const.CUR_UPLOADS.commit()  # Save the current uploads to disk
    const.UPLOAD_QUEUE.commit()  # Save the upload queue to disk

    return jsonify({
        "SUCCESS": f"Uploaded {len(saved_paths)} file(s) Successfully",
        "FILES": [str(path.name) for path in saved_paths]
    }), 201

@app.route("/attachments/<file_id>", methods=['GET'])
@limiter.limit("100 per minute")
def serve_attachment(file_id: str):
    path: Path | None = extras.choose_correct_path(const.VIDEO / file_id, const.IMAGE / file_id)

    if not path:
        return jsonify({
            "ERROR": f"File '{file_id}' does not exist"
        }), 404
    
    return send_file(path, as_attachment=True, conditional=True)

@app.route("/list", methods=['GET'])
def list_files():
    with const.SPACE_TAKEN_LOCK:
        return jsonify({
            "SPACE": f'{const.SPACE_TAKEN:_.2f}MBs',
            "FILES": const.CUR_UPLOADS[:]
        })

@app.route("/upload_queue", methods=['GET'])
def upload_queue():
    return jsonify([
        path.name
        for path in const.UPLOAD_QUEUE
    ])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10_000, debug=True)
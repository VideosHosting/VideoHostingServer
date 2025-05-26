from pathlib import Path
from json import dumps, loads
from typing import Any, NamedTuple
from threading import Lock

Upload = NamedTuple('Upload', [('name', str), ('timestamp', float)])

#custom file class for json.
class File:
    __filename: Path
    __json: list[Upload]
    __lock: Lock

    def __init__(self, filename: str | Path, data: list[tuple[str, int]] | None=None):
        self.__filename = filename if isinstance(filename, Path) else Path(filename)
        self.__lock = Lock()

        is_file = self.__filename.is_file()
        if not is_file:
            self.__filename.touch()

        #yikes, might be overkill? 
        self.__json = (
            self.__to_upload(data)
            if data else
            self.__to_upload(loads(self.__filename.read_text(encoding='utf-8')))
            if is_file else
            []
        )

    def set(self, value: Upload):
        with self.lock:
            self.__json.append(value)

    def commit(self):
        with self.lock:
            #although checking if it exists multiple times may be a problem, Its fine in this case because I don't give a shit
            self.__filename.touch(exist_ok=True)

            self.__filename.write_text(dumps(
                self.__json, indent=4
            ))

    #give it the lock for other threads to use
    @property
    def lock(self):
        return self.__lock

    def get_json(self) -> list[Upload]:
        return self.__json
    
    @classmethod
    def from_json(cls, filename: str | Path, json: list[Upload]):
        file: Path = filename if isinstance(filename, Path) else Path(filename)

        file.touch()

        file.write_text(dumps(
            json, indent=4
        ))

        return cls(file)
    
    def __to_upload(self, json: list[tuple[str, int]]) -> list[Upload]:
        lst: list[Upload] = list()

        for json_list in json:
            lst.append(Upload(
                name=json_list[0],
                timestamp=json_list[1]
            ))

        return lst
    
    def clear(self):
        with self.lock:
            self.__filename.unlink(missing_ok=True)
            self.__filename.touch()
            self.__json.clear()

    def copy(self):
        with self.lock:
            return self.__json.copy()

    def __getitem__(self, key: int | slice) -> Upload | list[Upload]:
        with self.lock:
            return self.__json[key]
    
    def __setitem__(self, key: int | slice, value: Any):
        with self.lock:
            self.__json[key] = value

    def __iter__(self):
        with self.lock:
            return iter(self.__json)

    def __del__(self):
        self.commit()

if __name__ == "__main__":
    #So glad dumps supports NamedTuples 😭
    file = File.from_json("Assets/CUR_UPLOADS.json", [
        Upload(name="10", timestamp=10.5),
        Upload(name="30", timestamp=20.56)
    ])

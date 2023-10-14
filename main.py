import json
from datetime import datetime
from pathlib import Path

FILE = "./storage/data.json"


def save_message(username, message):
    try:
        with open(FILE, "r+") as fh:
            data = json.loads(fh.read())
            data[str(datetime.now())] = {"username": username, 'message': message}
            fh.seek(0)
            fh.write(json.dumps(data))
    except FileNotFoundError:
        Path("./storage/").mkdir(exist_ok=True)
        with open(FILE, "w") as fh:
            fh.write(json.dumps({}))
        save_message(username, message)


if __name__ == "__main__":
    save_message("Vel", "First mes.")


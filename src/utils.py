import os
from gi.repository import Gio


def get_audio_files_in_dir(dir_path: str) -> list[str]:
    files = []
    for p in os.listdir(dir_path):
        content_type, _ = Gio.content_type_guess(p)
        if "audio" not in content_type:
            continue

        if not os.path.isfile(os.path.join(dir_path, p)):
            continue

        files.append(p)
    return files

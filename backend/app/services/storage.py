from __future__ import annotations

import abc
import re
import shutil
from pathlib import Path

_UNSAFE = re.compile(r'[\\/:*?"<>|]+')

def safe_folder_name(name: str) -> str:
    cleaned = _UNSAFE.sub("-", name).strip(" .")
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned or "untitled"

class ObjectStorage(abc.ABC):
    @abc.abstractmethod
    def put_product_images(
        self, product_name: str, image_paths: list[Path]
    ) -> dict:
        ...

class LocalObjectStorage(ObjectStorage):
    def __init__(self, root: Path) -> None:
        self.root = root

    def put_product_images(
        self, product_name: str, image_paths: list[Path]
    ) -> dict:
        folder = self.root / safe_folder_name(product_name)
        folder.mkdir(parents=True, exist_ok=True)
        written: list[str] = []
        for i, src in enumerate(image_paths, start=1):
            dst = folder / f"image_{i}{src.suffix or '.jpg'}"
            shutil.copyfile(src, dst)
            written.append(str(dst))
        return {"folder": str(folder), "written": written}

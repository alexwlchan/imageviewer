#!/usr/bin/env python3

import imghdr
import json
import os
import re
import subprocess
import sys
import tempfile
import webbrowser

from jinja2 import Environment, FileSystemLoader
from PIL import Image
import tqdm
from unidecode import unidecode

from tint_colors import choose_tint_color_for_file


CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".cache")

os.makedirs(CACHE_DIR, exist_ok=True)


def get_file_paths_under(root):
    """Generates the paths to every file under ``root``."""
    if not os.path.isdir(root):
        raise ValueError(f"Cannot find files under non-existent directory: {root!r}")

    for dirpath, _, filenames in os.walk(root):
        for f in filenames:
            yield os.path.join(dirpath, f)


def get_image_paths_under(root):
    for path in get_file_paths_under(root):
        if path.endswith(".md"):
            continue

        if imghdr.what(path) is not None:
            yield path


def slugify(u):
    """Convert Unicode string into blog slug."""
    u = re.sub("[–—/:;,.]", "-", u)  # replace separating punctuation
    a = unidecode(u).lower()  # best ASCII substitutions, lowercased
    a = re.sub(r"[^a-z0-9 -]", "", a)  # delete any other characters
    a = a.replace(" ", "-")  # spaces to hyphens
    a = re.sub(r"-+", "-", a)  # condense repeated hyphens
    return a


def as_hex(color):
    r, g, b = color
    return "#%02x%02x%02x" % (int(r * 255), int(g * 255), int(b * 255))


class ImageViewerCache:
    def __init__(self, root):
        self.root = root
        self._cache_entry_path = os.path.join(CACHE_DIR, slugify(root))

    def __enter__(self):
        try:
            with open(self._cache_entry_path) as infile:
                self._data = json.load(infile)
        except FileNotFoundError:
            self._data = {"root": self.root, "images": {}}

        assert self._data["root"] == self.root

        self._old_images = self._data["images"]
        self._data["images"] = {}

        return self

    def write(self):
        with open(self._cache_entry_path, "w") as outfile:
            outfile.write(json.dumps(self._data, indent=2, sort_keys=True))

    def __exit__(self, *exc_details):
        self.write()

    def add_image(self, path):
        rel_path = os.path.relpath(path, root)

        if (
            rel_path in self._old_images
            and self._old_images[rel_path]["mtime"] == os.stat(path).st_mtime
        ):
            self._data["images"][rel_path] = self._old_images[rel_path]
        else:
            im = Image.open(path)

            self._data["images"][rel_path] = {
                "mtime": os.stat(path).st_mtime,
                "dimensions": {
                    "width": im.width,
                    "height": im.height,
                },
                "tint_color": as_hex(choose_tint_color_for_file(path)),
            }

    def get_images(self):
        return sorted(
            self._data["images"].items(), key=lambda im: im[1]["mtime"], reverse=True
        )


if __name__ == "__main__":
    try:
        root = sys.argv[1]
    except IndexError:
        sys.exit(f"Usage: {__file__}")

    with ImageViewerCache(root) as cache:
        for path in tqdm.tqdm(list(get_image_paths_under(root))):
            cache.add_image(path)

        environment = Environment(loader=FileSystemLoader("templates/"))
        template = environment.get_template("index.html")

        _, tmp_path = tempfile.mkstemp(suffix=".html")

        with open(tmp_path, "w") as outfile:
            outfile.write(
                template.render(
                    root=os.path.abspath(root),
                    images=cache.get_images(),
                    static_dir=os.path.join(
                        os.path.dirname(os.path.abspath(__file__)), "static"
                    ),
                )
            )

        webbrowser.open('file://' + tmp_path)

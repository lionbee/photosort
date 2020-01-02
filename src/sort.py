#!/usr/bin/env python3
import argparse
import os
import sys

from datetime import datetime
from exif import Image
from typing import Callable, List, Optional


def _parse_exif_datetime(d: str) -> Optional[datetime]:
    try:
        return datetime.strptime(d, '%Y:%m:%d %H:%M:%S')
    except:
        return None


def _get_exif_datetime(path: str) -> Optional[datetime]:
    try:
        with open(path, 'rb') as image_file:
            ex = Image(image_file)
            if ex.has_exif:
                return _parse_exif_datetime(ex.datetime_original)
    except Exception as ex:
        print("Error: {0}: {1}".format(path, ex), file=sys.stderr)
    return None


def get_path_str_maker(target_dir: str) -> Callable[[str], Optional[str]]:
    def make_path_str(src: str) -> Optional[str]:
        dt = _get_exif_datetime(src)
        if dt is None:
            return None
        filename = os.path.basename(src)
        new_dir = os.path.join(target_dir, str(
            dt.year), "{0:02}".format(dt.month))
        new_filename = "{dt.day:02}_{dt.hour:02}{dt.minute:02}{dt.second:02}_{filename}".format(
            dt=dt, filename=filename)
        return os.path.join(new_dir, new_filename)

    return make_path_str


def get_photo_mover(make_target_path_str: Callable[[str], Optional[str]]) -> Callable[[str], None]:
    def move_photo(src: str) -> None:
        print("processing: {0}".format(src))
        target_path = make_target_path_str(src)
        if target_path:
            target_dir = os.path.dirname(target_path)
            print("{0} -> {1}".format(src, target_path))
            os.makedirs(target_dir, exist_ok=True)
            os.rename(src, target_path)
    return move_photo


def _walk_source_dir(root: str, fn: Callable[[str], None]) -> None:
    '''
    Walk a directory applying a function to each file in the directory
    '''
    walk_root: str
    files: List[str]
    for walk_root, _, files in os.walk(root):
        for f in files:
            file_path = os.path.join(walk_root, f)
            fn(file_path)


def move_all_photos(src: str, make_target_path_str: Callable[[str], Optional[str]]) -> None:
    move_photo = get_photo_mover(make_target_path_str)
    _walk_source_dir(src, move_photo)


def sort_photos(src: str, target: str) -> None:
    make_target_path_str = get_path_str_maker(target)
    move_all_photos(src, make_target_path_str)


def is_sub_path(src: str, target: str) -> bool:
    return target.startswith(src)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Sort photos based on EXIF.')
    parser.add_argument('source', type=str,
                        help='The folder to be be sorted')
    parser.add_argument('target', type=str,
                        help='Where the sorted folders will be moved to')
    args = parser.parse_args()

    src = os.path.realpath(args.source)
    target = os.path.realpath(args.target)

    if is_sub_path(src, target):
        print('target cannot be a sub folder of source', file=sys.stdout)
        sys.exit(1)

    sort_photos(src, target)

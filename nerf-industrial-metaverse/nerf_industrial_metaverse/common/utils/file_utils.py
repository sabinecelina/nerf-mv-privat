# -*- coding: utf-8 -*-

import os
import os.path as osp
import shutil
from shutil import copyfile, copytree, ignore_patterns
import zipfile
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'zip', 'r3d'}


def remove_if_exists(file):
    """Remove file if it exists"""
    if os.path.exists(file):
        os.remove(file)


def remove_dir_if_exists(folder):
    """Remove directory with all files if it exists"""
    if os.path.exists(folder):
        shutil.rmtree(folder, ignore_errors=True)


def remove_files(scene_dir, cfgs_json, logger):
    if not osp.exists(osp.join(scene_dir, cfgs_json.name)):
        logger.add_lod("No transform.json exists. Folders will not be deleted")
    else:
        colmap_sparse = osp.join(scene_dir, "sparse")
        colmap_db = osp.join(scene_dir, "database.db")
        remove_dir_if_exists(colmap_sparse)
        remove_if_exists(colmap_db)
    logger.add_log(
        f"Removed files that are not be used anymore: {colmap_sparse}, {colmap_db}")


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_file_type(filename):
    extension = filename.rsplit('.', 1)[1].lower()
    return extension


def get_filename_without_extension(filename):
    return filename.split('.')[0]


def unzip(UPLOAD_FOLDER, filename):
    file_path = os.path.join(
        UPLOAD_FOLDER, filename + ".r3d")
    unzip_folder = os.path.join(
        UPLOAD_FOLDER, filename)

    # Convert R3D to ZIP format
    zip_file_path = os.path.join(
        UPLOAD_FOLDER, get_filename_without_extension(filename) + ".zip")
    try:
        if not osp.exists(zip_file_path):
            shutil.copyfile(file_path, zip_file_path)
    except Exception as e:
        print("Error occurred during conversion:", str(e))
    try:
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(unzip_folder)
    except Exception as e:
        print("Error occurred during extraction:", str(e))
    try:
        if not osp.isdir(osp.join("data", filename)):
            shutil.move(unzip_folder, "data")
    except Exception as e:
        print("Error occured because folder already exists. ")

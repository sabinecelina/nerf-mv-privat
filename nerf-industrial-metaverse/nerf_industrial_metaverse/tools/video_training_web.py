#!/usr/bin/python

import os
import os.path as osp
import sys
import shutil
import numpy as np
from pathlib import Path
from nerf_industrial_metaverse.common.utils.file_utils import *
from nerf_industrial_metaverse.common.utils.img_utils import get_n_img_in_dir, is_img_ext
from nerf_industrial_metaverse.common.utils.video_utils import get_video_metadata, extract_video
from nerf_industrial_metaverse.common.utils.img_utils import get_n_img_in_dir, get_first_img, get_image_metadata
from nerf_industrial_metaverse.common.colmap.colmap_wrapper import *
from nerf_industrial_metaverse.common.colmap.colmap_func import *
from nerf_industrial_metaverse.common.utils.json_utils import *
from nerf_industrial_metaverse.common.utils.transform_utils import *


def extract_images(logger, cfgs):
    video_path = cfgs.data.video_path
    logger.add_log(
        'Start to extract images from video. Video path: {}'.format(video_path))
    assert osp.exists(video_path), 'No video file for processing...'
    scene_name = cfgs.data.scene_name
    if not osp.isdir(cfgs.dir.data_dir):
        os.mkdir(cfgs.dir.data_dir)
    scene_dir = osp.join(cfgs.dir.data_dir, scene_name)
    logger.add_log('Write to directory {}'.format(scene_dir))
    scene_img_dir = osp.join(scene_dir, 'images')
    if osp.isdir(scene_dir):
        logger.add_log('Already exist {}. Will be deleted'.format(scene_dir))
        if False != cfgs.overwrite or (
                input(
                    f"warning! folder '{scene_dir}' will be deleted/replaced. continue? (Y/n)").lower().strip() + "y")[
                :1] == "y":
            pass
        else:
            sys.exit(1)
        try:
            shutil.rmtree(scene_dir)
        except:
            pass
    os.mkdir(scene_dir)
    os.mkdir(scene_img_dir)
    # get meta data
    num_frame, width, height, _ = get_video_metadata(video_path)
    logger.add_log(
        'Original video information: num_frame-{}, shape-{}/{}(w/h)'.format(num_frame, width, height))
    logger.add_log(
        'Video Downsample: {}, Image Downsample {}'.format(cfgs.data.video_downsample, cfgs.data.image_downsample))
    # extract frames and write to output dir
    extract_video(
        video_path,
        scene_img_dir,
        video_downsample=cfgs.data.video_downsample,
        image_downsample=cfgs.data.image_downsample
    )

    logger.add_log('    Total image number extract: {}'.format(
        get_n_img_in_dir(scene_img_dir)))
    img_w, img_h, img_c = get_image_metadata(
        osp.join(scene_img_dir, get_first_img(scene_img_dir)))
    logger.add_log('    Extract image shape: {}/{}(w/h)'.format(img_w, img_h))


def run_poses(logger, cfgs):
    scene_name = cfgs.data.scene_name
    scene_dir = osp.join(cfgs.dir.data_dir, scene_name)
    if not osp.isdir(scene_dir):
        logger.add_log(
            '{} does not exist. Extract video or put image first...'.format(scene_dir))
        exit()

    logger.add_log(
        'Start to run COLMAP and estimate cam_poses... Scene dir: {}'.format(scene_dir))
    try:
        estimate_poses(scene_dir, logger, cfgs.data.colmap.match_type)
    except subprocess.CalledProcessError:
        logger.add_log(
            'Can not run poses estimation. Check {} for detail...'.format(
                osp.join(scene_dir, 'colmap_output.txt')),
            level='Error'
        )
        remove_dir_if_exists(osp.join(scene_dir, 'sparse'))


def export_json(logger, cfgs):
    cfgs_json = cfgs.json
    scene_name = cfgs.data.scene_name
    scene_dir = osp.join(cfgs.dir.data_dir, scene_name)
    if not osp.isdir(scene_dir):
        logger.add_log(
            '{} does not exist. Extract video or put image first...'.format(scene_dir))
        exit()
    colmap_output_dir = osp.join(scene_dir, "colmap_text")
    if not osp.isdir(colmap_output_dir):
        logger.add_log(
            '{} does not exist. Run colmap first...'.format(scene_dir))
        exit()

    logger.add_log(
        'Start to create transform.json file ... Scene dir: {}'.format(scene_dir))

    try:
        process_json_file(scene_dir, cfgs_json, logger)
    except subprocess.CalledProcessError:
        logger.add_log(
            'Can not create transform.json file. Check {} for detail...'.format(
                osp.join(scene_dir, 'export_json.txt')),
            level='Error'
        )


def record_to_json(logger, cfgs):
    cfgs_iphone = cfgs.iphone
    cfgs_json = cfgs.json
    scene_name = cfgs.data.scene_name
    scene_dir = osp.join(cfgs.dir.data_dir, scene_name)
    if not osp.exists(osp.join(scene_dir, "metadata")):
        logger.add_log(
            '{} does not exist.  Please use the right r3d format...'.format(scene_dir))
        exit()
    logger.add_log(
        'Start to create transform.json file ... Scene dir: {}'.format(scene_dir))
    try:
        iphone2json(scene_dir, cfgs_iphone, cfgs_json, logger)
    except subprocess.CalledProcessError:
        logger.add_log(
            'Can not create transform.json file. Check {} for detail...'.format(
                osp.join(scene_dir, 'export_json.txt')),
            level='Error'
        )

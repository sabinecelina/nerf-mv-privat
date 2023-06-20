#!/usr/bin/python

import os
import os.path as osp
import sys
import shutil

from nerf_industrial_metaverse.common.utils.cfgs_utils import parse_configs
from nerf_industrial_metaverse.common.utils.logger import Logger
from nerf_industrial_metaverse.common.utils.video_utils import get_video_metadata, extract_video
from nerf_industrial_metaverse.common.utils.img_utils import get_n_img_in_dir, get_first_img, get_image_metadata

def entrypoint():
    # parse args, logger
    cfgs = parse_configs()
    logger = Logger()

    # get video from path
    video_path = cfgs.data.video_path
    logger.add_log('Start to extract images from video. Video path: {}'.format(video_path))
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
    logger.add_log('Original video information: num_frame-{}, shape-{}/{}(w/h)'.format(num_frame, width, height))
    logger.add_log(
        'Video Downsample: {}, Image Downsample {}'.format(cfgs.data.video_downsample, cfgs.data.image_downsample))
    # extract frames and write to output dir
    extract_video(
        video_path,
        scene_img_dir,
        video_downsample=cfgs.data.video_downsample,
        image_downsample=cfgs.data.image_downsample
    )

    logger.add_log('    Total image number extract: {}'.format(get_n_img_in_dir(scene_img_dir)))
    img_w, img_h, img_c = get_image_metadata(osp.join(scene_img_dir,get_first_img(scene_img_dir)))
    logger.add_log('    Extract image shape: {}/{}(w/h)'.format(img_w, img_h))


if __name__ == '__main__':
    entrypoint()
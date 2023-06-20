import os
import shutil
from subprocess import check_output

import numpy as np
from .colmap_wrapper import run_colmap
from nerf_industrial_metaverse.common.utils.img_utils import get_n_img_in_dir

def estimate_poses(scene_dir, logger, match_type, factors=None):
    """estimate poses by colmap. images are at scene_dir/images.

    Args:
        scene_dir: scene_dir contains image and poses
        logger: logger
        match_type: ['sequential_matcher', 'exhaustive_matcher']
        factors: list of int. Factor > 1 means smaller, <1 means larger

    Returns:
        Write .bins file
    """
    filenames = ['{}.bin'.format(f) for f in ['cameras', 'images', 'points3D']]
    if os.path.exists(os.path.join(scene_dir, 'sparse/0')):
        cur_files = os.listdir(os.path.join(scene_dir, 'sparse/0'))
    else:
        cur_files = []

    if not all([f in cur_files for f in filenames]):
        logger.add_log('Need to run construct from colmap...')
        # sparse reconstruct from command line
        run_colmap(scene_dir, logger, match_type)
    else:
        logger.add_log('No need to run reconstruction again...')

    logger.add_log('Finish processing in dir: {}'.format(scene_dir))


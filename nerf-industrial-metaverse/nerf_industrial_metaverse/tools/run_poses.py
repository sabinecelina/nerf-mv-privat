import os.path as osp
import shutil
import subprocess
import numpy as np
from subprocess import check_output

from nerf_industrial_metaverse.common.utils.file_utils import remove_dir_if_exists
from nerf_industrial_metaverse.common.utils.cfgs_utils import *
from nerf_industrial_metaverse.common.utils.img_utils import get_n_img_in_dir, is_img_ext
from nerf_industrial_metaverse.common.utils.logger import *
from nerf_industrial_metaverse.common.colmap.colmap_wrapper import *
from nerf_industrial_metaverse.common.colmap.colmap_func import *

def entrypoint():
    cfgs = parse_configs()
    logger = Logger()
    scene_name = cfgs.data.scene_name
    scene_dir = osp.join(cfgs.dir.data_dir, scene_name)
    if not osp.isdir(scene_dir):
        logger.add_log('{} does not exist. Extract video or put image first...'.format(scene_dir))
        exit()

    logger.add_log('Start to run COLMAP and estimate cam_poses... Scene dir: {}'.format(scene_dir))
    try:
        estimate_poses(scene_dir, logger, cfgs.data.colmap.match_type)
    except subprocess.CalledProcessError:
        logger.add_log(
            'Can not run poses estimation. Check {} for detail...'.format(osp.join(scene_dir, 'colmap_output.txt')),
            level='Error'
        )
        remove_dir_if_exists(osp.join(scene_dir, 'sparse'))


if __name__ == '__main__':
    entrypoint()

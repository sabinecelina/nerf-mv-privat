import os.path as osp
import shutil
import subprocess
import numpy as np
from subprocess import check_output

from nerf_industrial_metaverse.common.utils.json_utils import *
from nerf_industrial_metaverse.common.utils.cfgs_utils import *
from nerf_industrial_metaverse.common.utils.logger import *
from nerf_industrial_metaverse.common.utils.file_utils import *
from nerf_industrial_metaverse.common.utils.transform_utils import *


def entrypoint():
    cfgs = parse_configs()
    logger = Logger()
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


if __name__ == '__main__':
    entrypoint()

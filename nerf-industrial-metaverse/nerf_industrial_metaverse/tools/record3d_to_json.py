import os
import os.path as osp
import numpy as np
import json
import copy
from pyquaternion import Quaternion
from tqdm import tqdm
from PIL import Image
import subprocess
from pathlib import Path

from nerf_industrial_metaverse.common.utils.json_utils import *
from nerf_industrial_metaverse.common.utils.cfgs_utils import *
from nerf_industrial_metaverse.common.utils.logger import *
from nerf_industrial_metaverse.common.utils.transform_utils import * 

def entrypoint():
    cfgs = parse_configs()
    logger = Logger()
    cfgs_iphone = cfgs.iphone
    cfgs_json = cfgs.json
    scene_name = cfgs.data.scene_name
    scene_dir = osp.join(cfgs.dir.data_dir, scene_name)
    video_path = cfgs.data.video_path
    print(video_path)
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


if __name__ == '__main__':
    entrypoint()

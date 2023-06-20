import os
import subprocess
import os.path as osp
import argparse
import sys
from nerf_industrial_metaverse.common.utils.cfgs_utils import *
from nerf_industrial_metaverse.common.utils.logger import *
import time


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--configs", type=str, help="Path to the config file")
    return parser.parse_args()


def entrypoint():
    cfgs = parse_configs()
    args = parse_args()
    logger = Logger()
    scene_name = cfgs.data.scene_name
    data_dir = cfgs.dir.data_dir
    scene_dir = osp.join(data_dir, scene_name)
    if not valid_key_in_cfgs(cfgs, 'iphone'):
        if not osp.isdir(osp.join(scene_dir, "images")):
            logger.add_log('--- EXTRACT IMAGES FROM VIDEO ---')
            extract_video_cmd = ["ngp-extract", "--configs", args.configs]
            extract_video_output = subprocess.check_output(
                extract_video_cmd, universal_newlines=True)
            logger.add_log(
                f'--- DONE EXTRACT IMAGES FROM VIDEO --- {extract_video_output}')
        if not osp.exists(osp.join(scene_dir, "colmap_output.txt")):
            logger.add_log('--- RUN COLMAP ---')
            run_colmap_cmd = ["ngp-colmap", "--configs", args.configs]
            run_colmap_output = subprocess.check_output(
                run_colmap_cmd, universal_newlines=True)
            logger.add_log(f'--- DONE RUN COLMAP --- {run_colmap_output}')
        if not osp.exists(osp.join(scene_dir, cfgs.json.name)):
            logger.add_log('--- EXPORT TRANSFORM.JSON ---')
            export_json_cmd = ["ngp-json", "--configs", args.configs]
            export_json_output = subprocess.check_output(
                export_json_cmd, universal_newlines=True)
            logger.add_log(
                f'--- DONE EXPORT TRANSFORM.JSON --- {export_json_output}')
        if osp.exists(osp.join(scene_dir, cfgs.json.name)) and osp.isdir(osp.join(scene_dir, "images")):
            logger.add_log('--- START TRAINING ---')
            train_ngp_cmd = ["ngp-train", "--configs", args.configs]
            start_time = time.time()
            train_ngp_output = subprocess.check_output(
                train_ngp_cmd, stdin=None, stderr=None, universal_newlines=True)
            end_time = time.time()
            total_time = end_time - start_time
            logger.add_log(f"Processing time: {total_time} seconds")
            logger.add_log(f'--- DONE TRAINING SCENE ---')
    else:
        if not osp.exists(osp.join(scene_dir, "metadata")):
            logger.add_log(
                '--- NO METADATA FILE WAS FOUND: PLEASE USE R3D FORMAT ---')
            exit()
        if not osp.exists(osp.join(scene_dir, cfgs.json.name)):
            logger.add_log('--- EXPORT TRANSFORM.JSON ---')
            export_json_cmd = ["ngp-iphone", "--configs", args.configs]
            export_json_output = subprocess.check_output(
                export_json_cmd, universal_newlines=True)
            logger.add_log(
                f'--- DONE EXPORT TRANSFORM.JSON --- {export_json_output}')
            print(osp.join(scene_dir, cfgs.json.name))
        if osp.exists(osp.join(scene_dir, cfgs.json.name)):
            train_ngp_cmd = f"ngp-train --configs {args.configs}"
            logger.add_log(
                f"Following Configuration is used for training: {train_ngp_cmd}")
            train_ngp_cmd = ["ngp-train", "--configs", args.configs]
            start_time = time.time()
            train_ngp_output = subprocess.check_output(
                train_ngp_cmd, stdin=None, stderr=None, universal_newlines=True)
            end_time = time.time()
            total_time = end_time - start_time
            logger.add_log(f"Processing time: {total_time} seconds")
            logger.add_log(f'--- DONE TRAINING SCENE ---')

if __name__ == '__main__':
    entrypoint()

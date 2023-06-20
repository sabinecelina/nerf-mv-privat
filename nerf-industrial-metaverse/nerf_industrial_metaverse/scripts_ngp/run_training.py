#!/usr/bin/env python3

# Copyright (c) 2020-2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.

import argparse
import os
import commentjson as json

import numpy as np

import shutil
import time

from nerf_industrial_metaverse.scripts_ngp.common import *
from nerf_industrial_metaverse.scripts_ngp.scenes import *
from nerf_industrial_metaverse.common.utils.cfgs_utils import *
from nerf_industrial_metaverse.common.utils.logger import *
from tqdm import tqdm

import pyngp as ngp  # noqa


def get_scene(scene):
    for scenes in [scenes_sdf, scenes_nerf, scenes_image, scenes_volume]:
        if scene in scenes:
            return scenes[scene]
    return None


def run_training(logger, args):
    scene_name = args.data.scene_name
    data_dir = args.dir.data_dir
    scene_dir = os.path.join(data_dir, scene_name)
    args = args.train
    testbed = ngp.Testbed()
    testbed.root_dir = ROOT_DIR
    for file in args.files:
        scene_info = get_scene(file)
        if scene_info:
            file = os.path.join(scene_info["data_dir"], scene_info["dataset"])
        testbed.load_file(file)

    if valid_key_in_cfgs(args, 'scene'):
        scene_info = get_scene(args.scene)
        if scene_info is not None:
            scene_dir = os.path.join(
                scene_info["data_dir"], scene_info["dataset"])
            if not args.network and "network" in scene_info:
                args.network = scene_info["network"]
        try:
            testbed.load_training_data(scene_dir)
        except Exception as e:
            logger.add_log(f"{e}")
            logger.add_log("Please subsample the video with changing the configs and try again")
            exit()

    if valid_key_in_cfgs(args, 'load_snapshot'):
        scene_info = get_scene(args.load_snapshot)
        if scene_info is not None:
            args.load_snapshot = default_snapshot_filename(scene_info)
        testbed.load_snapshot(args.load_snapshot)
    elif args.network:
        testbed.reload_network_from_file(args.network)

    ref_transforms = {}
    if valid_key_in_cfgs(args, 'screenshot_transforms'):
        logger.add_log(
            f"Screenshot transforms from {args.screenshot_transforms}")
        with open(os.path.join(scene_dir, args.screenshot_transforms)) as f:
            ref_transforms = json.load(f)

    testbed.nerf.sharpen = float(args.sharpen)
    testbed.exposure = args.exposure
    testbed.shall_train = args.train if valid_key_in_cfgs(
        args, 'gui') else True

    testbed.nerf.render_with_lens_distortion = True

    network_stem = os.path.splitext(os.path.basename(args.network))[
        0] if args.network else "base"

    if args.near_distance >= 0.0:
        logger.add_log("NeRF training ray near_distance ", args.near_distance)
        testbed.nerf.training.near_distance = args.near_distance

    if valid_key_in_cfgs(args, 'nerf_compatibility'):
        logger.add_log(f"NeRF compatibility mode enabled")

        # Prior nerf papers accumulate/blend in the sRGB
        # color space. This messes not only with background
        # alpha, but also with DOF effects and the likes.
        # We support this behavior, but we only enable it
        # for the case of synthetic nerf data where we need
        # to compare PSNR numbers to results of prior work.
        testbed.color_space = ngp.ColorSpace.SRGB

        # No exponential cone tracing. Slightly increases
        # quality at the cost of speed. This is done by
        # default on scenes with AABB 1 (like the synthetic
        # ones), but not on larger scenes. So force the
        # setting here.
        testbed.nerf.cone_angle_constant = 0

        # Match nerf paper behaviour and train on a fixed bg.
        testbed.nerf.training.random_bg_color = False

    old_training_step = 0
    n_steps = args.n_steps

    # If we loaded a snapshot, didn't specify a number of steps, _and_ didn't open a GUI,
    # don't train by default and instead assume that the goal is to render screenshots,
    # compute PSNR, or render a video.
    if n_steps < 0 and (not valid_key_in_cfgs(args, 'load_snapshot') or valid_key_in_cfgs(args, 'gui')):
        n_steps = 35000

    tqdm_last_update = 0
    if n_steps > 0:
        with tqdm(desc="Training", total=n_steps, unit="steps") as t:
            while testbed.frame():
                if testbed.want_repl():
                    repl(testbed)
                # What will happen when training is done?
                if testbed.training_step >= n_steps:
                    if valid_key_in_cfgs(args, 'gui'):
                        testbed.shall_train = False
                    else:
                        break

                # Update progress bar
                if testbed.training_step < old_training_step or old_training_step == 0:
                    old_training_step = 0
                    t.reset()

                now = time.monotonic()
                if now - tqdm_last_update > 0.1:
                    t.update(testbed.training_step - old_training_step)
                    t.set_postfix(loss=testbed.loss)
                    old_training_step = testbed.training_step
                    tqdm_last_update = now
                    logger.add_log(
                        f'progress step: {testbed.training_step}, loss: {testbed.loss}', level="TRAINING")
    else:
        logger.add_log(f'DONE TRAINING WITH : {n_steps}')
    if valid_key_in_cfgs(args, 'save_snapshot'):
        testbed.save_snapshot(args.save_snapshot, False)
        logger.add_log(f'saved snapshot "{args.save_snapshot}"')

    if valid_key_in_cfgs(args, 'test_transforms'):
        logger.add_log("Evaluating test transforms from ",
                       args.test_transforms)
        with open(args.test_transforms) as f:
            test_transforms = json.load(f)
        data_dir = os.path.dirname(args.test_transforms)
        totmse = 0
        totpsnr = 0
        totssim = 0
        totcount = 0
        minpsnr = 1000
        maxpsnr = 0

        # Evaluate metrics on black background
        testbed.background_color = [0.0, 0.0, 0.0, 1.0]

        # Prior nerf papers don't typically do multi-sample anti aliasing.
        # So snap all pixels to the pixel centers.
        testbed.snap_to_pixel_centers = True
        spp = 8

        testbed.nerf.render_min_transmittance = 1e-4

        testbed.shall_train = False
        testbed.load_training_data(args.test_transforms)

        with tqdm(range(testbed.nerf.training.dataset.n_images), unit="images", desc=f"Rendering test frame") as t:
            for i in t:
                resolution = testbed.nerf.training.dataset.metadata[i].resolution
                testbed.render_ground_truth = True
                testbed.set_camera_to_training_view(i)
                ref_image = testbed.render(
                    resolution[0], resolution[1], 1, True)
                testbed.render_ground_truth = False
                image = testbed.render(resolution[0], resolution[1], spp, True)

                if i == 0:
                    write_image(f"ref.png", ref_image)
                    write_image(f"out.png", image)

                    diffimg = np.absolute(image - ref_image)
                    diffimg[..., 3:4] = 1.0
                    write_image("diff.png", diffimg)

                A = np.clip(linear_to_srgb(image[..., :3]), 0.0, 1.0)
                R = np.clip(linear_to_srgb(ref_image[..., :3]), 0.0, 1.0)
                mse = float(compute_error("MSE", A, R))
                ssim = float(compute_error("SSIM", A, R))
                totssim += ssim
                totmse += mse
                psnr = mse2psnr(mse)
                totpsnr += psnr
                minpsnr = psnr if psnr < minpsnr else minpsnr
                maxpsnr = psnr if psnr > maxpsnr else maxpsnr
                totcount = totcount + 1
                t.set_postfix(psnr=totpsnr / (totcount or 1))

        psnr_avgmse = mse2psnr(totmse / (totcount or 1))
        psnr = totpsnr / (totcount or 1)
        ssim = totssim / (totcount or 1)
        logger.add_log(
            f"PSNR={psnr} [min={minpsnr} max={maxpsnr}] SSIM={ssim}")

    if valid_key_in_cfgs(args, 'save_mesh'):
        res = args.marching_cubes_res or 256
        logger.add_log(
            f"Generating mesh via marching cubes and saving to {args.save_mesh}. Resolution=[{res},{res},{res}]")
        testbed.compute_and_save_marching_cubes_mesh(
            args.save_mesh, [res, res, res])

    if ref_transforms:
        testbed.fov_axis = 0
        testbed.fov = ref_transforms["camera_angle_x"] * 180 / np.pi
        if not valid_key_in_cfgs(args, 'screenshot_transforms'):
            args.screenshot_frames = range(len(ref_transforms["frames"]))
        args.screenshot_frames = range(len(ref_transforms["frames"]))
        for idx in args.screenshot_frames:
            f = ref_transforms["frames"][int(idx)]
            cam_matrix = f["transform_matrix"]
            testbed.set_nerf_camera_matrix(np.matrix(cam_matrix)[:-1, :])
            outname = os.path.join(args.screenshot_dir,
                                   os.path.basename(f["file_path"]))

            # Some NeRF datasets lack the .png suffix in the dataset metadata
            if not os.path.splitext(outname)[1]:
                outname = outname + ".png"

            logger.add_log(f"rendering {outname}")
            image = testbed.render(args.width or int(ref_transforms["w"]), args.height or int(ref_transforms["h"]),
                                   args.screenshot_spp, True)
            os.makedirs(os.path.dirname(outname), exist_ok=True)
            write_image(outname, image)
    elif valid_key_in_cfgs(args, 'screenshot_dir'):
        outname = os.path.join(args.screenshot_dir,
                               args.scene + "_" + network_stem)
        logger.add_log(f"Rendering {outname}.png")
        # image = testbed.render(args.width or 1920, args.height or 1080, args.screenshot_spp, True)
        # if os.path.dirname(outname) != "":
        # os.makedirs(os.path.dirname(outname), exist_ok=True)
        # write_image(outname + ".png", image)
    if valid_key_in_cfgs(args, 'video_camera_path'):
        testbed.load_camera_path(args.video_camera_path)

        resolution = [args.width or 1920, args.height or 1080]
        n_frames = args.video_n_seconds * args.video_fps
        save_frames = "%" in args.video_output
        start_frame, end_frame = args.video_render_range

        if "tmp" in os.listdir():
            shutil.rmtree("tmp")
        os.makedirs("tmp")

        for i in tqdm(list(range(min(n_frames, n_frames + 1))), unit="frames", desc=f"Rendering video"):
            testbed.camera_smoothing = args.video_camera_smoothing
            if start_frame >= 0 and i < start_frame:
                # For camera smoothing and motion blur to work, we cannot just start rendering
                # from middle of the sequence. Instead we render a very small image and discard it
                # for these initial frames.
                # TODO Replace this with a no-op render method once it's available
                frame = testbed.render(32, 32, 1, True, float(i) / n_frames, float(i + 1) / n_frames, args.video_fps,
                                       shutter_fraction=0.5)
                continue
            elif end_frame >= 0 and i > end_frame:
                continue

            frame = testbed.render(resolution[0], resolution[1], args.video_spp, True, float(i) / n_frames,
                                   float(i + 1) / n_frames, args.video_fps, shutter_fraction=0.5)
            if save_frames:
                write_image(args.video_output % i, np.clip(
                    frame * 2 ** args.exposure, 0.0, 1.0), quality=100)
            else:
                write_image(f"tmp/{i:04d}.jpg", np.clip(frame *
                            2 ** args.exposure, 0.0, 1.0), quality=100)

            logger.add_log(
                f'video_progress current_frame: {i} total_frames: {n_frames}', level="RENDERING")

        if not save_frames:
            logger.add_log(
                f"ffmpeg -y -framerate {args.video_fps} -i tmp/%04d.jpg -c:v libx264 -pix_fmt yuv420p {args.video_output}")
            os.system(
                f"ffmpeg -y -framerate {args.video_fps} -i tmp/%04d.jpg -c:v libx264 -pix_fmt yuv420p {args.video_output}")

        shutil.rmtree("tmp")

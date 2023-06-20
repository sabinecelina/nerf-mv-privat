import os
import numpy as np
from subprocess import check_output
from math import pi, atan
from pathlib import Path
from nerf_industrial_metaverse.common.utils.json_utils import *
from nerf_industrial_metaverse.common.utils.cfgs_utils import *
from nerf_industrial_metaverse.common.utils.logger import *
from nerf_industrial_metaverse.common.utils.file_utils import *
from nerf_industrial_metaverse.common.utils.video_utils import *


def extract_camera_characteristics(colmap_output_dir, json_cfgs):
    default_values = {
        'w': 0,
        'h': 0,
        'fl_x': 0,
        'fl_y': 0,
        'cx': 0,
        'cy': 0,
        'k1': 0,
        'k2': 0,
        'k3': 0,
        'k4': 0,
        'p1': 0,
        'p2': 0,
        'is_fisheye': False,
    }
    camera_models = {
        "SIMPLE_PINHOLE": ['cx', 'cy'],
        "PINHOLE": ['fl_y', 'cx', 'cy'],
        "SIMPLE_RADIAL": ['cx', 'cy', 'k1'],
        "RADIAL": ['cx', 'cy', 'k1', 'k2'],
        "OPENCV": ['fl_y', 'cx', 'cy', 'k1', 'k2', 'p1', 'p2'],
        "SIMPLE_RADIAL_FISHEYE": ['is_fisheye', 'cx', 'cy', 'k1'],
        "RADIAL_FISHEYE": ['is_fisheye', 'cx', 'cy', 'k1', 'k2'],
        "OPENCV_FISHEYE": ['is_fisheye', 'fl_y', 'cx', 'cy', 'k1', 'k2', 'k3', 'k4']
    }

    with open(os.path.join(colmap_output_dir, "cameras.txt"), "r") as f:
        angle_x = pi / 2
        for line in f:
            if line[0] == "#":
                continue
            els = line.split(" ")
            default_values['w'] = float(els[2])
            default_values['h'] = float(els[3])
            default_values['fl_x'] = float(els[4])
            default_values['fl_y'] = float(els[4])
            default_values['cx'] = default_values['w'] / 2
            default_values['cy'] = default_values['h'] / 2
            default_values['is_fisheye'] = False
            camera_model = camera_models.get(els[1])
            if camera_model is None:
                print("Unknown camera model ", els[1])
                continue
            for idx, key in enumerate(camera_model, start=5):
                default_values[key] = bool(
                    els[idx]) if key == 'is_fisheye' else float(els[idx])
            angle_x = atan(default_values['w'] /
                           (default_values['fl_x'] * 2)) * 2
            angle_y = atan(default_values['h'] /
                           (default_values['fl_y'] * 2)) * 2
            fovx = angle_x * 180 / pi
            fovy = angle_y * 180 / pi
    out = {
        "camera_angle_x": angle_x,
        "camera_angle_y": angle_y,
        "fl_x": default_values['fl_x'],
        "fl_y": default_values['fl_y'],
        "k1": default_values['k1'],
        "k2": default_values['k2'],
        "k3": default_values['k3'],
        "k4": default_values['k4'],
        "p1": default_values['p1'],
        "p2": default_values['p2'],
        "is_fisheye": default_values['is_fisheye'],
        "cx": default_values['cx'],
        "cy": default_values['cy'],
        "w": default_values['w'],
        "h": default_values['h'],
        "aabb_scale": json_cfgs.aabb_scale,
        "frames": [],
    }
    return out


def extract_frame_information(colmap_output_dir, scene_dir):
    bottom = np.array([0.0, 0.0, 0.0, 1.0]).reshape([1, 4])
    up = np.zeros(3)
    image_path = osp.join(scene_dir, 'images')
    frames = []
    with open(os.path.join(colmap_output_dir, "images.txt"), "r") as f:
        lines = [line.strip() for line in f if line[0] != "#"]
        for i in range(0, len(lines), 2):
            elems = lines[i].split()
            name = f"./{image_path}/{'_'.join(elems[9:])}"
            b = sharpness(name)
            qvec = np.array(tuple(map(float, elems[1:5])))
            tvec = np.array(tuple(map(float, elems[5:8])))
            R = qvec2rotmat(-qvec)
            t = tvec.reshape([3, 1])
            m = np.concatenate([np.concatenate([R, t], 1), bottom], 0)
            c2w = np.linalg.inv(m)

            c2w[0:3, [1, 2]] *= -1  # flip the y and z axis
            c2w = c2w[[1, 0, 2, 3], :]
            c2w[2, :] *= -1  # flip whole world upside down

            up += c2w[0:3, 1]
            frame = {"file_path": f"./images/{'_'.join(elems[9:])}",
                     "sharpness": b, "transform_matrix": c2w}
            frames.append(frame)

    return frames, up


def scale_camera_distance(nframes, out):
    avglen = 0.
    for f in out["frames"]:
        avglen += np.linalg.norm(f["transform_matrix"][0:3, 3])
    avglen /= nframes
    for f in out["frames"]:
        f["transform_matrix"][0:3, 3] *= 4.0 / avglen  # scale to "nerf sized"

    return out, avglen


def compute_center_of_attention(out):
    totw = 0.0
    totp = np.array([0.0, 0.0, 0.0])
    for f in out["frames"]:
        mf = f["transform_matrix"][0:3, :]
        for g in out["frames"]:
            mg = g["transform_matrix"][0:3, :]
            p, w = closest_point_2_lines(
                mf[:, 3], mf[:, 2], mg[:, 3], mg[:, 2])
            if w > 0.00001:
                totp += p * w
                totw += w
    if totw > 0.0:
        totp /= totw
    # the cameras are looking at totp
    for f in out["frames"]:
        f["transform_matrix"][0:3, 3] -= totp

    return out, totp


def export_transform_json(output_path, out):
    with open(output_path, "w") as outfile:
        json.dump(out, outfile, indent=2)


def load_json(filepath):
    with open(filepath, 'r') as file:
        data = json.load(file)
    return data


def create_screenshot_json(output_path, out, logger):
    if osp.exists(output_path):
        out["frames"] = [out["frames"][0], out["frames"][-1]]
        output_path = osp.join(output_path, "screenshots")
        os.makedirs(output_path, exist_ok=True)
        output_json_path = osp.join(output_path, "screenshot.json")
        i = 0
        for frame in out["frames"]:
            frame["file_path"] = osp.join(
                "./screenshots", f"screenshots_{i}.jpg")
            frame["transform_matrix"][0][3] -= 0.2
            frame["transform_matrix"][1][3] -= 0
            frame["transform_matrix"][2][3] -= 0
            frame["transform_matrix"] = np.array(
                frame["transform_matrix"]).tolist()  # Convert ndarray to list
            i += 1
        logger.add_log(f"Writing {output_json_path}")
        export_transform_json(output_json_path, out)
        logger.add_log(f"Finished processing, output path: {output_json_path}")


def process_json_file(scene_dir, cfgs_json, logger):
    colmap_output_dir = osp.join(scene_dir, "colmap_text")
    out = extract_camera_characteristics(colmap_output_dir, cfgs_json)
    logger.add_log('    Extract information from cameras.txt done')
    logger.add_log(
        f'    camera characteristics: res={out["w"], out["h"]}, center={round(out["cx"], 2), round(out["cy"], 2)}, focal={round(out["fl_x"], 2), round(out["fl_y"], 2)}')
    out["frames"], up = extract_frame_information(colmap_output_dir, scene_dir)
    nframes = len(out["frames"])
    logger.add_log(
        f'    extract information from images.txt done. Image count: {nframes}')

    up = up / np.linalg.norm(up)
    logger.add_log("    up vector was {}".format(up))
    R = rotmat(up, [0, 0, 1])  # rotate up vector to [0,0,1]
    R = np.pad(R, [0, 1])
    R[-1, -1] = 1

    for f in out["frames"]:
        f["transform_matrix"] = np.matmul(
            R, f["transform_matrix"])  # rotate up to be the z axis

    # find a central point they are all looking at
    logger.add_log('    computing center of attention...')
    out, totp = compute_center_of_attention(out)
    logger.add_log('    center of attention {}'.format(totp))

    out, avglen = scale_camera_distance(nframes, out)
    logger.add_log("    avg camera distance from origin {}".format(avglen))

    for f in out["frames"]:
        f["transform_matrix"] = f["transform_matrix"].tolist()
    logger.add_log("    {} frames extracted".format(nframes))
    out['frames'] = out['frames'][::cfgs_json.subsample]
    output_path = osp.join(scene_dir, cfgs_json.name)
    logger.add_log("    writing {}".format(output_path))
    export_transform_json(output_path, out)
    logger.add_log(
        "Finished process of creating json file.. output path: {}".format(output_path))
    if osp.exists(output_path):
        create_screenshot_json(scene_dir, out, logger)
    remove_files(scene_dir, cfgs_json, logger)


def iphone2json(video_path, cfgs_iphone, cfgs_json, logger):
    dataset_dir = Path(video_path)
    logger.add_log(
        'Original video information: num_frame-{}'.format(get_n_img_in_dir(osp.join(dataset_dir, "rgbd"))))
    logger.add_log(f"subsampling iphone images: {cfgs_json.subsample}")
    with open(dataset_dir / 'metadata') as f:
        metadata = json.load(f)
    frames = []
    n_images = len(list((dataset_dir / 'rgbd').glob('*.jpg')))
    poses = np.array(metadata['poses'])
    for idx in tqdm(range(n_images)):
        # Link the image.
        img_name = f'{idx}.jpg'
        img_path = dataset_dir / 'rgbd' / img_name

        # Rotate the image.
        if cfgs_iphone.rotate:
            rotate_img(img_path)

        # Extract c2w.
        """ Each `pose` is a 7-element tuple which contains quaternion + world position.
			[qx, qy, qz, qw, tx, ty, tz]
		"""
        pose = poses[idx]
        q = Quaternion(x=pose[0], y=pose[1], z=pose[2], w=pose[3])
        c2w = np.eye(4)
        c2w[:3, :3] = q.rotation_matrix
        c2w[:3, -1] = [pose[4], pose[5], pose[6]]
        if cfgs_iphone.rotate:
            c2w = rotate_camera(c2w)
            c2w = swap_axes(c2w)

        frames.append(
            {
                "file_path": f"./rgbd/{img_name}",
                "transform_matrix": c2w.tolist(),
            }
        )

    # Write intrinsics to `cameras.txt`.
    if not cfgs_iphone.rotate:
        h = metadata['h']
        w = metadata['w']
        K = np.array(metadata['K']).reshape([3, 3]).T
        fx = K[0, 0]
        fy = K[1, 1]
        cx = K[0, 2]
        cy = K[1, 2]
    else:
        h = metadata['w']
        w = metadata['h']
        K = np.array(metadata['K']).reshape([3, 3]).T
        fx = K[1, 1]
        fy = K[0, 0]
        cx = K[1, 2]
        cy = h - K[0, 2]

    transforms = {}
    transforms['fl_x'] = fx
    transforms['fl_y'] = fy
    transforms['cx'] = cx
    transforms['cy'] = cy
    transforms['w'] = w
    transforms['h'] = h
    transforms['aabb_scale'] = cfgs_json.aabb_scale
    transforms['scale'] = 1.0
    transforms['camera_angle_x'] = 2 * \
        np.arctan(transforms['w'] / (2 * transforms['fl_x']))
    transforms['camera_angle_y'] = 2 * \
        np.arctan(transforms['h'] / (2 * transforms['fl_y']))
    transforms['frames'] = frames

    os.makedirs(dataset_dir / 'arkit_transforms', exist_ok=True)
    with open(dataset_dir / 'arkit_transforms' / 'transforms.json', 'w') as fp:
        json.dump(transforms, fp, indent=2)

    # Normalize the poses.
    transforms['frames'] = transforms['frames'][::cfgs_json.subsample]
    logger.add_log("    computing center of attention...")
    translation, scale, avglen = find_transforms_center_and_scale(transforms)
    logger.add_log("    avg camera distance from origin {}".format(avglen))
    normalized_transforms = normalize_transforms(
        transforms, translation, scale)

    output_path = osp.join(dataset_dir, cfgs_json.name)
    with open(output_path, "w") as outfile:
        json.dump(normalized_transforms, outfile, indent=2)
    logger.add_log(
        "Finished process of creating json file.. output path: {}".format(output_path))
    if osp.exists(output_path):
        create_screenshot_json(dataset_dir, transforms, logger)

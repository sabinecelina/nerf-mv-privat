import os.path as osp
import os
import cv2

from nerf_industrial_metaverse.common.utils.img_utils import *


def extract_video(path, dst_folder, max_name_len=6, ext='.png', video_downsample=1, image_downsample=1, max_count=None):
    """Extract frames of a video to final folder. Frame will to write to xxxxx.jpg.

    Args:
        path: video path
        dst_folder: folder to write
        max_name_len: max len of name.
        video_downsample: video downsample factor
        image_downsample: if >1, will resize image_h and image_w by factor
        max_count: max number of frames to be extracted. None will extract all
        ext: .png or .jpg
    """
    assert osp.exists(path), 'No video file at {}'.format(path)

    idx = 0
    count = 0
    cap = cv2.VideoCapture(path)
    while cap.isOpened():
        ret, img = cap.read()
        if not ret:
            break

        # video downsample
        if idx % video_downsample != 0:
            idx += 1
            continue
        idx += 1

        name = str(count).zfill(max_name_len) + ext
        img_path = osp.join(dst_folder, name)
        h, w = img.shape[0], img.shape[1]

        if image_downsample > 1:
            img = cv2.resize(img, (int(w / image_downsample),
                             int(h / image_downsample)), interpolation=cv2.INTER_AREA)
        cv2.imwrite(img_path, img)

        count += 1
        if max_count is not None and count >= max_count:
            break

    cap.release()


def get_video_metadata(path):
    """
    Get the metadata of a video.

    Args:
        path: video path

    Returns：
        - length: number of frames
        - width: frame width
        - height: frame height
        - fps: video fps
    """
    assert osp.exists(path), 'No video file at {}'.format(path)

    cap = cv2.VideoCapture(path)
    length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    return length, width, height, fps


def get_n_img_in_dir(folder):
    """Get the num of image in directory"""
    return len([f for f in os.listdir(folder) if is_img_ext(f)])


def get_image_metadata(img_path):
    """Get image w,h,channel"""
    img = cv2.imread(img_path)
    if len(img.shape) == 2:
        h, w = img.shape[:2]
        channel = 0
    else:
        h, w, channel = img.shape

    return w, h, channel


def get_first_img(img_dir):
    # Get a list of all files in the folder
    files = os.listdir(img_dir)

    # Sort the list of files by name
    files.sort()

    # Find the first image file
    first_image = None
    for file in files:
        if file.endswith('.png'):
            first_image = file
            break

    return first_image

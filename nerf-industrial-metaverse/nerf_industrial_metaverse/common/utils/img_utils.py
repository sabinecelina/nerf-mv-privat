import os
import cv2 
def is_img_ext(file):
    """Check whether a filename is an image file by checking extension."""
    return file.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp'))

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
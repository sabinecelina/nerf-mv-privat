import numpy as np
import json
import math
import cv2
from pyquaternion import Quaternion
from tqdm import tqdm
from PIL import Image
import copy

def variance_of_laplacian(image):
    return cv2.Laplacian(image, cv2.CV_64F).var()


def sharpness(imagePath):
    image = cv2.imread(imagePath)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    fm = variance_of_laplacian(gray)
    return fm


def qvec2rotmat(qvec):
    return np.array([
        [
            1 - 2 * qvec[2] ** 2 - 2 * qvec[3] ** 2,
            2 * qvec[1] * qvec[2] - 2 * qvec[0] * qvec[3],
            2 * qvec[3] * qvec[1] + 2 * qvec[0] * qvec[2]
        ], [
            2 * qvec[1] * qvec[2] + 2 * qvec[0] * qvec[3],
            1 - 2 * qvec[1] ** 2 - 2 * qvec[3] ** 2,
            2 * qvec[2] * qvec[3] - 2 * qvec[0] * qvec[1]
        ], [
            2 * qvec[3] * qvec[1] - 2 * qvec[0] * qvec[2],
            2 * qvec[2] * qvec[3] + 2 * qvec[0] * qvec[1],
            1 - 2 * qvec[1] ** 2 - 2 * qvec[2] ** 2
        ]
    ])


def rotmat(a, b):
    a, b = a / np.linalg.norm(a), b / np.linalg.norm(b)
    v = np.cross(a, b)
    c = np.dot(a, b)
    # handle exception for the opposite direction input
    if c < -1 + 1e-10:
        return rotmat(a + np.random.uniform(-1e-2, 1e-2, 3), b)
    s = np.linalg.norm(v)
    kmat = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
    return np.eye(3) + kmat + kmat.dot(kmat) * ((1 - c) / (s ** 2 + 1e-10))


def closest_point_2_lines(oa, da, ob,
                          db):  # returns point closest to both rays of form o+t*d, and a weight factor that goes to 0 if the lines are parallel
    da = da / np.linalg.norm(da)
    db = db / np.linalg.norm(db)
    c = np.cross(da, db)
    denom = np.linalg.norm(c) ** 2
    t = ob - oa
    ta = np.linalg.det([t, db, c]) / (denom + 1e-10)
    tb = np.linalg.det([t, da, c]) / (denom + 1e-10)
    if ta > 0:
        ta = 0
    if tb > 0:
        tb = 0
    return (oa + ta * da + ob + tb * db) * 0.5, denom

def rotate_img(img_path, degree=90):
	img = Image.open(img_path)
	img = img.rotate(degree, expand=1)
	img.save(img_path, quality=100, subsampling=0)

def rotate_camera(c2w, degree=90):
	rad = np.deg2rad(degree)
	R = Quaternion(axis=[0, 0, -1], angle=rad)
	T = R.transformation_matrix
	return c2w @ T

def swap_axes(c2w):
	rad = np.pi / 2
	R = Quaternion(axis=[1, 0, 0], angle=rad)
	T = R.transformation_matrix
	return T @ c2w

# Automatic rescale & offset the poses.
def find_transforms_center_and_scale(raw_transforms):
	frames = raw_transforms['frames']
	for frame in frames:
		frame['transform_matrix'] = np.array(frame['transform_matrix'])

	rays_o = []
	rays_d = []
	for f in tqdm(frames):
		mf = f["transform_matrix"][0:3,:]
		rays_o.append(mf[:3,3:])
		rays_d.append(mf[:3,2:3])
	rays_o = np.asarray(rays_o)
	rays_d = np.asarray(rays_d)

	# Find the point that minimizes its distances to all rays.
	def min_line_dist(rays_o, rays_d):
		A_i = np.eye(3) - rays_d * np.transpose(rays_d, [0,2,1])
		b_i = -A_i @ rays_o
		pt_mindist = np.squeeze(-np.linalg.inv((np.transpose(A_i, [0,2,1]) @ A_i).mean(0)) @ (b_i).mean(0))
		return pt_mindist

	translation = min_line_dist(rays_o, rays_d)
	normalized_transforms = copy.deepcopy(raw_transforms)
	for f in normalized_transforms["frames"]:
		f["transform_matrix"][0:3,3] -= translation

	# Find the scale.
	avglen = 0.
	for f in normalized_transforms["frames"]:
		avglen += np.linalg.norm(f["transform_matrix"][0:3,3])
	nframes = len(normalized_transforms["frames"])
	avglen /= nframes
	scale = 4.0 / avglen # scale to "nerf sized"

	return translation, scale, avglen

def normalize_transforms(transforms, translation, scale):
	normalized_transforms = copy.deepcopy(transforms)
	for f in normalized_transforms["frames"]:
		f["transform_matrix"] = np.asarray(f["transform_matrix"])
		f["transform_matrix"][0:3,3] -= translation
		f["transform_matrix"][0:3,3] *= scale
		f["transform_matrix"] = f["transform_matrix"].tolist()
	return normalized_transforms
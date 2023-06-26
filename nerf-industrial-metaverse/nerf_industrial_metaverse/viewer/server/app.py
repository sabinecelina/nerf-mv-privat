from flask import Flask, request, jsonify, session, send_file, g
from werkzeug.utils import secure_filename
import os
import secrets
import os.path as osp
from flask_cors import CORS
from flask_socketio import SocketIO
import time
from nerf_industrial_metaverse.common.utils.cfgs_utils import *
from nerf_industrial_metaverse.common.utils.client_logger import *
from nerf_industrial_metaverse.tools.video_training_web import *
from nerf_industrial_metaverse.scripts_ngp.run_training import *

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*")
UPLOAD_FOLDER = './uploads'
DOWNLOAD_FOLDER = './downloads'
DATA_FOLDER = './data'
CONFIGS_PATH = "configs/default.yaml"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER
app.config['DATA_FOLDER'] = DATA_FOLDER
secret_key = secrets.token_hex(16)
app.secret_key = secret_key
logger = Client_Logger(socketio)
glob_cfgs = None


def set_glob_cfgs(value):
    # Declare that we want to use the global variable
    global glob_cfgs
    glob_cfgs = value
    return glob_cfgs


# Replace default.yaml with default_example.yaml
def replace_config():
    example_file = "configs/default_example.yaml"
    default_file = CONFIGS_PATH
    shutil.copyfile(example_file, default_file)


def get_file_path(extension):
    filename = session.get('filename')
    if filename is None:
        return 'Filename not found', 404

    file_path = os.path.join(DOWNLOAD_FOLDER, filename + extension)
    if not os.path.exists(file_path):
        return 'File not found', 404

    return file_path


def update_yaml_with_session():
    filename_without_extension = session.get('filename')
    video_path = osp.join(UPLOAD_FOLDER, filename_without_extension)
    snapshot = osp.join(
        DOWNLOAD_FOLDER, filename_without_extension + ".ingp")
    export_video = osp.join(
        DOWNLOAD_FOLDER, filename_without_extension + ".mp4")
    screenshot_dir = osp.join(
        "data", filename_without_extension, "screenshots")
    metadata_file = osp.join(
        "data", filename_without_extension, 'metadata')
    image_folder = osp.join("data", filename_without_extension, "images")
    new_config = {
        'name': filename_without_extension,
        'data.video_path': f"{video_path}.{session['file_type']}",
        'data.scene_name': filename_without_extension,
        'train.save_snapshot': snapshot,
        'train.screenshot_dir': screenshot_dir
    }
    if session['file_type'] == 'r3d':
        new_config['iphone'] = {'rotate': True}
    update_yaml_config(CONFIGS_PATH, new_config)
    if session['file_type'] in ['r3d', 'zip']:
        unzip(UPLOAD_FOLDER, filename_without_extension)
        update_yaml_config(CONFIGS_PATH, {
            'data.video_path': filename_without_extension
        })
        if os.path.exists(image_folder) and not os.path.exists(metadata_file):
            image_files = os.listdir(image_folder)
            os.makedirs(image_folder, exist_ok=True)
            logger.add_log(image_folder)
            if image_files:
                for image_file in image_files:
                    image_path = osp.join(image_folder, image_file)
                    shutil.move(image_path, image_folder)
    set_glob_cfgs(load_configs_yaml(CONFIGS_PATH))


@app.before_request
def set_global_session():
    # Use Flask's g object to store data across requests
    g.filename = session.get('filename')


@socketio.on("connect")
def connected():
    print("client has connected")


@socketio.on("disconnect")
def disconnected():
    print("user disconnected")


@app.route('/upload', methods=['POST'])
def upload():
    replace_config()
    if 'file' not in request.files:
        return 'No file uploaded', 400
    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        session['filename'] = get_filename_without_extension(filename)
        session['file_type'] = get_file_type(filename)
        update_yaml_with_session()
        return 'File uploaded successfully!'
    else:
        return 'Invalid file type', 400


@app.route('/api/trained-file-url')
def get_training_file_url():
    return send_file(get_file_path('.ingp'), as_attachment=True)


@app.route('/api/rendered-video-url')
def get_rendered_video_url():
    return send_file(get_file_path('.mp4'), as_attachment=True)


@app.route('/get-filename', methods=['GET'])
def get_filename():
    filename = session.get('filename') + ".ingp"
    return jsonify({'filename': filename})


@app.route('/api/images')
def get_images():
    try:
        filename = session.get('filename')
        image_folder = osp.join("data", filename, "screenshots")
        image_paths = [filename for filename in os.listdir(
            image_folder) if filename.endswith('.jpg')]
        return jsonify({'images': image_paths})
    except FileNotFoundError:
        return jsonify({'error': 'Images not found'}), 404


@app.route('/api/images/<path:image_path>')
def get_image(image_path):
    try:
        full_image_path = osp.join("data", session.get(
            'filename'), "screenshots", image_path)
        return send_file(full_image_path, mimetype='image/jpeg')
    except FileNotFoundError:
        return jsonify({'error': 'Image not found'}), 404


@app.route('/update_yaml_config', methods=['POST'])
def update_yaml_config_route():
    cfgs = request.get_json()
    new_config = {}
    remove_transform = False
    if 'image_downsample' in cfgs:
        image_downsample = cfgs['image_downsample']
        if image_downsample != 1:
            new_config['data.image_downsample'] = image_downsample

    if 'video_downsample' in cfgs:
        video_downsample = cfgs['video_downsample']
        if video_downsample != 1:
            new_config['data.video_downsample'] = video_downsample

    if 'n_steps' in cfgs:
        n_steps = cfgs['n_steps']
        if n_steps != 1:
            new_config['train.n_steps'] = n_steps

    if 'subsample' in cfgs:
        remove_transform = True
        default_subsample = cfgs['subsample']
        if default_subsample != 1:
            new_config['json.subsample'] = default_subsample

    if 'aabb_scale' in cfgs:
        remove_transform = True
        aabb_scale = cfgs['aabb_scale']
        if aabb_scale != 1:
            new_config['json.aabb_scale'] = aabb_scale

    if new_config:
        update_yaml_config(CONFIGS_PATH, new_config)

    set_glob_cfgs(load_configs_yaml(CONFIGS_PATH))
    scene_dir = osp.join(glob_cfgs.dir.data_dir, glob_cfgs.data.scene_name)
    transform_dir = osp.join(scene_dir, glob_cfgs.json.name)
    if osp.exists(transform_dir) and remove_transform:
        try:
            os.remove(transform_dir)
        except Exception as e:
            logger.add_log(e)
    return jsonify({'message': 'Config updated successfully'})


@app.route('/render-video')
def render_video():
    key_to_remove = 'train.save_snapshot'
    remove_yaml_key(CONFIGS_PATH, key_to_remove)
    filename = session.get('filename')
    snapshot = osp.join(DOWNLOAD_FOLDER, filename + ".ingp")
    export_video = osp.join(DOWNLOAD_FOLDER, filename + ".mp4")
    new_config = {
        'train.video_output': export_video,
        'train.load_snapshot': snapshot,
        'train.video_camera_path': "configs/base_cam.json",
    }
    update_yaml_config(CONFIGS_PATH, new_config)
    logger.add_log('--- START VIDEO RENDERING ---')
    cfgs = set_glob_cfgs(load_configs_yaml(CONFIGS_PATH))
    start_time = time.time()
    run_training(logger, cfgs)
    end_time = time.time()
    total_time = end_time - start_time
    logger.add_log(f"Processing time: {total_time} seconds")
    logger.add_log(f'--- DONE VIDEO RENDERING ---')
    socketio.emit("rendering_complete")
    return jsonify({'status': 'success', 'message': 'Training has done started.'})


@app.route('/start-training', methods=['POST'])
def start_training():
    try:
        cfgs = set_glob_cfgs(load_configs_yaml(CONFIGS_PATH))
        scene_name = cfgs.data.scene_name
        data_dir = cfgs.dir.data_dir
        scene_dir = osp.join(data_dir, scene_name)

        if not valid_key_in_cfgs(cfgs, 'iphone'):
            if not osp.isdir(osp.join(scene_dir, "images")):
                logger.add_log('--- EXTRACT IMAGES FROM VIDEO ---')
                extract_images(logger, cfgs)
                logger.add_log(f'--- DONE EXTRACT IMAGES FROM VIDEO ---')

            if not osp.exists(osp.join(scene_dir, "colmap_output.txt")) and not osp.isdir(osp.join(scene_dir, "colmap_text")) and not osp.isdir(osp.join(scene_dir, "sparse")):
                logger.add_log(
                    '--- RUN COLMAP. See COLMAP Log for current process. ---')
                start_time = time.time()
                run_poses(logger, cfgs)
                end_time = time.time()
                total_time = end_time - start_time
                logger.add_log(
                    f"Processing time: {total_time} seconds", level="COLMAP")
                logger.add_log(f'--- DONE RUN COLMAP ---')

            if not osp.exists(osp.join(scene_dir, cfgs.json.name)):
                logger.add_log('--- EXPORT TRANSFORM.JSON ---')
                export_json(logger, cfgs)
                logger.add_log(f'--- DONE EXPORT TRANSFORM.JSON ---')
        else:
            if not osp.exists(osp.join("data", scene_name, cfgs.json.name)):
                logger.add_log('--- EXPORT TRANSFORM.JSON ---')
                record_to_json(logger, cfgs)
                logger.add_log(f'--- DONE EXPORT TRANSFORM.JSON ---')

        if osp.exists(osp.join(scene_dir, cfgs.json.name)) and (osp.isdir(osp.join(scene_dir, "images")) or osp.isdir(osp.join(scene_dir, "rgbd"))):
            logger.add_log('--- START TRAINING ---')
            run_training(logger, cfgs)
            logger.add_log(f'--- DONE TRAINING SCENE ---')
            socketio.emit('training_complete')

        return jsonify({'status': 'success', 'message': 'Training done.'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', debug=True)

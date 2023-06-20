# -*- coding: utf-8 -*-

import os
import subprocess
from glob import glob

def run_subprocess(args, logger, logfile):
    process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                               universal_newlines=True)
    for line in process.stdout:
        logger.add_log(line, level="COLMAP")
        logfile.write(line)
    process.wait()
    return process.returncode

def run_colmap(scene_dir, logger, match_type='exhaustive_matcher'):
    """Run colmap by command line wrapper. """
    logfile_name = os.path.join(scene_dir, 'colmap_output.txt')
    logfile = open(logfile_name, 'w')
    colmap_binary = "colmap"

    # feature extraction. Same camera models
    feature_extractor_args = [
        colmap_binary,
        'feature_extractor',
        '--database_path',
        os.path.join(scene_dir, 'database.db'),
        '--image_path',
        os.path.join(scene_dir, 'images'),
        '--ImageReader.camera_model',
        'OPENCV',
        '--SiftExtraction.use_gpu=true',
        '--SiftExtraction.estimate_affine_shape=true',
        '--SiftExtraction.domain_size_pooling=true',
        '--ImageReader.single_camera',
        '1',
        '--SiftExtraction.gpu_index=0'
    ]
    logger.add_log('Starting Feature Extraction...')
    run_subprocess(feature_extractor_args, logger, logfile)
    logger.add_log('    Features extracted...')
    # feature extraction. Same camera models

    # feature matching
    feature_matcher_args = [
        colmap_binary,
        match_type,
        '--database_path',
        os.path.join(scene_dir, 'database.db'),
        '--SiftMatching.use_gpu=true',
        '--SiftMatching.guided_matching=true',
        '--SiftMatching.gpu_index=0',
    ]

    logger.add_log('Starting Feature Matching...')
    run_subprocess(feature_matcher_args, logger, logfile)
    logger.add_log('    Features matched...')

    # sparse mapping
    sparse_folder = os.path.join(scene_dir, 'sparse')
    if not os.path.exists(sparse_folder):
        os.makedirs(sparse_folder)
    mapper_args = [
        colmap_binary,
        'mapper',
        '--database_path',
        os.path.join(scene_dir, 'database.db'),
        '--image_path',
        os.path.join(scene_dir, 'images'),
        '--output_path',
        os.path.join(scene_dir, 'sparse')
    ]
    logger.add_log('Starting create sparse map...')
    run_subprocess(mapper_args, logger, logfile)
    logger.add_log('    Sparse map created...')

    bundle_adjuster_args = [
        colmap_binary,
        'bundle_adjuster',
        '--input_path',
        os.path.join(sparse_folder, '0'),
        '--output_path',
        os.path.join(sparse_folder, '0'),
        '--BundleAdjustment.refine_principal_point',
        '1'
    ]
    logger.add_log('Starting Bundle Adjusment. This may take a while...')
    run_subprocess(bundle_adjuster_args, logger, logfile)
    logger.add_log('    Bundle Adjustment done...')

    text = "colmap_text/"
    if not os.path.exists(os.path.join(scene_dir, text)):
        os.makedirs(os.path.join(scene_dir, text))
    model_converter_args = [
        colmap_binary,
        'model_converter',
        '--input_path',
        os.path.join(scene_dir, 'sparse/0/'),
        '--output_path',
        os.path.join(scene_dir, text),
        '--output_type',
        'TXT'
    ]
    
    model_converter_output = subprocess.check_output(model_converter_args, universal_newlines=True)
    logfile.write(model_converter_output)
    logger.add_log('    Model converted to .txt files')

    logfile.close()
    logger.add_log('Finished running COLMAP, see {} for logs'.format(logfile_name))
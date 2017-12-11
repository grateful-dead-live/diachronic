import os
import numpy as np
from collections import OrderedDict

FEATURES = None
TO_CATEGORY = None

def init(dir):
    #find features in first file of first folder
    dir = dir+'/'+os.listdir(dir)[1]
    with open(get_all_files(dir, '.essentia')[0], 'r') as lfile:
        essentia = json.load(lfile)
    categories = list(essentia.keys())
    TO_CATEGORY = {f:c for f in c.keys() for c in categories}
    FEATURES = list(TO_CATEGORY.keys())

def create_feature_map(dir):
    #TODO IMPLEMENT
    return

def get_all_files(path, extension):
    files = [root+'/'+name for root, dirs, files in os.walk(path) for name in files]
    return filter(lambda n: n.endswith(extension), files)

def get_all_features(dir):
    if not FEATURES:
        init(dir)
    return FEATURES

def load_feature_median(file, feature):
    with open(file, 'r') as lfile:
        return json.load(lfile)[TO_CATEGORY[feature]][feature]['median']
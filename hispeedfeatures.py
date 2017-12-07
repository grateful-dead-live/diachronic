import os
import numpy as np
from collections import OrderedDict

def create_feature_map(dir):
    features = {name: {'log': True, 'events': False} for name in get_all_features(dir)}
    [features[f].update({'events': True}) for f in ['onsets', 'beats']]
    nonlog = ['onsets', 'beats', 'chromagram', 'key', 'coefficients', 'tempo',
        'inharmonicity', 'tonality', 'zcr']
    [features[f].update({'log': False}) for f in nonlog]
    return features

def get_all_n3_files(path):
    files = [root+'/'+name for root, dirs, files in os.walk(path) for name in files]
    return filter(lambda n: n.endswith('.n3'), files)

def get_all_features(dir):
    #find all features in first folder
    dir = dir+'/'+os.listdir(dir)[1]
    all_files = [f.split('_')[-1].split('.')[0] for f in get_all_n3_files(dir)]
    return list(OrderedDict.fromkeys(all_files))

def xsdDurationToFloat(duration):
    return float(duration.split('"')[1].replace('PT', '').replace('S', ''))

def load_values(string):
    dims = string.split('af:dimensions')[1].split('"')[1].split()
    dims = map(int, dims)
    values = string.split('af:value')[1].replace('"', '').split()[:-1]
    values = map(float, values)
    return np.array(values).reshape((-1, dims[0]))

def load_events(string):
    times = map(lambda s: s.split(';')[0], string.split('tl:at')[1:])
    return np.array(sorted(map(xsdDurationToFloat, times)))

def load_feature(file):
    with open(file) as f:
        content = f.read()
    values = 'af:value' in content
    return load_values(content) if values else load_events(content)
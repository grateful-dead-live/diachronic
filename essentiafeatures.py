import os, json

FEATURES = None
TO_CATEGORY = None

def init(dir):
    global FEATURES, TO_CATEGORY
    #find features in first file of first folder
    dir = dir+'/'+os.listdir(dir)[1]
    with open(get_all_files(dir, '.essentia')[0], 'r') as lfile:
        essentia = json.load(lfile)
    categories = list(essentia.keys())
    TO_CATEGORY = {f:c for c in categories for f in essentia[c].keys()}
    FEATURES = list(TO_CATEGORY.keys())

def create_feature_map(dir):
    features = {name: {'log': True} for name in get_all_features(dir)}
    #TODO UPDATE!!!
    nonlog = ['bpm', 'beats_count', 'key_edma', 'mfcc', 'zerocrossingrate']
    [features[f].update({'log': False}) for f in nonlog]
    return features


def get_all_files(path, extension):
    files = [root+'/'+name for root, dirs, files in os.walk(path) for name in files]
    return filter(lambda n: n.endswith(extension), files)

def get_all_features(dir):
    if not FEATURES:
        init(dir)
    return FEATURES

def load_feature_median(file, feature):
    with open(file, 'r') as lfile:
        feature = json.load(lfile)[TO_CATEGORY[feature]][feature]
    if isinstance(feature, dict) and 'median' in feature:
        return feature['median']
    else:
        return feature
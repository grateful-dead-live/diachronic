import os
import numpy as np
import seaborn as sns
import internetarchive as ia
from hispeedfeatures import load_feature, get_all_features, get_all_n3_files
from archive import get_all_song_names, get_song_versions_by_year

SONG_NAME = 'Sugar Magnolia'
FEATURE = 'tempo'
AUDIO_DIRS = '../../thomasw/grateful_dead/lma_soundboards/sbd/'


def get_all_n3_files_of_type(path, type):
    return filter(lambda n: type in n, get_all_n3_files(path))

def get_n3_file_of_type(paths_and_audio, type):
    path = AUDIO_DIRS+paths_and_audio['recording']#TODO PUT TEST/ SOMEWHERE ELSE!!
    audio = paths_and_audio['track'].split('.')[0]
    return filter(lambda f: audio in f and type in f, get_all_n3_files(path))

def get_n3_files_of_type(paths_and_audio, type):
    return [f for pa in paths_and_audio for f in get_n3_file_of_type(pa, type)]

def load_and_join_features(featurefiles):
    features = map(load_feature, featurefiles)
    features = filter(lambda f: f.shape[0] > 0, features)
    return np.concatenate(features)

def load_and_join_features_means(featurefiles):
    features = map(load_feature, featurefiles)
    features = filter(lambda f: f.shape[0] > 0, features)
    return [f.mean() for f in features]

def get_all_joined_features(path, type):
    return load_and_join_features(get_all_n3_files_of_type(path, type))

def get_joined_features(paths_and_audio, type):
    return load_and_join_features(get_n3_files_of_type(paths_and_audio, type))

def plot_features(features, file):
    #features = [f.tolist() for f in features]
    plot = sns.boxplot(data=features, showfliers=False)
    plot.get_figure().savefig(file)
    plot.get_figure().clf()

def test_plot():
    dir = AUDIO_DIRS
    dirs = [dir+d for d in os.listdir(dir) if os.path.isdir(os.path.join(dir, d))]
    features = map(lambda p: get_all_joined_features(p, 'zcr'), dirs)
    plot_features(features, 'results/'+FEATURE+'.png')

def plot_song_versions(song, feature):
    yearly_versions = get_song_versions_by_year(song)
    yearly_features = []
    for year, versions in sorted(yearly_versions.iteritems()):
        print song, feature, year
        yearly_features.append(get_joined_features(versions, feature))
    plot_features(yearly_features, 'results/'+song+'_'+feature+'.png')

song_names = get_all_song_names()
features = get_all_features(AUDIO_DIRS)
for i, song in enumerate(song_names):
    for j, feature in enumerate(features):
        print 'S'+str(i)+'/'+str(len(song_names)), 'F'+str(j)+'/'+str(len(features))
        plot_song_versions(song, feature)
    print '--------------------------------------'

#plot_song_versions(SONG_NAME, FEATURE)
#test_plot()

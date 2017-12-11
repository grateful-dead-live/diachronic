import os, math
import numpy as np
from sklearn.preprocessing import normalize as sklnorm
import seaborn as sns
import matplotlib.pyplot as plt
import internetarchive as ia
import hispeedfeatures as vamp
import essentiafeatures as essentia
from archive import get_all_song_names, get_song_versions_by_year, get_track_durations

AUDIO_DIRS = '../../thomasw/grateful_dead/lma_soundboards/sbd/'
VAMP_FEATURES = vamp.create_feature_map(AUDIO_DIRS)
ESSENTIA_FEATURES = essentia.create_feature_map(AUDIO_DIRS)

def to_path_and_stem(path_and_audio):
    path = AUDIO_DIRS+path_and_audio['recording']
    audio = path_and_audio['track']
    return (path, audio[:audio.rfind('.')])

def get_vamp_file_of_type(path_and_audio, type):
    (path, stem) = to_path_and_stem(path_and_audio)
    return [f for f in vamp.get_all_n3_files(path) if stem in f and type in f]

def get_vamp_files_of_type(paths_and_audio, type):
    return [f for pa in paths_and_audio for f in get_vamp_file_of_type(pa, type)]

def get_essentia_file(path_and_audio):
    (path, stem) = to_path_and_stem(path_and_audio)
    return path+'/'+stem+'.essentia'

def get_essentia_files(paths_and_audio):
    return [get_essentia_file(pa) for pa in paths_and_audio]

def load_features(featurefiles):
    features = [vamp.load_feature(f) for f in featurefiles]
    #only non-empty features...
    return filter(lambda f: f.shape[0] > 0, features)

def get_vamp_features(paths_and_audio, name):
    features = load_features(get_vamp_files_of_type(paths_and_audio, name))
    if VAMP_FEATURES[name]['events']:
        return [len(f) for f in features]
    else:
        return [np.median(f) for f in features]#np.concatenate(features)

def get_essentia_features(paths_and_audio, name):
    files = get_essentia_files(paths_and_audio)
    return [essentia.load_feature_median(f, name) for f in files]

def get_summarized_features(paths_and_audio, name):
    if name in VAMP_FEATURES:
        features = get_vamp_features(paths_and_audio, name)
    else:
        features = get_essentia_features(paths_and_audio, name)
    return np.mean(features)

def boxplot_features(features, file):
    plot = sns.boxplot(data=features, showfliers=False)
    plot.get_figure().savefig(file)
    plot.get_figure().clf()

def lineplot(lines, labels, xticks, title, file):
    [plt.plot(line, label=labels[i]) for i, line in enumerate(lines)]
    plt.legend(loc=5)
    plt.xticks(np.arange(len(xticks)), tuple(xticks))
    #plt.locator_params(axis='x', nticks=5)
    plt.title(title)
    plt.savefig(file)
    plt.clf()

def lineplot2(lines, file):
    plot = sns.tsplot(data=lines)
    plot.get_figure().savefig(file)
    plot.get_figure().clf()

def boxplot_song_versions(song, feature):
    yearly_versions = get_song_versions_by_year(song)
    yearly_features = []
    for year, versions in sorted(yearly_versions.iteritems()):
        print song, feature, year
        yearly_features.append(get_joined_features(versions, feature))
    boxplot_features(yearly_features, 'results/'+song+'_'+feature+'.png')

def normalize(feature):
    feature = np.array(feature).reshape(-1, 1)
    return sklnorm(feature, axis=0, norm='max')

def fit_polynomial(data):
    #improve for year gaps!!
    xs = np.arange(len(data))
    z = np.polyfit(xs, data[:,0], 1)
    f = np.poly1d(z)
    return f(xs)

def sliding_mean(data, window=4):
    cumsum = np.cumsum(np.insert(data, 0, 0))
    means = (cumsum[window:] - cumsum[:-window]) / window
    pad = np.arange(window/2)
    beginning = [(sum(data[:(i+1)])/(i+1))[0] for i in pad]
    end = [(sum(data[-(i+1):])/(i+1))[0] for i in pad].reverse()
    means = np.append(np.array(beginning), np.array(means))
    return np.append(np.array(means), np.array(end))

def lineplot_song_versions(song, features, extension):
    versions_by_years = sorted(get_song_versions_by_year(song).iteritems())
    years = [str(y).replace('19', '') for y, v in versions_by_years]
    labels = ['versions', 'duration'] + features
    yearly_features = []
    #version count
    print song, 'version count'
    num_versions = [len(v) for y, v in versions_by_years]
    yearly_features.append(num_versions)
    title = song + ' ('+ str(sum(num_versions)) +' versions)'
    #version durations
    print song, 'duration'
    durations = []
    for year, versions in versions_by_years:
        durations.append(np.array(get_track_durations(versions)).mean())
    yearly_features.append(durations)
    #all other features
    for j, feature in enumerate(features):
        current_feature = []
        print song, feature, '('+str(j+1)+'/'+str(len(features))+')'
        for year, versions in versions_by_years:
            #print song, feature, '('+str(j+1)+'/'+str(len(features))+')', year
            current_feature.append(get_summarized_features(versions, feature))
        if feature in VAMP_FEATURES and VAMP_FEATURES[feature]['log']:
            current_feature = [math.log(f) for f in current_feature]
        yearly_features.append(current_feature)
    yearly_features = [normalize(yf) for yf in yearly_features]
    yearly_features = [sliding_mean(yf) for yf in yearly_features]
    lineplot(yearly_features, labels, years, title, 'results/'+song+'_'+extension+'.png')

def plot_all_songs(features, extension):
    song_names = get_all_song_names()
    for i, song in enumerate(song_names):
        print song, str(i+1)+'/'+str(len(song_names))
        lineplot_song_versions(song, features, extension)
        #print '--------------------------------------'

def plot_all_songs_and_features():
    plot_all_songs(get_all_features(AUDIO_DIRS))

#VAMP
#plot_all_songs(['tempo', 'onsets', 'amplitude', 'beats'], 'overview2')
#plot_all_songs(['inharmonicity', 'zcr', 'loudness', 'crest', 'centroid', 'spread'], 'overview3')

#ESSENTIA
#plot_all_songs(['bpm', 'average_loudness', 'beats_count'], 'essentia2')
#plot_all_songs(['zerocrossingrate', 'average_loudness', 'barkbands_crest', 'spectral_centroid', 'spectral_spread'], 'essentia3')

#COMPARISON
plot_all_songs(['bpm', 'tempo', 'beats_count', 'beats'], 'compare')

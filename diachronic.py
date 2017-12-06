import os
import numpy as np
from sklearn.preprocessing import normalize as sklnorm
import seaborn as sns
import matplotlib.pyplot as plt
import internetarchive as ia
from hispeedfeatures import load_feature, get_all_features, get_all_n3_files
from archive import get_all_song_names, get_song_versions_by_year

SONG_NAME = 'bird song'
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

def lineplot_song_versions(song, features):
    versions_by_years = sorted(get_song_versions_by_year(song).iteritems())
    years = [str(y).replace('19', '') for y, v in versions_by_years]
    labels = ['versions'] + features
    yearly_features = []
    num_versions = [len(v) for y, v in versions_by_years]
    yearly_features.append(num_versions)
    title = song + ' ('+ str(sum(num_versions)) +' versions)'
    for j, feature in enumerate(features):
        current_feature = []
        for year, versions in versions_by_years:
            print song, feature, '('+str(j+1)+'/'+str(len(features))+')', year
            year_median = np.median(get_joined_features(versions, feature))
            current_feature.append(year_median)
    yearly_features = [normalize(yf) for yf in yearly_features]
    yearly_features = [sliding_mean(yf) for yf in yearly_features]
    lineplot(yearly_features, labels, years, title, 'results/'+song+'_overview.png')

def plot_all_songs_and_features():
    song_names = get_all_song_names()
    features = get_all_features(AUDIO_DIRS)
    for i, song in enumerate(song_names):
        for j, feature in enumerate(features):
            print 'S'+str(i)+'/'+str(len(song_names)), 'F'+str(j)+'/'+str(len(features))
            plot_song_versions(song, feature)
        print '--------------------------------------'

#boxplot_song_versions(SONG_NAME, 'tempo')
lineplot_song_versions(SONG_NAME, ['tempo', 'key', 'amplitude', 'centroid'])
#test_plot()

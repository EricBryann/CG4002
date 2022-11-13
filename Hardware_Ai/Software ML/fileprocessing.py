import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from numpy import mean, std, sqrt, percentile
from scipy.stats import skew, kurtosis
from sklearn.preprocessing import StandardScaler
from sklearn.utils import shuffle
import os


def load_file(filename):
    """
    Load the file from the filename given.
    :param filename: The name of the data file to load
    :return: A 2d array of size (25, 3)
    """
    dataframe = list()
    with open(filename, 'r') as file:
        for line in file:
            line = line.strip()
            if line != '':
                temp = line.split(',')
                if len(temp) < 3:
                    continue
                try:
                    dataframe.append([float(x) for x in temp])
                except:
                    continue
    if len(dataframe) < 10:
        print(filename, len(dataframe), "The data points given are too little!")
    min_len = len(dataframe) if len(dataframe) < 25 else 25  # take maximum the first 25 data points
    return dataframe[:min_len]


def load_group(filenames):
    """
    Load all the files that belong to either training group or testing group.
    :param filenames: An array that contains all the names of the files within one group to load.
    :return: The processed input data, contains 61 features per action
    """
    loaded = list()
    # print("Loading files",filenames)
    for action_files in filenames:
        acc_x = list()
        acc_y = list()
        acc_z = list()
        gyro_x = list()
        gyro_y = list()
        gyro_z = list()
        for file in action_files:
            sensor_data = load_file(file)
            if sensor_data is None:
                continue
            if file.__contains__('accel'):
                for data in sensor_data:
                    acc_x.append(data[0])
                    acc_y.append(data[1])
                    acc_z.append(data[2])
            else:
                # print(sensor_data)
                for data in sensor_data:
                    gyro_x.append(data[0])
                    gyro_y.append(data[1])
                    gyro_z.append(data[2])
        features = list()
        try:
            # extract features from only accelerometer or gyroscope
            features.extend(extract_features(acc_x))
            features.extend(extract_features(acc_y))
            features.extend(extract_features(acc_z))
            features.extend(extract_features(gyro_x))
            features.extend(extract_features(gyro_y))
            features.extend(extract_features(gyro_z))
            features.extend([max(acc_x), max(acc_y), max(acc_z), min(acc_x), min(acc_y), min(acc_z)])
            # features.extend([var(gyro_x), var(gyro_y), var(gyro_z)])
            # features.append(len(argrelextrema(np.array(acc_x), np.greater)[0]))
            # features.append(len(argrelextrema(np.array(acc_y), np.greater)[0]))
            # features.append(len(argrelextrema(np.array(acc_x), np.greater)[0]))
            features.append(np.argmax(gyro_y) - np.argmin(gyro_y))  # differentiate shield and reload from others
        except Exception as e:
            print(action_files, "causes the error")
            print(e)
        # normalize the features
        try:
            features = np.array(features).reshape(-1, 1)
            s = StandardScaler()
            s.fit(features)
            features = s.transform(features)
            features = np.hstack(features)  # convert back to 1-d
            loaded.append(features)
        except:
            continue
    print("Total test cases loaded:", len(loaded))
    return loaded


def extract_features(raw_data):
    """
    Perform feature extraction, extract features on both accelerometer and gyroscope data
    :param raw_data: The unprocessed single-axis data from either accelerometer or gyroscope
    :return: An array of features extracted from the current single-axis data given
    """
    loaded = []

    def min_max_normalize(data):
        dist_max = abs(max(data))
        dist_min = abs(min(data))
        new_data = []
        for each in data:
            new_data.append((each - dist_min) / (dist_max - dist_min))
        return new_data

    # extract mean and standard deviation, root-mean-square, 25th percentile
    # tmax = max(raw_data)
    # tmin = min(raw_data)
    tstd = std(raw_data)
    # tminarg = np.argmin(raw_data)
    tmean = mean(raw_data)
    trms = sqrt(mean(sum(data ** 2 for data in raw_data)))
    # tmad = median_abs_deviation(raw_data)
    # tmed = np.median(raw_data)
    tskew = skew(raw_data)
    tkurtosis = kurtosis(raw_data)
    # tpeaks = argrelextrema(np.array(raw_data), np.greater)[0]
    # tmaxarg = np.argmax(raw_data)
    # tminarg = np.argmin(raw_data)
    # tinterval = abs(tmaxarg - np.partition(raw_data, -2)[-2])
    t25percentile = percentile(raw_data, 25)
    temp = [tmean, tstd, t25percentile, trms, tskew, tkurtosis]
    # temp = min_max_normalize(temp)
    # convert to frequency domain by FFT
    freq_domain = np.fft.rfft(raw_data)
    # extract the max, min and spectral energy from the frequency domain
    # fstd = std(freq_domain)
    fmin = abs(min(freq_domain))
    fmax = abs(max(freq_domain))
    # fmean = abs(mean(freq_domain))
    # fargmax = np.argmax(freq_domain)
    # fsecmax = abs(np.partition(freq_domain, -2)[-2])
    # fmad = median_abs_deviation(freq_domain)
    # fpeaks = argrelextrema(np.array(freq_domain), np.greater)[0]
    energy = sum(abs(freq_domain) ** 2) / 100 ** 2
    # fmed = abs(np.median(freq_domain))
    freq_temp = [fmax, fmin, energy]
    # freq_temp = min_max_normalize(freq_temp)
    temp.extend(freq_temp)
    # print(temp)
    loaded.extend(temp)
    return loaded


def load_dataset_group(group: str):
    """
    Load a dataset group, such as train or test.
    :param group: Accept either 'train' or 'test' group only
    :return:
    """
    training_files = list()
    if group == 'train':
        X, y = load_train_group(training_files)
    elif group == 'test':
        X, y = load_test_group(training_files)
    else:
        X, y = None, None
    return X, y


def load_test_group(testing_files):
    """
    Load and format all data for test group.
    :param testing_files: An array that contains all the file names for testing data
    :return: Processed testing data testX, and its true label testy
    """
    testing_files.extend(get_file_name('../dataset/real/test/grenade/'))
    grenade_count = len(testing_files)
    testing_files.extend(get_file_name('../dataset/real/test/reload/'))
    reload_count = len(testing_files) - grenade_count
    testing_files.extend(get_file_name('../dataset/real/test/shield/'))
    shield_count = len(testing_files) - reload_count - grenade_count
    noise_count = 0
    testing_files.extend(get_file_name('../dataset/real/test/noise'))
    noise_count = len(testing_files) - shield_count - reload_count - grenade_count
    testing_files.extend(get_file_name('../dataset/real/test/end'))
    end_count = len(testing_files) - shield_count - reload_count - grenade_count - noise_count
    print("Grenade count:", grenade_count)
    print("Reload count", reload_count)
    print("Shield count:", shield_count)
    print("Noise count:", noise_count)
    print("End count:", end_count)
    # load input data
    X = load_group(testing_files)
    colnames = ['tmean_ax', 'tstd_ax', 't25_ax', 'trms_ax', 'tskew_ax', 'tkurt_ax', 'fmax_ax', 'fmin_ax', 'fen_ax',
                'tmean_ay', 'tstd_ay', 't25_ay', 'trms_ay', 'tskew_ay', 'tkurt_ay', 'fmax_ay', 'fmin_ay', 'fen_ay',
                'tmean_az', 'tstd_az', 't25_az', 'trms_az', 'tskew_az', 'tkurt_az', 'fmax_az', 'fmin_az', 'fen_az',
                'tmean_gx', 'tstd_gx', 't25_gx', 'trms_gx', 'tskew_gx', 'tkurt_gx', 'fmax_gx', 'fmin_gx', 'fen_gx',
                'tmean_gy', 'tstd_gy', 't25_gy', 'trms_gy', 'tskew_gy', 'tkurt_gy', 'fmax_gy', 'fmin_gy', 'fen_gy',
                'tmean_gz', 'tstd_gz', 't25_gz', 'trms_gz', 'tskew_gz', 'tkurt_gz', 'fmax_gz', 'fmin_gz', 'fen_gz',
                'tmax_ax', 'tmax_ay', 'tmax_az', 'tmin_ax', 'tmin_ay', 'tmin_az', 'tint_gy'
                ]
    df = pd.DataFrame(X, columns=colnames)
    to_drop = ['t25_ax', 'tkurt_ax', 'tmean_ay', 'tskew_ay', 'tkurt_ay', 't25_az', 'tskew_az', 'tkurt_az', 'fen_az', 'tskew_gx',
     'tkurt_gx', 'tskew_gy', 'tkurt_gy', 'tskew_gz', 'tkurt_gz', 'tint_gy']
    df = df.drop(to_drop, axis=1)
    X = np.array(df)
    # load class output
    y = generate_labels(end_count, grenade_count, noise_count, reload_count, shield_count)
    y = np.array(y)
    return X, y


def load_train_group(training_files):
    """
    Load and format all data for test group.
    :param training_files: An array that contains all the file names for training data
    :return: Processed training data trainX, and its true label trainy
    """
    training_files.extend(get_file_name('../dataset/real/train/imu1/grenade/'))
    training_files.extend(get_file_name('../dataset/real/train/imu2/grenade/'))
    training_files.extend(get_file_name('../dataset/real/train/old data/grenade'))
    training_files.extend(get_file_name('../dataset/real/test/old data/grenade'))
    grenade_count = len(training_files)
    training_files.extend(get_file_name('../dataset/real/train/imu1/reload/'))
    training_files.extend(get_file_name('../dataset/real/train/imu2/reload/'))
    training_files.extend(get_file_name('../dataset/real/train/old data/reload'))
    training_files.extend(get_file_name('../dataset/real/test/old data/reload'))
    reload_count = len(training_files) - grenade_count
    training_files.extend(get_file_name('../dataset/real/train/imu1/shield/'))
    training_files.extend(get_file_name('../dataset/real/train/imu2/shield/'))
    training_files.extend(get_file_name('../dataset/real/train/old data/shield'))
    training_files.extend(get_file_name('../dataset/real/test/old data/shield'))
    shield_count = len(training_files) - reload_count - grenade_count
    training_files.extend(get_file_name('../dataset/real/train/noise'))
    noise_count = len(training_files) - shield_count - reload_count - grenade_count
    training_files.extend(get_file_name('../dataset/real/train/imu1/end'))
    training_files.extend(get_file_name('../dataset/real/train/imu2/end/'))
    training_files.extend(get_file_name('../dataset/real/train/old data/end'))
    training_files.extend(get_file_name('../dataset/real/test/old data/end'))
    end_count = len(training_files) - shield_count - reload_count - grenade_count - noise_count
    print("Grenade count:", grenade_count)
    print("Reload count", reload_count)
    print("Shield count:", shield_count)
    print("Noise count:", noise_count)
    print("End count:", end_count)
    # load input data
    X = load_group(training_files)
    colnames = ['tmean_ax', 'tstd_ax', 't25_ax', 'trms_ax', 'tskew_ax', 'tkurt_ax', 'fmax_ax', 'fmin_ax', 'fen_ax',
                'tmean_ay', 'tstd_ay', 't25_ay', 'trms_ay', 'tskew_ay', 'tkurt_ay', 'fmax_ay', 'fmin_ay', 'fen_ay',
                'tmean_az', 'tstd_az', 't25_az', 'trms_az', 'tskew_az', 'tkurt_az', 'fmax_az', 'fmin_az', 'fen_az',
                'tmean_gx', 'tstd_gx', 't25_gx', 'trms_gx', 'tskew_gx', 'tkurt_gx', 'fmax_gx', 'fmin_gx', 'fen_gx',
                'tmean_gy', 'tstd_gy', 't25_gy', 'trms_gy', 'tskew_gy', 'tkurt_gy', 'fmax_gy', 'fmin_gy', 'fen_gy',
                'tmean_gz', 'tstd_gz', 't25_gz', 'trms_gz', 'tskew_gz', 'tkurt_gz', 'fmax_gz', 'fmin_gz', 'fen_gz',
                'tmax_ax', 'tmax_ay', 'tmax_az', 'tmin_ax', 'tmin_ay', 'tmin_az', 'tint_gy'
                ]
    # compute correlation matrix for features and remove highly correlated features
    dataframe = pd.DataFrame(X, columns=colnames)
    corr = dataframe.corr().abs()
    upper_tri = corr.where(np.triu(np.ones(corr.shape), k=1).astype(np.bool))
    to_drop = [column for column in upper_tri.columns if any(upper_tri[column] > 0.9)]
    print(to_drop)
    df = dataframe.drop(to_drop, axis=1)
    corr = df.corr()
    mask = np.zeros_like(corr, dtype=np.bool)
    sns.set_style(style='white')
    f, ax = plt.subplots(figsize=(11, 9))
    cmap = sns.diverging_palette(220, 10, as_cmap=True)
    sns.heatmap(corr, mask=mask, cmap=cmap,
                square=True,
                linewidths=.5, cbar_kws={"shrink": .5}, ax=ax).get_figure().savefig('../dataset/real/corr.png')

    X = np.array(df)
    # load class output
    y = generate_labels(end_count, grenade_count, noise_count, reload_count, shield_count)
    y = np.array(y)
    return X, y


def generate_labels(end_count, grenade_count, noise_count, reload_count, shield_count):
    y = list()
    for i in range(grenade_count):
        y.append([1, 0, 0, 0, 0])
    for i in range(reload_count):
        y.append([0, 1, 0, 0, 0])
    for i in range(shield_count):
        y.append([0, 0, 1, 0, 0])
    for i in range(noise_count):
        y.append([0, 0, 0, 1, 0])
    for i in range(end_count):
        y.append([0, 0, 0, 0, 1])
    return y


def get_file_name(filepath):
    """
    Iterate through the file path and store all the file names inside an array of format [accel.txt, ypr.txt].
    :param filepath: The file path for iterating through
    :return: An array of format [[accel1.txt, ypr1.txt], [accel2.txt, ypr2.txt],...]
    """
    idx = 0
    files = []
    for filename in os.scandir(filepath):
        try:
            if str(filename.path).__contains__('accel'):
                if str(filename.path).__contains__('_e'):
                    files.append([filename.path])
                elif str(filename.path).__contains__('_k'):
                    files.append([filename.path])
                elif str(filename.path).__contains__('_r'):
                    files.append([filename.path])
                elif str(filename.path).__contains__('_s'):
                    files.append([filename.path])
                elif str(filename.path).__contains__('_v'):
                    files.append([filename.path])
                else:
                    files.append([filename.path])
            else:
                if str(filename.path).__contains__('_e'):
                    files[idx].append(filename.path)
                elif str(filename.path).__contains__('_k'):
                    files[idx].append(filename.path)
                elif str(filename.path).__contains__('_r'):
                    files[idx].append(filename.path)
                elif str(filename.path).__contains__('_s'):
                    files[idx].append(filename.path)
                elif str(filename.path).__contains__('_v'):
                    files[idx].append(filename.path)
                else:
                    files[idx].append(filename.path)
                idx += 1
        except:
            print(filename.path)
    return files


def load_dataset():
    """
    Load both the training and testing data from the database, the database can be obtained from the GitHub link here
    https://github.com/tryyang2001/Capstone-Training-and-Testing-Database.git
    :return: The training data with its true label and the testing data with its true label, the returned array is a
    numpy array.
    """
    # load all train
    trainX, trainy = load_dataset_group('train')
    # load all test
    testX, testy = load_dataset_group('test')
    trainX, trainy = shuffle(trainX, trainy, random_state=0)
    testX, testy = shuffle(testX, testy, random_state=0)
    return trainX, trainy, testX, testy

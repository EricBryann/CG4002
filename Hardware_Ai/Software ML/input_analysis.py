import pandas as pd
from numpy import mean, std, percentile
from scipy.stats import skew
import numpy as np
from matplotlib import pyplot as plt
import os


# load a single file as a numpy array
def load_file(filepath):
    dataframe = list()
    with open(filepath, 'r') as file:
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
    return dataframe


# load a list of files and return as a 3d numpy array
def load_group(filenames):
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
        features.extend(extract_features(acc_x))
        features.extend(extract_features(acc_y))
        features.extend(extract_features(acc_z))
        features.extend(extract_features(gyro_x))
        features.extend(extract_features(gyro_y))
        features.extend(extract_features(gyro_z))
        # expect 54 features in total => 54 columns
        features = np.array(features)
        loaded.append(features)
    print("Total test cases loaded:", len(loaded))
    return loaded


def extract_features(raw_data):
    loaded = []

    def min_max_normalize(data):
        dist_max = abs(max(data))
        dist_min = abs(min(data))
        new_data = []
        for each in data:
            new_data.append((each - dist_min) / (dist_max - dist_min))
        return new_data

    # extract min, max, mean and standard deviation
    tstd = std(raw_data)
    tmin = min(raw_data)
    tminarg = np.argmin(raw_data)
    tmax = max(raw_data)
    tmaxarg = np.argmax(raw_data)
    tmean = mean(raw_data)
    tskew = skew(raw_data)
    tinterval = abs(tmaxarg - tminarg)
    temp = [tmin, tmax, tmean, tstd, tskew, tinterval]
    # correlation coefficient => covariance
    # convert to frequency domain by FFT
    freq_domain = np.fft.rfft(raw_data)
    fmin = abs(min(freq_domain))
    fmax = abs(max(freq_domain))
    energy = sum(abs(freq_domain) ** 2)
    fmed = abs(np.median(freq_domain))
    freq_temp = [fmax, fmin, fmed, energy]
    temp.extend(freq_temp)
    # print(temp)
    loaded.extend(temp)
    return loaded


def plot_graph_and_save_fig(loaded, filename):
    plt.plot(loaded[::5])
    plt.savefig('D:/Tan Rui Yang NUS/Year 3 Sem 1/CG4002/dataset/action_graphs/' + filename + '.png')
    plt.clf()


# load a dataset group, such as train or test
def load_dataset_group(group):
    training_files = list()
    if group == 'train':
        X, y = load_train_group(training_files)
    else:
        X, y = load_test_group(training_files)
    return X, y


def load_test_group(testing_files):
    testing_files.extend(get_file_name('../dataset/real/test/grenade/'))
    grenade_count = len(testing_files)
    testing_files.extend(get_file_name('../dataset/real/test/reload/'))
    reload_count = len(testing_files) - grenade_count
    testing_files.extend(get_file_name('../dataset/real/test/shield/'))
    shield_count = len(testing_files) - reload_count - grenade_count
    testing_files.extend(get_file_name('../dataset/real/test/end'))
    end_count = len(testing_files) - shield_count - reload_count - grenade_count
    # load input data
    X = load_group(testing_files)
    X = np.array(X)
    # load class output
    y = list()
    for i in range(grenade_count):
        y.append([1, 0, 0, 0])
    for i in range(reload_count):
        y.append([0, 1, 0, 0])
    for i in range(shield_count):
        y.append([0, 0, 1, 0])
    for i in range(end_count):
        y.append([0, 0, 0, 1])
    y = np.array(y)
    return X, y


def load_train_group(training_files):
    training_files.extend(get_file_name('../dataset/real/train/grenade/'))
    grenade_count = len(training_files)
    training_files.extend(get_file_name('../dataset/real/train/reload/'))
    reload_count = len(training_files) - grenade_count
    training_files.extend(get_file_name('../dataset/real/train/shield/'))
    shield_count = len(training_files) - reload_count - grenade_count
    training_files.extend(get_file_name('../dataset/real/train/end'))
    end_count = len(training_files) - shield_count - reload_count - grenade_count
    # load input data
    X = load_group(training_files)
    X = np.array(X)
    # load class output
    y = list()
    for i in range(grenade_count):
        y.append([1, 0, 0, 0])
    for i in range(reload_count):
        y.append([0, 1, 0, 0])
    for i in range(shield_count):
        y.append([0, 0, 1, 0])
    for i in range(end_count):
        y.append([0, 0, 0, 1])
    y = np.array(y)
    return X, y


def get_file_name(filepath):
    idx = 0
    files = []
    for filename in os.scandir(filepath):
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
    return files


# load the dataset, returns train and test X and y elements
def load_dataset():
    # load all train
    trainX, trainy = load_dataset_group('train')
    # load all test
    testX, testy = load_dataset_group('test')
    # zero-offset class values?
    return trainX, trainy, testX, testy


# load raw data for grenade
print("Start loading files...")


def load_and_separate_6_inputs(file):
    acc_x = list()
    acc_y = list()
    acc_z = list()
    gyro_x = list()
    gyro_y = list()
    gyro_z = list()
    sensor_data = load_file(file)[:5]
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
    return acc_x, acc_y, acc_z, gyro_x, gyro_y, gyro_z


def load_and_plot(path_to_load, path_to_savefig):
    files = get_file_name(path_to_load)
    idx = 0
    for action_files in files[::10]:
        acc_x = list()
        acc_y = list()
        acc_z = list()
        gyro_x = list()
        gyro_y = list()
        gyro_z = list()
        for file in action_files:
            sensor_data = load_file(file)
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
        plt.plot(acc_x, label='acc_x')
        plt.plot(acc_y, label='acc_y')
        plt.plot(acc_z, label='acc_z')
        plt.legend(loc='lower right')
        plt.savefig('D:/Tan Rui Yang NUS/Year 3 Sem 1/CG4002/dataset/action_graphs/'
                    + path_to_savefig + str(idx + 1) + '_acc.png')
        plt.clf()
        plt.plot(gyro_x, label='gyro_x')
        plt.plot(gyro_y, label='gyro_y')
        plt.plot(gyro_z, label='gyro_z')
        plt.legend(loc='lower right')
        plt.savefig('D:/Tan Rui Yang NUS/Year 3 Sem 1/CG4002/dataset/action_graphs/'
                    + path_to_savefig + str(idx + 1) + '_gyro.png')
        plt.clf()
        idx += 1


# load_and_plot('../dataset/real/train/grenade/', 'grenade/grenade')
# load_and_plot('../dataset/real/train/reload/', 'reload/reload')
# load_and_plot('../dataset/real/train/shield/', 'shield/shield')
# load_and_plot('../dataset/real/train/end/', 'end/end')
# load_and_plot('../dataset/real/train/noise/', 'noise/noise')


def extract_min_max_diff(arr):
    _max = max(arr)
    _min = min(arr)
    return _max - _min


def load_and_save_raw_data(files):
    for action_files in files:
        raw = []
        acc_x = list()
        acc_y = list()
        acc_z = list()
        gyro_x = list()
        gyro_y = list()
        gyro_z = list()
        for file in action_files:
            sensor_data = load_file(file)
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
        min_len = len(acc_x) if len(acc_x) < len(gyro_x) else len(gyro_x)
        for i in range(min_len):
            raw.append([])
            raw[i].append(acc_x[i])
            raw[i].append(acc_y[i])
            raw[i].append(acc_z[i])
            raw[i].append(gyro_x[i])
            raw[i].append(gyro_y[i])
            raw[i].append(gyro_z[i])
        with open('../dataset/real/raw/raw_data.txt', 'a') as file:
            for data in raw:
                file.write(str(data) + ',')
            file.write('\n')


def prepare_data_for_threshold(files):
    for action_files in files:
        for file in action_files:
            curr_gacc_x, curr_gacc_y, curr_gacc_z, curr_ggyro_x, curr_ggyro_y, curr_ggyro_z = \
                load_and_separate_6_inputs(file)
            if file.__contains__('accel'):
                acc_x.append(extract_min_max_diff(curr_gacc_x[:5]))
                acc_y.append(extract_min_max_diff(curr_gacc_y[:5]))
                acc_z.append(extract_min_max_diff(curr_gacc_z[:5]))
            else:
                gyro_x.append(extract_min_max_diff(curr_ggyro_x[:5]))
                gyro_y.append(extract_min_max_diff(curr_ggyro_y[:5]))
                gyro_z.append(extract_min_max_diff(curr_ggyro_z[:5]))


def print_threshold():
    print("Threshold for acc_x:", percentile(acc_x, 25))
    print("Threshold for acc_y:", percentile(acc_y, 25))
    print("Threshold for acc_z:", percentile(acc_z, 25))
    print("Threshold for gyro_x:", percentile(gyro_x, 25))
    print("Threshold for gyro_y:", percentile(gyro_y, 25))
    print("Threshold for gyro_z:", percentile(gyro_z, 25))
    print('------------------------------------')


np.set_printoptions(suppress=True)
acc_data = []
# grenade
files = get_file_name('../dataset/real/train/imu1/grenade/')
files.extend(get_file_name('../dataset/real/train/imu2/grenade'))
acc_x = list()
acc_y = list()
acc_z = list()
gyro_x = list()
gyro_y = list()
gyro_z = list()
prepare_data_for_threshold(files)
print('------------------------------------')
print('Number of data:', len(files))
print("Threshold values for grenade action:")
print_threshold()
acc_data.append(percentile(acc_x, 25) + percentile(acc_y, 25) + percentile(acc_z, 25))
# load_and_save_raw_data(files)

# reload
files = get_file_name('../dataset/real/train/imu1/reload/')
files.extend(get_file_name('../dataset/real/train/imu2/reload'))
print('Number of data:', len(files))
acc_x.clear()
acc_y.clear()
acc_z.clear()
gyro_x.clear()
gyro_y.clear()
gyro_z.clear()
prepare_data_for_threshold(files)
print("Threshold for reload action:")
print_threshold()
acc_data.append(percentile(acc_x, 25) + percentile(acc_y, 25) + percentile(acc_z, 25))
# load_and_save_raw_data(files)

# shield
files = get_file_name('../dataset/real/train/imu1/shield/')
files.extend(get_file_name('../dataset/real/train/imu2/shield'))
print('Number of data:', len(files))
acc_x.clear()
acc_y.clear()
acc_z.clear()
gyro_x.clear()
gyro_y.clear()
gyro_z.clear()
prepare_data_for_threshold(files)
print("Threshold for shield action:")
print_threshold()
acc_data.append(percentile(acc_x, 25) + percentile(acc_y, 25) + percentile(acc_z, 25))
# load_and_save_raw_data(files)

# end game
files = get_file_name('../dataset/real/train/imu1/end/')
files.extend(get_file_name('../dataset/real/train/imu2/end'))
print('Number of data:', len(files))
acc_x.clear()
acc_y.clear()
acc_z.clear()
gyro_x.clear()
gyro_y.clear()
gyro_z.clear()
prepare_data_for_threshold(files)
print("Threshold for end game action:")
print_threshold()
acc_data.append(percentile(acc_x, 25) + percentile(acc_y, 25) + percentile(acc_z, 25))
# load_and_save_raw_data(files)

# noise
files = get_file_name('../dataset/real/train/noise/')
print('Number of data:', len(files))
acc_x.clear()
acc_y.clear()
acc_z.clear()
gyro_x.clear()
gyro_y.clear()
gyro_z.clear()
prepare_data_for_threshold(files)
print("Threshold for noise action:")
print_threshold()
acc_data.append(percentile(acc_x, 25) + percentile(acc_y, 25) + percentile(acc_z, 25))
# load_and_save_raw_data(files)

# Conclusion
print('Sum of the 25-percentile from three axis from accelerometer:')
print(acc_data)
print('The threshold is that the sum of the 25th percentile from each axis output from accelerometer should be')
print((min(acc_data[:4])) // 2)

# Generate raw data to test mlp_u96 start of action identification
# load_and_save_raw_data(files)

# mlp neural network training model
# import pandas as pd
from numpy import mean, std
# from scipy.stats import median_abs_deviation, skew, kurtosis
import numpy as np
from matplotlib import pyplot as plt
from sklearn.metrics import ConfusionMatrixDisplay
from sklearn.metrics import confusion_matrix
from sklearn.preprocessing import StandardScaler
from keras.models import Sequential
from keras.layers import Dense, LeakyReLU
import os


INPUT_SHAPE = 5*6 + 6
OUTPUT_SHAPE = 5


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
        try:
            features.extend(extract_features(acc_x))
            features.extend(extract_features(acc_y))
            features.extend(extract_features(acc_z))
            features.extend(extract_features(gyro_x))
            features.extend(extract_features(gyro_y))
            features.extend(extract_features(gyro_z))
            # features.append(np.var(acc_x))
            # features.append(np.var(acc_y))
            # features.append(np.var(acc_z))
            features.append(max(acc_x))
            features.append(max(acc_y))
            features.append(max(acc_z))
            features.append(min(acc_x))
            features.append(min(acc_y))
            features.append(min(acc_z))
        except:
            print(action_files)
        features = np.array(features).reshape(-1, 1)
        s = StandardScaler()
        s.fit(features)
        features = s.transform(features)
        features = np.hstack(features)
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
    # tminarg = np.argmin(raw_data)
    # tmaxarg = np.argmax(raw_data)
    tmean = mean(raw_data)
    # tmad = median_abs_deviation(raw_data)
    # tmed = np.median(raw_data)
    # tskew = skew(raw_data)
    # tinterval = abs(tmaxarg - tminarg)
    # tkurtosis = kurtosis(raw_data)
    temp = [tmean, tstd]
    # temp = min_max_normalize(temp)
    # correlation coefficient => covariance
    # convert to frequency domain by FFT
    freq_domain = np.fft.rfft(raw_data)
    # fstd = std(freq_domain)
    fmin = abs(min(freq_domain))
    fmax = abs(max(freq_domain))
    # fmean = abs(mean(freq_domain))
    # fargmax = np.argmax(freq_domain)
    # fsecmax = abs(np.partition(np.array(freq_domain).flatten(), -2)[-2])
    # fmad = median_abs_deviation(freq_domain)
    energy = sum(abs(freq_domain)**2) / 100**2
    # fmed = abs(np.median(freq_domain))
    freq_temp = [fmax, fmin, energy]
    # freq_temp = min_max_normalize(freq_temp)
    temp.extend(freq_temp)
    # print(temp)
    loaded.extend(temp)
    return loaded


def plot_graph_and_save_fig(loaded):
    for i in range(31):
        plt.plot(loaded[i])
        plt.savefig(
            'D:\\Tan Rui Yang NUS\\Year 3 Sem 1\\CG4002\\dataset\\action_graphs\\standing\\standing' + str(i) + '.png')
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
    X = np.array(X)
    # load class output
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
    y = np.array(y)
    return X, y


def load_train_group(training_files):
    training_files.extend(get_file_name('../dataset/real/train/grenade/'))
    grenade_count = len(training_files)
    training_files.extend(get_file_name('../dataset/real/train/reload/'))
    reload_count = len(training_files) - grenade_count
    training_files.extend(get_file_name('../dataset/real/train/shield/'))
    shield_count = len(training_files) - reload_count - grenade_count
    training_files.extend(get_file_name('../dataset/real/train/noise'))
    noise_count = len(training_files) - shield_count - reload_count - grenade_count
    training_files.extend(get_file_name('../dataset/real/train/end'))
    end_count = len(training_files) - shield_count - reload_count - grenade_count - noise_count

    # load input data
    X = load_group(training_files)
    X = np.array(X)
    # load class output
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
    return trainX, trainy, testX, testy


# load data from text files
print("Start loading dataset...")
trainX, trainy, testX, testy = load_dataset()
print("TrainX size:", trainX.shape, "Trainy size:", trainy.shape)
print("TestX size:", testX.shape, "Testy size:", testy.shape)
# plot_graph_and_save_fig(trainX)
np.savetxt('../dataset/real/input_data.txt', testX, fmt='%f,')
np.savetxt("../dataset/real/test_output.txt", testy, fmt='%f,')
print("Dataset loaded completely")

"""
Epoch: the number of times the algorithm runs on the whole training set
Batch: the number of sample used to update the model parameters
Learning rate: specify how much model weights to be updated
Loss: Difference between the expected and actual values
"""
# create model of MLP
total_acc = []
weights = []
biases = []
highest_acc = 0
min_acc = 100
best_model = Sequential()
worst_model = Sequential()
for i in range(10):
    model = Sequential()
    model.add(Dense(INPUT_SHAPE, input_shape=(INPUT_SHAPE,))) # 0
    model.add(LeakyReLU(alpha=0.01)) # 1
    model.add(Dense(64)) # 2
    model.add(LeakyReLU(alpha=0.05)) # 3
    model.add(Dense(48)) # 4
    model.add(LeakyReLU(alpha=0.05)) # 5
    model.add(Dense(32)) # 6
    model.add(LeakyReLU(alpha=0.05)) # 7
    model.add(Dense(16, activation='relu')) # 9
    model.add(Dense(OUTPUT_SHAPE, activation='softmax')) # 10
    model.compile(loss='categorical_crossentropy',
                  optimizer='adam',
                  metrics=['accuracy'])
    # fit network
    model.fit(trainX, trainy,
              epochs=9,
              verbose=1,
              validation_split=0.05)
    loss, accuracy = model.evaluate(testX, testy, verbose=0)
    print("Test #", i, accuracy)
    if accuracy < min_acc:
        worst_model = model
        min_acc = accuracy
    if accuracy > highest_acc:
        best_model = model
        highest_acc = accuracy
        weights = list()
        biases = list()
        idx = 0
        for i in range(len(model.layers)):
            if i == 0:
                weights.append("float15 input_layer_weight[INPUT_NODES * INPUT_LAYER_NODES] = {\n")
                biases.append("float15 input_layer_bias[INPUT_LAYER_NODES] = {\n")
            elif i == 2:
                weights.append("float15 h1_weight[INPUT_LAYER_NODES * HIDDEN_LAYER_1_NODES] = {\n")
                biases.append("float15 h1_bias[HIDDEN_LAYER_1_NODES] = {\n")
            elif i == 4:
                weights.append("float15 h2_weight[HIDDEN_LAYER_1_NODES * HIDDEN_LAYER_2_NODES] = {\n")
                biases.append("float15 h2_bias[HIDDEN_LAYER_2_NODES] = {\n")
            elif i == 6:
                weights.append("float15 h3_weight[HIDDEN_LAYER_2_NODES * HIDDEN_LAYER_3_NODES] = {\n")
                biases.append("float15 h3_bias[HIDDEN_LAYER_3_NODES] = {\n")
            elif i == 8:
                weights.append("float15 h4_weight[HIDDEN_LAYER_3_NODES * HIDDEN_LAYER_4_NODES] = {\n")
                biases.append("float15 h4_bias[HIDDEN_LAYER_4_NODES] = {\n")
            # elif i == 10:
            #     weights.append("float15 h5_weight[HIDDEN_LAYER_4_NODES * HIDDEN_LAYER_5_NODES] = {\n")
            #     biases.append("float15 h5_bias[HIDDEN_LAYER_5_NODES] = {\n")
            elif i == 9:
                weights.append("float15 output_layer_weight[HIDDEN_LAYER_4_NODES * OUTPUT_LAYER_NODES] = {\n")
                biases.append("float15 output_layer_bias[OUTPUT_LAYER_NODES] = {\n")
            else:
                continue
            weight = model.layers[i].get_weights()[0].flatten('F').tolist()
            for data in weight:
                weights[idx] += str(data) + ', '
            weights[idx] += '\n};\n'
            bias = model.layers[i].get_weights()[1].flatten().tolist()
            for data in bias:
                biases[idx] += str(data) + ', '
            biases[idx] += '\n};\n'
            idx += 1
        with open('../dataset/real/weight_input.txt', 'w') as file:
            for line in weights:
                file.write(line + '\n')
        with open('../dataset/real/bias_input.txt', 'w') as file:
            for line in biases:
                file.write(line + '\n')
    total_acc.append(accuracy)

print("Mean accuracy:", np.mean(total_acc))
prediction = best_model.predict(testX)
np.set_printoptions(suppress=True)
predicted_result = []
actual_result = testy
for i in range(len(prediction)):
    max_prob = 0
    action = -1
    for j in range(OUTPUT_SHAPE):
        if prediction[i][j] > max_prob:
            max_prob = prediction[i][j]
            action = j
    predicted_result.append(action)

actual_action = []
for i in range(len(actual_result)):
    max_prob = 0
    action = -1
    for j in range(OUTPUT_SHAPE):
        if actual_result[i][j] > max_prob:
            max_prob = actual_result[i][j]
            action = j
    actual_action.append(action)

print("Confusion matrices of the test data:")
cm = confusion_matrix(testy.argmax(axis=1), prediction.argmax(axis=1))
display = ConfusionMatrixDisplay(confusion_matrix=cm)
display.plot(cmap=plt.cm.Blues)
plt.savefig('../dataset/real/ConfusionMatrix.png')

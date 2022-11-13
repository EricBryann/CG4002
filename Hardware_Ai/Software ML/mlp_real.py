# mlp neural network training model
from numpy import argmax
import numpy as np
from matplotlib import pyplot as plt
from sklearn.metrics import ConfusionMatrixDisplay, confusion_matrix, classification_report
from keras.models import Sequential
from keras.layers import Dense, LeakyReLU
from fileprocessing import load_dataset

# setting for training the model
REPEAT = 10
BATCH_SIZE = 32
EPOCHS = 15
VALIDATION_RATIO = 0.23

# number of neurons for MLP
INPUT_SHAPE = 45
HIDDEN_LAYER_1 = 64
HIDDEN_LAYER_2 = 48
HIDDEN_LAYER_3 = 32
HIDDEN_LAYER_4 = 16
OUTPUT_SHAPE = 5

# global variables definition
trainX = np.array([])
trainy = np.array([])
testX = np.array([])
testy = np.array([])

np.set_printoptions(suppress=True)


def load_and_process_data():
    """
    Load training data and testing data from the local database.
    :return: train_X, which is a 2d matrix such that the no. of rows define the no. of actions used for training and
             the no. of columns is the total number of features extracted.
             train_y, which contains the true label for each training data given.
             test_X, which is a 2d matrix such that the no. of rows define the no. of actions used for testing and
             the no. of columns is the total number of features extracted.
             test_y, which contains the true label for each testing data given.
    """
    print("Start loading dataset...")
    train_X, train_y, test_X, test_y = load_dataset()
    print("TrainX size:", train_X.shape, "Trainy size:", train_y.shape)
    print("TestX size:", test_X.shape, "Testy size:", test_y.shape)
    # plot_graph_and_save_fig(trainX)
    record_train_test_data(test_X, test_y)
    print("Dataset loaded completely")
    return train_X, train_y, test_X, test_y


def record_train_test_data(testX, testy):
    """
    Save the input data, the data can be used to test C++ code later.
    :param testX: The testing data such that each data contains 61 features
    :param testy: The true label of each testing data
    :return: None
    """
    with open('../dataset/real/input_data.txt', 'w') as file:
        file.write('float test_case[TEST_CASES_NUMBER * INPUT_NODES] = {\n')
        for line in testX:
            for data in line:
                file.write(str(data) + ',')
            file.write('\n')
        file.write('};\n\n')
        file.write('int correct_ans[TEST_CASES_NUMBER] = {\n')
        for line in testy:
            ans = argmax(line)
            file.write(str(ans) + ',')
        file.write('\n};')
    # np.savetxt('../dataset/real/input_data.txt', testX, fmt='%f,')
    # np.savetxt('../dataset/real/output_data.txt', [np.argmax(data) for data in testy], fmt='%d', newline=',')
    # np.savetxt("../dataset/real/test_output.txt", testy, fmt='%f,')


def create_MLP(train_X, train_y):
    """
    Create the multilayer-perceptron (MLP) neural network model
    :param train_X: The training data such that each data contains 61 features
    :param train_y: The true label of each training data
    :return: None
    """
    model = Sequential()
    model.add(Dense(INPUT_SHAPE, input_shape=(INPUT_SHAPE,)))  # 0
    model.add(LeakyReLU(alpha=0.01))  # 1
    model.add(Dense(HIDDEN_LAYER_1))  # 2
    model.add(LeakyReLU(alpha=0.05))  # 3
    model.add(Dense(HIDDEN_LAYER_2))  # 4
    model.add(LeakyReLU(alpha=0.05))  # 5
    model.add(Dense(HIDDEN_LAYER_3))  # 6
    model.add(LeakyReLU(alpha=0.05))  # 7
    model.add(Dense(HIDDEN_LAYER_4, activation='relu'))  # 8
    model.add(Dense(OUTPUT_SHAPE, activation='softmax'))  # 9
    model.compile(loss='categorical_crossentropy',
                  optimizer='adam',
                  metrics=['accuracy'])
    model.fit(train_X, train_y,
              epochs=EPOCHS,
              batch_size=BATCH_SIZE,
              verbose=1,
              validation_split=VALIDATION_RATIO)
    return model


def save_weights_and_biases(model):
    """
    Records the weights and biases for each layer of the neural network created, used for the C++ code later
    :param model: The neural network model
    :return: None
    """
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
    with open('../dataset/real/wnb.txt', 'w') as file:
        for line in weights:
            file.write(line + '\n')
        for line in biases:
            file.write(line + '\n')


def predict_with_model(model):
    """
    Perform classification by using the testing data.
    :param model: The neural network or any machine learning model created.
    :return: None
    """
    prediction = model.predict(testX)
    predicted_result = []
    for i in range(len(prediction)):
        max_prob = 0
        action = -1
        for j in range(OUTPUT_SHAPE):
            if prediction[i][j] > max_prob:
                max_prob = prediction[i][j]
                action = j
        predicted_result.append(action)
    return prediction, predicted_result


def plot_conf_matrix(prediction, filepath):
    """
    Plot the confusion matrix for the model to visualize the performance and accuracy of the machine learning model.
    :param prediction: The output generated from the neural network
    :param filepath: The destination path to save the confusion matrix plot
    :return: None
    """
    cm = confusion_matrix(testy.argmax(axis=1), prediction.argmax(axis=1))
    display = ConfusionMatrixDisplay(confusion_matrix=cm)
    display.plot(cmap=plt.cm.Blues)
    plt.savefig(filepath)


def generate_class_report_and_plot_conf_matrix(best_model, worst_model):
    """
    Generate the classification report and plot the confusion matrix for the model with the highest accuracy and the
    model with the lowest accuracy. This function is used for the model performance analysis.
    :param best_model: The neural network model that gives the highest accuracy for the testing data used in all batches
    :param worst_model: The neural network model that gives the lowest accuracy for the testing data used in all batches
    :return: None
    """
    actual_action = []
    for i in range(len(testy)):
        max_prob = 0
        action = -1
        for j in range(OUTPUT_SHAPE):
            if testy[i][j] > max_prob:
                max_prob = testy[i][j]
                action = j
        actual_action.append(action)
    prediction, predicted_result = predict_with_model(best_model)
    print(classification_report(actual_action, predicted_result,
                                target_names=['grenade', 'reload', 'shield', 'noise', 'logout']))
    plot_conf_matrix(prediction, '../dataset/real/BestConfusionMatrix.png')
    prediction, predicted_result = predict_with_model(worst_model)
    plot_conf_matrix(prediction, '../dataset/real/WorstConfusionMatrix.png')


def run_machine_learning():
    """
    Start the machine learning, collecting weights and biases and perform some analysis.
    :return: None
    """
    global trainX, trainy, testX, testy
    trainX, trainy, testX, testy = load_and_process_data()
    # create model of MLP
    overall_accuracy = []
    highest_acc = 0
    min_acc = 100
    best = None
    worst = None
    for i in range(REPEAT):
        model = create_MLP(trainX, trainy)
        loss, accuracy = model.evaluate(testX, testy, verbose=0)
        print("Test #", i, accuracy)
        if accuracy < min_acc:
            worst = model
            min_acc = accuracy
        if accuracy > highest_acc:
            best = model
            highest_acc = accuracy
        overall_accuracy.append(accuracy)
    print("Mean accuracy:", np.mean(overall_accuracy))
    # all training are done, collecting statistics and do analysis
    save_weights_and_biases(best)
    generate_class_report_and_plot_conf_matrix(best, worst)


if __name__ == '__main__':
    run_machine_learning()



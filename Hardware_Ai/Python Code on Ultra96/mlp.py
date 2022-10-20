import pynq.lib.dma
from pynq import allocate
from pynq import Overlay
import numpy as np
from numpy import mean, std, var
from sklearn.preprocessing import StandardScaler
from slidingwindow import SlidingWindow
import time
import logging


INPUT_NODES = 5 * 6 + 6
ACC_ACTION_THRESHOLD = 5.2


print("Uploading bitstream to FPGA...")
overlay = Overlay('mlp.bit')  # name of bitstream

# power monitoring
# rails = pynq.get_rails()
# if 'VSYS' in rails.keys():
#     print("Recording Ultra96 v1 power...")
#     rail_name = 'VSYS'
# elif 'PSINT_FP' in rails.keys():
#     print("Recording Ultra96 v2 power...")
#     rail_name = 'PSINT_FP'
# else:
#     raise RuntimeError("Cannot determine Ultra96 board version.")
# recorder = pynq.DataRecorder(rails[rail_name].power)

# set up for running bitstream
buffer_input = allocate(shape=(INPUT_NODES,), dtype=np.float32)
buffer_output = allocate(shape=(1,), dtype=np.int32)
dma = overlay.axi_dma_0
action_checker = SlidingWindow()
logging.basicConfig(filename='fpga.log', filemode='a', format='%(level)s - %(message)s s', level=logging.INFO)

def data_processing(raw_data):
    """
    Performs feature extraction and data normalization
    :param raw_data: Expect raw data of format [[ax, ay, az, gx, gy, gz], ...], arbitrary length is fine
    :return: A processed_data with 63 features => len(processed_data) = 63
    """
    processed_data = list()
    # separate each axis input, so we need 6 lists
    acc_x = list()
    acc_y = list()
    acc_z = list()
    gyro_x = list()
    gyro_y = list()
    gyro_z = list()
    for data in raw_data:
        acc_x.append(data[0])
        acc_y.append(data[1])
        acc_z.append(data[2])
        gyro_x.append(data[3])
        gyro_y.append(data[4])
        gyro_z.append(data[5])
    # do feature extraction for each axis input
    processed_data = feature_extraction(acc_x, acc_y, acc_z, gyro_x, gyro_y, gyro_z, processed_data)
    # expect 36 features
    return processed_data


def feature_extraction(acc_x, acc_y, acc_z, gyro_x, gyro_y, gyro_z, processed_data):
    def extract_features(raw_axis_data):
        loaded = []
        tstd = std(raw_axis_data)
        tmean = mean(raw_axis_data)
        temp = [tmean, tstd]
        # convert to frequency domain by FFT
        freq_domain = np.fft.rfft(raw_axis_data)
        fmin = abs(min(freq_domain))
        fmax = abs(max(freq_domain))
        energy = sum(abs(freq_domain) ** 2) / 100**2
        freq_temp = [fmax, fmin, energy]
        temp.extend(freq_temp)
        loaded.extend(temp)
        return loaded

    processed_data.extend(extract_features(acc_x))
    processed_data.extend(extract_features(acc_y))
    processed_data.extend(extract_features(acc_z))
    processed_data.extend(extract_features(gyro_x))
    processed_data.extend(extract_features(gyro_y))
    processed_data.extend(extract_features(gyro_z))
    processed_data.append(max(acc_x))
    processed_data.append(max(acc_y))
    processed_data.append(max(acc_z))
    processed_data.append(min(acc_x))
    processed_data.append(min(acc_y))
    processed_data.append(min(acc_z))
    processed_data = np.array(processed_data).reshape(-1, 1)
    s = StandardScaler()
    s.fit(processed_data)
    processed_data = s.transform(processed_data)
    processed_data = np.hstack(processed_data)
    return processed_data


def _get_output_from_fpga(input_data):
    """
    Implicit function used in get_output_from_FPGA to send input to FPGA and receive output from FPGA
    :param input_data: The processed input data, expect an array with 63 columns => len(input_data) = 63
    :return:
    """
    if input_data is None or len(input_data) == 0:
        return 3  # NO_ACTION
    try:
        # copy input_data to input buffer
        for i in range(len(input_data)):
            buffer_input[i] = input_data[i]
        # send input to FPGA and wait for output
        dma.sendchannel.transfer(buffer_input)
        dma.recvchannel.transfer(buffer_output)
        dma.sendchannel.wait()  # wait for send channel
        dma.recvchannel.wait()  # wait for recv channel
        action_no = buffer_output[0]
    except:
        print("There is an error occurs in FPGA!")
        action_no = 3
    return action_no


def get_output_from_FPGA(raw_data):
    """
    Processes raw data, send to FPGA and get back output
    :param raw_data: Expect [[ax1, ay1, az1, gx1, gy1, gz1],[ax2, ay2, az2, gx2, gy2, gz2],...]
    :return: action, an integer from 0 to 4 (0 -> grenade, 1 -> reload, 2 -> shield, 3 -> none, 4 -> end)
    """
    start_time = time.time()
    try:
        action_checker.clear_window()
        action_checker.fill_window(raw_data)
        if action_checker.get_curr_value() > ACC_ACTION_THRESHOLD:  # this can be an action
            print("This is an action!")
            input_data = data_processing(raw_data)
            action = _get_output_from_fpga(input_data)
        else:
            print("This is not an action...")
            action = 3
    except:
        print("There is an error occurs in FPGA...")
        action = 3
    logging.info(str(time.time() - start_time))
    return action


# print("0: Grenade\n1: Reload\n2: Shield\n3: No Action\n4: End")


# Group B06 CG4002 Capstone Project 2022

The motive of the capstone project is to design a two-player first person laser tag game. The game includes standard rules like the players trying to eliminate each other by shooting, and a player can protect themself by activating a shield with a swiping arm gesture. Similarly, players are also given a set number of grenades to throw at the opponent, activating this grenade throwing with a throwing arm gesture. Likewise, players are allowed to reload their guns with a set number of magazines once their bullets run out and this too will be based on a particular arm gesture. These actions are deduced by an AI model run on the Ultra96 FPGA with the help of IMU sensors.

Therefore, this repository contains the code used by our various components such as AI Hardware, Internal and External Comms, Visualiser, etc for the whole project to function together as a whole and they are located within their respective folders.

## Hardware_Sensor

There are 3 main parts from the hardware sensors to realise this project:

### IMU Sensor MPU6050

This sensor generates accelerations and gyroscope data in the x-y-z axis.
The directories relevant for this sensor include:

- CG4002_IMU_1 (code for player 1's IMU)
- CG4002_IMU_2 (code for player 2's IMU)
- CG4002_IMU_Calibration (code to calibrate the IMUs and generate offsets)

(The code above references [Jrowberg's I2Cdev library](https://github.com/jrowberg/i2cdevlib) and [this](https://wired.chillibasket.com/2015/01/calibrating-mpu6050/) calibration tutorial.

### IR Receiver VS1838

This receiver detects and receives long-range IR signal.
The directories relevant for this sensor include:

- CG4002_IR_receiver_red (code for player 1's IR receiver)
- CG4002_IR_receiver_green (code for player 2's IR receiver)

The code above uses <IRremote.h> library that provides convenient APIs to receive IR signal and decode its encoding value.

### IR Emitter DFR0095

This emitter will emit IR signal.
The directories relevant for this sensor include:

- CG4002_IR_emitter_green (code for player 1's IR emitter)
- CG4002_IR_emitter_red (code for player 2's IR emitter)

The code above uses <IRremote.h> library that provides convenient APIs to send IR signal with its associated encoding value.

## Hardware_AI

The code for building hardware AI can be split into 3 parts: software machine learning (Software ML), high-level synthesis (HLS) and scripts that should be run on Ultra96 (Ultra96).

### Software ML

This directory contains all the necessary codes for training the multilayer-perceptron (MLP) neural network model on Python. The library used is Keras. All the code regarding the creation of the machine learning model is inside _mlp_real.py_. The model must take in training and testing data from the database. The database can be
cloned through this GitHub repository: [Capstone Database](https://github.com/tryyang2001/Capstone-Training-and-Testing-Database.git). The file _fileprocessing.py_ handles the data preprocessing and feature extraction by taking the raw data from the database and send the processed data to the ML model. The files _data_collection_wireless.py_ and _data_collection_wired.py_ are Python scripts for data collection, they will store the data on your local device as _.txt_ file.
The file _input_analysis.py_ is used to determine the threshold value for start of action identification.

### HLS

This directory contains codes for performing high-level synthesis. To run the code, download Vivado HLS software and do C-simulation and C-synthesis on the software using the code in this directory. The _hls.cpp_ is the C++ code used for C-synthesis, and the _test_hls.cpp_ is used for C-simulation only.

### Ultra96

This directory contains the files and codes that should be run on Ultra96. The code _mlp.py_ is the Python script used to upload the bitstream to Ultra96 FPGA, and control the I/O and the behaviours of the hardware accelerator. To upload the bitstream to FPGA on Ultra96, we must have a .bit file (_mlp.bit_) and a hardware handoff file (_mlp.hwh_). The codes _slidingwindow.py_ and _power.py_ are helper libraries that are included in _mlp.py_. The former is used to identify start of action and the latter is used for controlling Ultra96 Programming Logic (PL) clock frequencies.

## Internal_Comms

The code for relay node must be run on a Linux OS due to the constraints of the BluePy library used. The file "4002_p1.py" handles the connection of the three beetles owned by player 1, while the file "4002_p2.py" handles the connection of the three beetles owned by player 2.

The internal communication servers act as clients to the Ultra96 server. As such, before these two internal comm files run, the Ultra96 server must first be activated and has started listening for connections.

## External_Comms

The code for external communication includes three parts: eval_server, one_player_game and two_player_game.

### eval_server

The file `eval_server.py` should run in the very beginning to start the server and wait for the connection from the evaluation client inside the `combine.py`

To install:

`python3 -m venv <virtual_env_name>`
`source <virtual_env_name>/bin/activate`
`pip3 install -r requirements.txt`

To run:

Start virtual environment `source <virtual_env_name>/bin/activate`<br />
Go to the correct directory and run `python eval_server.py <PORT> <GROUP_ID> <NUM_PLAYERS>` <br />

### one_player_game and two_player_game

In both one_player_game and two_player_game directories, the primary code is `combine.py`. This code is to establish the communication between Ultra96 and relay nodes, Ultra96 and evaluation server, as well as Ultra96 and visualizers. It includes a server to wait for the connections from relay nodes and receive the messages. It also includes a evaluation client to send the messages to evaluation server and receive the correct game state from evaluation server during the game play. It also deals with the message transmission between Ultra96 and visualizers via MQTT.

The files `GameState.py` `Helper.py` `MoveEngine.py` `PlayerState.py` `StateStaff.py` are imported by `combine.py` to update the players' game state for current round during the game play.

The file `mlp.py` is imported by `combine.py` to get the output from FPGA and map to corresponding predicted players' actions.

The file `combine_refactor.py` in the two_player_game directory is an improved version for code `combine.py`. It enhanced the code readiblity and deal with the inconsistency data transmission problem between Ultra96 and visualizers.

To run:

Go to the correct directory and run `python combine.py`

## Software_Visualizer

Unity was the main platform used to develop our augmented reality based visualizer app. The app showcases the various inventories and actions of the players with necessary animations, sound, and visual effects.

Some of the game objects used in the unity project required additional programming to achieve the desired operations and effects, so the files required for these can be found in the visulaizer folder. They are coded in C# and have to be added to Unity prefabs or gameobjects to function. For example, grenade.cs file has to added to the grenade prefab in the Unity project to make the grenade appear on the screen as a projectile for 2s and then explode.

## Contributors

- [Eric Bryan](https://github.com/EricBryann)
- [Tan Rui Yang](https://github.com/tryyang2001)
- [Li Kexuan](https://github.com/Cocokkkk)
- [Zhong Shuhao](https://github.com/Rye98)
- [Vignesh Kumaravel](https://github.com/KVignesh122)

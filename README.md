
# Group B06 CG4002 Capstone Project 2022

The motive of the capstone project is to design a two-player first person laser tag game. The game includes standard rules like the players trying to eliminate each other by shooting, and a player can protect themself by activating a shield with a swiping arm gesture. Similarly, players are also given a set number of grenades to throw at the opponent, activating this grenade throwing with a throwing arm gesture. Likewise, players are allowed to reload their guns with a set number of magazines once their bullets run out and this too will be based on a particular arm gesture. These actions are deduced by an AI model run on the Ultra96 FPGA with the help of IMU sensors.

Therefore, this repository contains the code used by our various components such as AI Hardware, Internal and External Comms, Visualiser, etc for th whole project to function together as a whole and they are located within their respective folders.

## Hardware Sensor

<>

## Hardware AI

<>

## Internal Comms

The code for relay node must be run on a Linux OS due to the constraints of the BluePy library used. The file "4002_p1.py" handles the connection of the three beetles owned by player 1, while the file "4002_p2.py" handles the connection of the three beetles owned by player 2. 

Before these two internal comm files run, the Ultra96 server must be activated and has started listening for connections.

## External Comms

<>

## Visualizer

Unity was the main platform used to develop our augmented reality based visualizer app. The app showcases the various inventories and actions of the players with necessary animations, sound, and visual effects.

Some of the game objects used in the unity project required additional programming to achieve the desired operations and effects, so the files required for these can be found in the visulaizer folder. They are coded in C# and have to be added to Unity prefabs or gameobjects to function. For example, grenade.cs file has to added to the grenade prefab in the Unity project to make the grenade appear on the screen as a projectile for 2s and then explode.

## Contributors

* [Eric Bryan](https://github.com/EricBryann)
* [Rui Yang](https://github.com/tryyang2001)
* [Kexuan](https://github.com/Cocokkkk)
* [Shuhao](https://github.com/Rye98)
* [Vignesh](https://github.com/KVignesh122)
*

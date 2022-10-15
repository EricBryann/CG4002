mlp_real.cpp: 
- C++ code for the multilayer-perceptron neural network layer's implementation. The MLP implemented is a 7-layers (including input layer and output layer) neural network with different activation functions such as ReLU, Leaky ReLU, and Softmax)

test_mlp_real.cpp:
- C++ testbench for C-simulation on Vivado HLS

y2k22_patch folder:
- is the patch files required for running HLS/exporting RTL
- include this folder in your HLS folder

mlp.bit:
- is the bitstream that should be uploaded to Ultra96

mlp.hwh:
- is the hardware handoff file required for uploading the bitstream to FPGA
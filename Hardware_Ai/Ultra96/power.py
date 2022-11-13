import pynq.ps
import sys, inspect


def print_classes():
    for name, obj in inspect.getmembers(sys.modules['pynq.ps']):
        if inspect.isclass(obj):
            print(obj)


# lower clock frequency for PL
def lower_PL_clk_rate():
    """
    Lower the unused clock frequency to save power
    :return: None
    """
    pynq.ps.Clocks.fclk0_mhz = 5
    pynq.ps.Clocks.fclk1_mhz = 1
    pynq.ps.Clocks.fclk2_mhz = 1
    pynq.ps.Clocks.fclk3_mhz = 1




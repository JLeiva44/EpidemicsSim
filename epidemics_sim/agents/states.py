from enum import Enum

class State(Enum):
    SUSCEPTIBLE = 0 #
    INFECTED = 1 # 
    RECOVERED = 2 #
    DECEASED = 4 #
    ASYMPTOMATIC = 5
    RECOVERED_IMMUNE = 6

class Severity(Enum):
    NORMAL = 0
    MID = 1
    SEVERE = 2

    

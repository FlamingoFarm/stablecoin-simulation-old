import numpy as np

class MarketStressSimulator:
    def __init__(self, rate: float=0.01):
        if rate < 0:
            raise Exception("The average event frequency per time interval cannot be negative")
        self.__rate = rate
    
    def get_rate(self):
        return self.__rate
    
    def event_occurrence(self):
        return bool(np.random.poisson(self.__rate))

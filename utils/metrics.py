import numpy as np
import pandas as pd
import copy

class Metrics:
    def __init__(self, coll_price: float):
        if coll_price < 0:
            raise Exception("Collateral price must not be negative")
        self.__indicators = pd.DataFrame({
            'coll_price': [coll_price],
            'moving_average': [coll_price]
        })
  
    def update_indicators(self, coll_price: float):
        if coll_price < 0:
            raise Exception("Collateral price must not be negative")
        updated_row = {
            'coll_price': coll_price,
            'moving_average': (len(self.__indicators) * self.__indicators.tail(1)['moving_average'] +  coll_price) / (len(self.__indicators) + 1)
        }
        self.__indicators = pd.concat([self.__indicators, pd.DataFrame(updated_row)], ignore_index=True)
        self.__indicators['exponential_moving_average'] = self.__indicators['coll_price'].ewm(alpha=0.05, adjust=False).mean()
        # self.__indicators['moving_average_50'] = self.__indicators['coll_price'].rolling(window=50).mean()
        # self.__indicators['slope_10'] = self.__indicators['exponential_moving_average'].rolling(window=10).apply(lambda x: np.polyfit(range(10), x, 1)[0], raw=False) # very time-intensive
        self.__indicators['pct_delta_ema_ma_to_ma'] = (self.__indicators['exponential_moving_average'] - self.__indicators['moving_average']) / self.__indicators['moving_average']
    
    def get_indicators(self):
        return copy.deepcopy(self.__indicators.tail(1))
    
    def get_all_indicators(self):
        return copy.deepcopy(self.__indicators)

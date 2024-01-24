from random import choice

class SimplePriceSimulator:
    def __init__(self, coll_price_change_rate: float=0.05):
        if coll_price_change_rate < 0:
            raise Exception("The collateral price change rate must be greater than 0")
        self.__coll_price_change_rate = coll_price_change_rate
        
        
    def calculate_price_change(self, previous_price: float):
        return choice([1, -1]) * self.__coll_price_change_rate * previous_price
from enum import Enum
import pandas as pd
from math import sqrt
from random import choice, uniform
from trove import Trove

BorrowerStrategy = Enum('BorrowerStrategy', [
    'ACTIVE', # characterized by maintaining an appropriate liquidation buffer
    'SENTIMENT_DRIVEN', # following the market sentiment
    'PASSIVE', # hands-off approach
    'RANDOM', # characterized by updating the trove randomly
    'SIMPLE_COLL', # maintains liquidation buffer via simple collateral adjustment
    'SIMPLE_LOAN', # maintains liquidation buffer via simple loan adjustment
    'TRADITIONAL' # risk-averse 
])

class Borrower:
    def __init__(self, strategy: BorrowerStrategy):
        if not isinstance(strategy, BorrowerStrategy):
            raise TypeError('strategy must be an instance of BorrowerStrategy')
        self.__strategy = strategy
    
    def get_strategy(self):
        return self.__strategy
    
    def modify_trove(self, trove: Trove, indicators: pd.DataFrame):
        if not trove.liquidated:
            match self.__strategy:
                case BorrowerStrategy.ACTIVE:
                    self.__modify_trove_via_active_strategy(trove, indicators)
                case BorrowerStrategy.SENTIMENT_DRIVEN:
                    self.__modify_trove_via_sentiment_driven_strategy(trove, indicators)
                case BorrowerStrategy.PASSIVE:
                    self.__modify_trove_via_passive_strategy()
                case BorrowerStrategy.RANDOM:
                    self.__modify_trove_via_random_strategy(trove, indicators)
                case BorrowerStrategy.SIMPLE_COLL:
                    self.__modify_trove_via_simple_coll_strategy(trove)
                case BorrowerStrategy.SIMPLE_LOAN:
                    self.__modify_trove_via_simple_loan_strategy(trove)
                case BorrowerStrategy.TRADITIONAL:
                    self.__modify_trove_via_traditional_strategy(trove, indicators)
                case _:
                    raise ValueError("Not a valid strategy")
            
    def __modify_trove_via_active_strategy(self, trove: Trove, indicators: pd.DataFrame):
        latest_coll_price = indicators['coll_price'].values[0]
        delta = trove.liquidation_buffer - 0.5 * trove.volatility_buffer
        p = uniform(0, 1) # random floating point in [0,1]
        delta_loan_value = p * delta
        delta_coll_balance = ((2 * trove.min_coll_ratio) / (3 - trove.min_coll_ratio)) * ((trove.loan_value + delta_loan_value) / latest_coll_price) - trove.coll_balance
        trove.update_loan(delta_coll_balance, delta_loan_value)
    
    def __modify_trove_via_sentiment_driven_strategy(self, trove: Trove, indicators: pd.DataFrame):
        sentiment_indicator = indicators['pct_delta_ema_ma_to_ma'].values[0]
        market_sentiment = self.__market_sentiment_function(sentiment_indicator)
        if market_sentiment > 0: # bullish
            if trove.liquidation_buffer > 0.5 * trove.volatility_buffer:
                p_coll = uniform(0, 1) # random floating point in [0,1]
                delta_coll_balance = p_coll * market_sentiment
                p_loan = uniform(0.5, 0.95)
                buffer_ratio = p_loan * (1 - market_sentiment)
                delta_loan_value = ((1 - buffer_ratio * (trove.min_coll_ratio - 1)) / trove.min_coll_ratio) * (trove.coll_value + delta_coll_balance * indicators['coll_price'].values[0]) - trove.loan_value
                trove.update_loan(delta_coll_balance, delta_loan_value)
        if market_sentiment < 0: # bearish
            if trove.liquidation_buffer < 0.75 * trove.volatility_buffer:
                p = uniform(0.75, 1)
                delta_loan_value = trove.liquidation_buffer - p * trove.volatility_buffer
                trove.update_loan(0, delta_loan_value)
    
    def __modify_trove_via_passive_strategy(self):
        pass # do nothing
    
    def __modify_trove_via_random_strategy(self, trove: Trove, indicators: pd.DataFrame):
        action = choice([True, False])
        if action:
            buffer_ratio_high = 0.8 / (trove.min_coll_ratio - 1)
            buffer_ratio = uniform(0, buffer_ratio_high)
            p_coll = uniform(-0.1, 0.1)
            delta_coll_balance = p_coll * trove.coll_balance
            delta_loan_value = ((1 - buffer_ratio * (trove.min_coll_ratio - 1)) / trove.min_coll_ratio) * (trove.coll_value + delta_coll_balance * indicators['coll_price'].values[0]) - trove.loan_value
            trove.update_loan(delta_coll_balance, delta_loan_value)
            
    def __modify_trove_via_simple_coll_strategy(self, trove: Trove):
        if trove.liquidation_buffer < 0.5 * trove.volatility_buffer:
            trove.update_loan(0.05 * trove.coll_balance, 0)
        if trove.liquidation_buffer > trove.volatility_buffer:
            trove.update_loan(-0.05 * trove.coll_balance, 0)
    
    def __modify_trove_via_simple_loan_strategy(self, trove: Trove):
        if trove.liquidation_buffer < 0.5 * trove.volatility_buffer:
            delta_loan_value = trove.liquidation_buffer - 0.5 * trove.volatility_buffer
            trove.update_loan(0, delta_loan_value)
        if trove.liquidation_buffer > 0.5 * trove.volatility_buffer:
            delta_loan_value = trove.liquidation_buffer - 0.5 * trove.volatility_buffer
            trove.update_loan(0, delta_loan_value)
    
    def __modify_trove_via_traditional_strategy(self, trove: Trove, indicators: pd.DataFrame):
        if trove.liquidation_buffer < 0.75 * trove.volatility_buffer or trove.liquidation_buffer > 1.25 * trove.volatility_buffer:
            delta_coll_balance = (trove.min_coll_ratio / (indicators['coll_price'].values[0] * (2 - trove.min_coll_ratio))) * (trove.loan_value) - trove.coll_balance
            trove.update_loan(delta_coll_balance, 0)
    
    def __market_sentiment_function(self, x: float):
        # alternative: 2 / (1 + exp(-a * x)) - 1 where a >= 1
        return x / sqrt(x**2 + 1)
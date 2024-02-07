from enum import Enum
import pandas as pd
from math import sqrt
from random import choice, uniform
from vault import Vault

OwnerStrategy = Enum('OwnerStrategy', [
    'ACTIVE', # characterized by maintaining an appropriate liquidation buffer
    'SENTIMENT_DRIVEN', # following the market sentiment
    'PASSIVE', # hands-off approach
    'RANDOM', # characterized by updating the vault randomly
    'SIMPLE_COLL', # maintains liquidation buffer via simple collateral adjustment
    'SIMPLE_LOAN', # maintains liquidation buffer via simple loan adjustment
    'TRADITIONAL' # risk-averse 
])

class Owner:
    def __init__(self, strategy: OwnerStrategy):
        if not isinstance(strategy, OwnerStrategy):
            raise TypeError('strategy must be an instance of OwnerStrategy')
        self.__strategy = strategy
    
    def get_strategy(self):
        return self.__strategy
    
    def modify_vault(self, vault: Vault, indicators: pd.DataFrame):
        if not vault.liquidated:
            match self.__strategy:
                case OwnerStrategy.ACTIVE:
                    self.__modify_vault_via_active_strategy(vault, indicators)
                case OwnerStrategy.SENTIMENT_DRIVEN:
                    self.__modify_vault_via_sentiment_driven_strategy(vault, indicators)
                case OwnerStrategy.PASSIVE:
                    self.__modify_vault_via_passive_strategy()
                case OwnerStrategy.RANDOM:
                    self.__modify_vault_via_random_strategy(vault, indicators)
                case OwnerStrategy.SIMPLE_COLL:
                    self.__modify_vault_via_simple_coll_strategy(vault)
                case OwnerStrategy.SIMPLE_LOAN:
                    self.__modify_vault_via_simple_loan_strategy(vault)
                case OwnerStrategy.TRADITIONAL:
                    self.__modify_vault_via_traditional_strategy(vault, indicators)
                case _:
                    raise ValueError("Not a valid strategy")
            
    def __modify_vault_via_active_strategy(self, vault: Vault, indicators: pd.DataFrame):
        latest_coll_price = indicators['coll_price'].values[0]
        delta = vault.liquidation_buffer - 0.5 * vault.volatility_buffer
        p = uniform(0, 1) # random floating point in [0,1]
        delta_loan_value = p * delta
        delta_coll_balance = ((2 * vault.min_coll_ratio) / (3 - vault.min_coll_ratio)) * ((vault.loan_value + delta_loan_value) / latest_coll_price) - vault.coll_balance
        vault.update_loan(delta_coll_balance, delta_loan_value)
    
    def __modify_vault_via_sentiment_driven_strategy(self, vault: Vault, indicators: pd.DataFrame):
        sentiment_indicator = indicators['pct_delta_ema_ma_to_ma'].values[0]
        market_sentiment = self.__market_sentiment_function(sentiment_indicator)
        if market_sentiment > 0: # bullish
            if vault.liquidation_buffer > 0.5 * vault.volatility_buffer:
                p_coll = uniform(0, 1) # random floating point in [0,1]
                delta_coll_balance = p_coll * market_sentiment
                p_loan = uniform(0.5, 0.95)
                buffer_ratio = p_loan * (1 - market_sentiment)
                delta_loan_value = ((1 - buffer_ratio * (vault.min_coll_ratio - 1)) / vault.min_coll_ratio) * (vault.coll_value + delta_coll_balance * indicators['coll_price'].values[0]) - vault.loan_value
                vault.update_loan(delta_coll_balance, delta_loan_value)
        if market_sentiment < 0: # bearish
            if vault.liquidation_buffer < 0.75 * vault.volatility_buffer:
                p = uniform(0.75, 1)
                delta_loan_value = vault.liquidation_buffer - p * vault.volatility_buffer
                vault.update_loan(0, delta_loan_value)
    
    def __modify_vault_via_passive_strategy(self):
        pass # do nothing
    
    def __modify_vault_via_random_strategy(self, vault: Vault, indicators: pd.DataFrame):
        action = choice([True, False])
        if action:
            buffer_ratio_high = 0.8 / (vault.min_coll_ratio - 1)
            buffer_ratio = uniform(0, buffer_ratio_high)
            p_coll = uniform(-0.1, 0.1)
            delta_coll_balance = p_coll * vault.coll_balance
            delta_loan_value = ((1 - buffer_ratio * (vault.min_coll_ratio - 1)) / vault.min_coll_ratio) * (vault.coll_value + delta_coll_balance * indicators['coll_price'].values[0]) - vault.loan_value
            vault.update_loan(delta_coll_balance, delta_loan_value)
            
    def __modify_vault_via_simple_coll_strategy(self, vault: Vault):
        if vault.liquidation_buffer < 0.5 * vault.volatility_buffer:
            vault.update_loan(0.05 * vault.coll_balance, 0)
        if vault.liquidation_buffer > vault.volatility_buffer:
            vault.update_loan(-0.05 * vault.coll_balance, 0)
    
    def __modify_vault_via_simple_loan_strategy(self, vault: Vault):
        if vault.liquidation_buffer < 0.5 * vault.volatility_buffer:
            delta_loan_value = vault.liquidation_buffer - 0.5 * vault.volatility_buffer
            vault.update_loan(0, delta_loan_value)
        if vault.liquidation_buffer > 0.5 * vault.volatility_buffer:
            delta_loan_value = vault.liquidation_buffer - 0.5 * vault.volatility_buffer
            vault.update_loan(0, delta_loan_value)
    
    def __modify_vault_via_traditional_strategy(self, vault: Vault, indicators: pd.DataFrame):
        if vault.liquidation_buffer < 0.75 * vault.volatility_buffer or vault.liquidation_buffer > 1.25 * vault.volatility_buffer:
            delta_coll_balance = (vault.min_coll_ratio / (indicators['coll_price'].values[0] * (2 - vault.min_coll_ratio))) * (vault.loan_value) - vault.coll_balance
            vault.update_loan(delta_coll_balance, 0)
    
    def __market_sentiment_function(self, x: float):
        # alternative: 2 / (1 + exp(-a * x)) - 1 where a >= 1
        return x / sqrt(x**2 + 1)
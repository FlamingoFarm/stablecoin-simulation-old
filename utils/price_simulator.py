import numpy as np
import pandas as pd
import scipy.stats as st

class PriceSimulator:
    def __init__(self, market_stress: bool=True, market_stress_rate: float=0.01):
        self.__market_stress = market_stress
        if market_stress_rate < 0:
            raise Exception("The average event frequency per time interval cannot be negative")
        self.__market_stress_rate = market_stress_rate
        
    # def __init__(self, csv_filename: str='../data/eth-max.csv'):  
    #     self.price_df = self.__get_coll_prices(csv_filename)
    
    # def __open_csv_datafile(self, csv_filename: str) -> pd.DataFrame:
    #     try:
    #         csv_dataframe = pd.read_csv(csv_filename)
    #         return(csv_dataframe)
    #     except FileNotFoundError:
    #         print(f"File '{csv_filename}' not found.")
    #     except Exception as e:
    #         print(f"An error occurred while opening the file: {e}")

    # def __get_coll_prices(self, csv_filename: str) -> pd.Series:
    #     csv_df = self.__open_csv_datafile(csv_filename)
    #     convert_epochs_to_timestamp = lambda df: pd.to_datetime(df['timestamp']).dt.tz_localize(None)
    #     price_df = (csv_df
    #         .rename(columns={'snapped_at': 'timestamp', 'price': 'coll_price'})
    #         .assign(timestamp=convert_epochs_to_timestamp)
    #         .drop(columns=['market_cap', 'total_volume']))
    #     return price_df
    
    def calculate_change_rate(self):
        if self.__market_stress and self.__event_occurrence():
            change_rate = self.__generate_price_shock_change_rate()
            negative_price_shock = change_rate < 0
            return change_rate, negative_price_shock
        else:
            change_rate = st.norm.rvs(loc=0.0, scale=0.05)
            return change_rate, False
    
    def __event_occurrence(self):
        return bool(np.random.poisson(self.__market_stress_rate))

    def __generate_price_shock_change_rate(self):
        result = 0
        while not 0.1 <= abs(result) <= 0.85:
            result = st.norm.rvs(loc=0.0, scale=0.5)
        return result

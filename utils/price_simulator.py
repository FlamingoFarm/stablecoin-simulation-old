import pandas as pd
import scipy.stats as st
from random import choice

class PriceSimulator:
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
    
    def calculate_price_change(self, previous_price: float, price_shock: bool=False):
        if price_shock:
            return choice(self.__generate_price_shock_change_rates()) * previous_price
        else:
            return choice(st.norm.rvs(loc=0.0, scale=0.05, size=10)) * previous_price

    def __generate_price_shock_change_rates(self):
        result = st.norm.rvs(loc=0.0, scale=0.5, size=15)
        result = [x for x in result if 0.1 <= abs(x) <= 0.85]
        while len(result) < 10:
            rate = st.norm.rvs(loc=0.0, scale=1)
            if 0.1 <= abs(rate) <= 0.85:
                result.append(rate)
        return result

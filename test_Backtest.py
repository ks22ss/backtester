from Backtest import Backtester
import yfinance as yf
import hkfdb
import os
import unittest
import pandas as pd

para_dict = {
        'stop_loss': [1,2,3],
        'take_profit':[2,4,6]
    }

def setup_test_env():
    
    start_date = "2022-08-01"
    end_date = "2022-08-05"
    data = yf.Ticker('SPY').history(start=start_date, end=end_date)
    
    return data

data = setup_test_env()


def test_set_param_combination():
    para_dict = {
        'stop_loss': [1,2,3],
        'take_profit':[2,4,6]
    }
    b = Backtester(para_dict=para_dict)
    assert b.para_name_list == list(para_dict)
    assert b.para_combinations == [{'stop_loss': 1, 'take_profit': 2}, {'stop_loss': 1, 'take_profit': 4}, {'stop_loss': 1, 'take_profit': 6}, {'stop_loss': 2, 'take_profit': 2}, {'stop_loss': 2, 'take_profit': 4}, {'stop_loss': 2, 'take_profit': 6}, {'stop_loss': 3, 'take_profit': 2}, {'stop_loss': 3, 'take_profit': 4}, {'stop_loss': 3, 'take_profit': 6}]
    
class Test_Backtest_add_df(unittest.TestCase):
    def test_empty_df(self):
        data = pd.DataFrame()
        b = Backtester(para_dict=para_dict)
        with self.assertRaises(Exception) as context:
            b.add_df(data, "test")
        self.assertTrue('df must include open high low close.' in str(context.exception))

    def test_df_time_index(self):
        data_no_time_index = data.reset_index()
        b = Backtester(para_dict=para_dict)
        with self.assertRaises(Exception) as context:
            b.add_df(data_no_time_index, "test")
        self.assertTrue('index is not datetime index.' in str(context.exception))

class Test_Backtest_backtest(unittest.TestCase):
    def test_empty_dfs(self):
        b = Backtester(para_dict=para_dict)
        b.add_df(data, "SPY") # pass in correct data
        with self.assertRaises(Exception) as context:
            b.backtest("not_a_symbol")
        self.assertTrue('not_a_symbol does not found in dfs. use list_dfs to check existing data' in str(context.exception))

    def test_df_time_index(self):
        b = Backtester(para_dict=para_dict)
        with self.assertRaises(Exception) as context:
            b.backtest("symbol")
        self.assertTrue('please add data using add_df(df, name) method.' in str(context.exception))


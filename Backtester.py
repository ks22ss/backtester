from cmath import exp
import pandas as pd
import itertools
from typing import List, Dict
from abc import ABC, abstractmethod
import numpy as np
import yfinance as yf
from dataclasses import dataclass, field

pd.set_option('display.max_column', None)
pd.set_option('display.max_row', None)
pd.set_option('display.width', 320)


def create_empty_list():
    return []

@dataclass
class Context:
        open_price: float = 0
        realized_pnl_list: List[float] =  field(default_factory=create_empty_list)
        initial_capital: float = 100000
        last_realized_capital: float = 100000
        num_of_share: int = 0
        equity_value_list: List[float] =  field(default_factory=create_empty_list)
        dd_dollar_list: List[float] =  field(default_factory=create_empty_list)
        dd_pct_list: List[float] =  field(default_factory=create_empty_list)
        lot_size: int = 100
        commission_rate: float = 0.0003
        min_commission: float = 3
        platform_fee: float  = 15

print(Context().initial_capital)
        

class Backtester:
    def __init__(self,para_dict:Dict={} ,configs:Dict={}):
        self.dfs = {}
        self.__para_dict = para_dict
        self.__configs  = configs

        # backtest context and df
        self.context = self.set_context()
        self.df_running = None

        self.para_name_list = list(para_dict)
        self.para_combinations = self.__set_param_combination()


    def __set_param_combination(self) -> List[Dict]:
        if len(self.__para_dict) != 0:
            param_keys = list(self.__para_dict)
            param_values = list(self.__para_dict.values())
            combinations = [dict(zip(param_keys, comb)) for comb in list(itertools.product(*param_values))]

            self.para_combinations = combinations

            return combinations
        else:
            raise Exception("para_dict cannot initiate as empty {}. ")
        

    def set_context(self, context=None):
        if context == None:
            return Context()
        return context
    

    def add_df(self, df: pd.DataFrame, name: str):
        
        # Check df contain columns
        expect_cols = ['open','high','low','close']
        df.columns = [c.lower() for c in df.columns]
        contain_expected_columns = all([col in df.columns for col in expect_cols])

        if not contain_expected_columns:
            raise Exception("df must include open high low close.")

        if not isinstance(df.index, pd.DatetimeIndex):
            raise Exception("index is not datetime index.")

        print("Checking na value...")
        print(df.isna().sum())
        
        df.name = name

        self.dfs[name] = df
    

    def get_df(self, name):
        return self.dfs[name]


    def list_dfs(self):
        if len(self.dfs):
            print("No dataframe added.")
            return []
        return list(self.dfs.keys())


    def open_position(self):

        self.context.num_of_share = self.context.lot_size * (self.context.last_realized_capital // (self.context.now_close * self.context.lot_size))

        self.context.open_price = self.context.now_close

        self.df_running.at[self.context.i, 'action'] = 'open'
        self.df_running.at[self.context.i, 'open_price'] = self.context.open_price
        self.df_running.at[self.context.i, 'num_of_share'] = self.context.num_of_share


    def close_position(self):
        self.context.realized_pnl = self.context.unrealized_pnl
        self.context.unrealized_pnl = 0

        self.context.realized_pnl_list.append(self.context.realized_pnl)

        self.context.last_realized_capital += self.context.realized_pnl

        self.context.num_of_share = 0

        self.df_running.at[self.context.i, 'close_price'] = self.context.now_close
        self.df_running.at[self.context.i, 'realized_pnl'] = self.context.realized_pnl
        self.df_running.at[self.context.i, 'commission'] = self.context.commission
        self.df_running.at[self.context.i, 'action'] = 'close'


    def __initialize_df_running(self, df_name: str):
        # preparing dataframe
        if len(self.dfs) == 0:
            raise Exception("please add data using add_df(df, name) method.")
        if df_name not in self.dfs.keys():
            raise Exception(f"{df_name} does not found in dfs. use list_dfs to check existing data")
        
        df = self.dfs[df_name]
        
        df = df.reset_index()

        df.columns = [c.lower() for c in df.columns]
        
            
        # empty columns to record all context
        df['action'] = ''
        df['num_of_share'] = 0
        df['open_price'] = np.NaN
        df['close_price'] = np.NaN
        df['realized_pnl'] = np.NaN
        df['unrealized_pnl'] = 0
        df['net_profit'] = 0
        df['equity_value'] = self.context.initial_capital
        df['mdd_dollar'] = 0
        df['mdd_pct'] = 0
        df['logic'] = ''
        df['commission'] = 0

        

        self.df_running = df


    def calculate_commission(self, context):
            if context.num_of_share > 0:
                if context.num_of_share * context.now_close * context.commission_rate < 3:
                    commission = 3 + context.platform_fee
                else:
                    commission = context.min_commission + context.platform_fee
            else:
                commission = 0
            commission = round(commission, 3)
            return commission


    def calculate_unrealized_pnl(self, context):
        unrealized_pnl = context.num_of_share * (context.now_close - context.open_price) - context.commission
        unrealized_pnl = round(unrealized_pnl, 3)
        return unrealized_pnl


    def calculate_equity_value(self, context):
        equity_value = self.context.last_realized_capital +  self.context.unrealized_pnl
        equity_value = round(equity_value, 3)
        return equity_value


    def calculate_mdd(self, context):
        max_equity = max(self.context.equity_value_list)
        dd_dollar = max_equity - self.context.equity_value
        dd_dollar = round(dd_dollar, 3)

        self.context.dd_dollar_list.append(dd_dollar)
        mdd_dollar = max(self.context.dd_dollar_list)

        dd_pct = 100 * (1 - self.context.equity_value / max_equity)
        dd_pct = round(dd_pct, 3)

        self.context.dd_pct_list.append(dd_pct)
        mdd_pct = max(self.context.dd_pct_list)

        return mdd_dollar, mdd_pct


    def backtest(self, df_name: str, params: Dict={}):
        self.__initialize_df_running(df_name)

        start_index = 0
        end_index = len(self.df_running)

        print(f"backtest begin. Start Date = {self.df_running.loc[start_index,'date']}")

        # initiate loop
        for i in range(start_index, end_index):
            ### Market Data
            self.context.now_date = self.df_running.loc[i, 'date']
            self.context.now_open = self.df_running.loc[i, 'open']
            self.context.now_high = self.df_running.loc[i, 'high']
            self.context.now_low = self.df_running.loc[i, 'low']
            self.context.now_close = self.df_running.loc[i, 'close']
            self.context.i = i

            ### Equity Calculation
            self.context.commission = self.calculate_commission(self.context)
            self.context.unrealized_pnl = self.calculate_unrealized_pnl(self.context)
            self.context.equity_value = self.calculate_equity_value(self.context)
            self.context.equity_value_list.append(self.context.equity_value)
            self.context.net_profit = self.context.equity_value - self.context.initial_capital
            self.context.mdd_dollar , self.context.mdd_pct = self.calculate_mdd(self.context)


            self.onData(self.df_running, self.context, params)


            ### record at last
            self.df_running.at[self.context.i, 'equity_value'] = self.context.equity_value
            self.df_running.at[self.context.i, 'unrealized_pnl'] = self.context.unrealized_pnl
            self.df_running.at[self.context.i, 'net_profit'] = self.context.net_profit
            self.df_running.at[self.context.i, 'mdd_dollar'] = self.context.mdd_dollar
            self.df_running.at[self.context.i, 'mdd_pct'] = self.context.mdd_pct

            #print(self.df_running)
            #time.sleep(12345)

        # reset backtest states context
        print(f"backtest ended. End Date = {self.df_running.loc[end_index-1,'date']}")
        print(self.df_running)
        self.context = self.create_context()
        
    @abstractmethod    
    def onData(self, df, context, params, i):
        return

    


class Strategy(Backtester):
    def __init__(self,para_dict,configs):
        super().__init__(para_dict, configs)

    def onData(self, df, context, params):
        now_date = df.loc[context.i, 'date']
        now_open = df.loc[context.i, 'open']
        now_high = df.loc[context.i, 'high']
        now_low = df.loc[context.i, 'low']
        now_close = df.loc[context.i, 'close']
        now_pct_chg = df.loc[context.i, 'pct_chg']

        print(f"{now_date} {now_open} {now_high} {now_low} {now_close} {now_pct_chg}")
        ### strategy specific factors
        


        ### trade logic



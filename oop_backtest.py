import pandas as pd
import itertools
from typing import Dict, List, Tuple
from abc import ABC, abstractmethod
import numpy as np

def weighted_average(list_of_tuples: List[Tuple[float, float]]):
    """[(weight, measurement), ...]"""
    if len(list_of_tuples) == 0:
        return 0
    
    sum_of_weight = sum([w for w,m in list_of_tuples])
    
    if sum_of_weight == 0:
        return 0
        
    return sum([(w/sum_of_weight)*m for w,m in list_of_tuples])
    
print(weighted_average([(50,10),(20,11),(-70, 12)]))


class BacktestRunner(ABC):
    """BacktestRunner Version 0.0.1"""
    
    def __init__(self, df, warm_up, lot_size, debug=True):
        self.debug = debug
        self.df = df
        self.warm_up = warm_up
        self.lot_size = lot_size
        
        self.pos_list = [(0,0)]

        self.records = {
            'trade_open_list': [],
            'trade_close_list': [],
            'pnl_list' : [],
            'equity_list' : [],
            'dd_dollar_list' : [],
            'dd_pct_list' : []
        }
    
    @abstractmethod    
    def onData(self, i, params):
        return
        
        
    def market_data(self, i, name):
        if name in self.df.columns:
            return self.df.loc[i, name]
        else:
            raise Exception(f"Column name {name} not found in df.")
    
    def open_position(self, pos_open_price, pos_open_lots):


        # updated total position lots and average open price after opening position
        self.pos_list.append((pos_open_lots, pos_open_price))
        avg_open_price = weighted_average(self.pos_list)
        pos_lots = self.pos_list[0][0] + pos_open_lots
        self.pos_list = []
        self.pos_list.append((pos_lots, avg_open_price))
        
        
        if self.debug:
            print(f"""\n
                [Position Open] {pos_open_lots} Lots @ Price = {pos_open_price}
            """)
        self.records['trade_open_list'].append((pos_open_lots, pos_open_price))
        
        return True
    
    
    def close_position(self, pos_close_price, pos_close_lots):

        if self.pos_list[0][0] >= pos_close_lots:
            
            shares = pos_close_lots * self.lot_size
            pnl_share = pos_close_price - self.pos_list[0][1]
            pnl = pnl_share * shares
            
            self.records['pnl_list'].append(pnl)
            
            if self.debug:
                print(f"""\n
                    [Position Close] {pos_close_lots} Lots @ Price = {pos_close_price}
                """)
                
            # updated total position lots after closing position, avg price unchange
            self.pos_list[0][0] = self.pos_list[0][0] - pos_close_lots
            
            # If all position close, reset
            if self.pos_list[0][0] == 0:
                self.pos_list = [(0,0)]
            
            self.records['trade_close_list'].append((pos_close_lots, pos_close_price))
            
            return True
            
        else:
            raise Exception("Error when closing position. Number of Lots exceed position lots")
        
    
        
    def create_backtest(self, params):
        for i in range(self.warm_up, len(self.df)):
            
            # 1. Basic Market Data
            if self.debug:
                print(f""" \n
                    iteration = {i}
                    now_open: {self.market_data(i,'open')} 
                    now_high: {self.market_data(i,'high')} 
                    now_low: {self.market_data(i,'low')} 
                    now_close: {self.market_data(i,'close')} 
                    now_time: {self.market_data(i,'time')} 
                    now_volume: {self.market_data(i,'volume')} 
                """)
                
            # 2. Equity Recording
            unrealize_pnl = round(self.pos_list[0][0] * self.lot_size * (self.market_data(i,'close') - self.pos_list[0][1]), 0)
            realize_pnl = round(sum(self.records['pnl_list']), 0)
            
            equity = round(realize_pnl + unrealize_pnl, 0)
            self.records['equity_list'].append(equity)
            
            highest_equity = max(self.records['equity_list'])

            dd_dollar = highest_equity - equity
            dd_pct = (equity / highest_equity) - 1
            self.records['dd_dollar_list'].append(dd_dollar)
            if np.isnan(dd_pct):
                dd_pct = 0
            self.records['dd_pct_list'].append(dd_pct)
            
            if self.debug:
                print(f"""\n
                
                    avg_open_price: {self.pos_list[0][1]}
                    pos_lots : {self.pos_list[0][0]}
                    unrealize_pnl: {unrealize_pnl}
                    realize_pnl: {realize_pnl}
                    pnl_list: {self.records['pnl_list']}
                    equity_list: {self.records['equity_list']}
                    dd_dollar_list: {self.records['dd_dollar_list']}
                    dd_pct_list: {self.records['dd_pct_list']}
                """)
                
            self.onData(i, params)
        
        
            if is_last and self.pos_list[0][0] != 0:
                self.close_position(self.market_data(i,'close'), self.pos_list[0][0])
        


class Strategy(BacktestRunner):
    def __init__(self, df, warm_up, lot_size, debug=True):
        super().__init__(df, warm_up, lot_size, debug)
    
    def onData(self,i,params):
        print(f"[On Data] i={i}, params={params}")
        # 3. Define Trading Logic
        
        # 4. Close Position
        
        # 5. Open Position
        

    

 
        
        
data = {
        "time": ["01092022", "02092022", "03092022", "04092022", "05092022", "06092022", "07092022", "08092022", "09092022",
                 "10092022", "11092022", "12092022", "13092022", "14092022"],
        "open": [99, 101, 102, 103, 103.5, 103.8, 105.1, 106, 105, 112, 105.2, 105.1, 103.9, 104],
        "high": [99, 101, 102, 103, 103.5, 103.8, 105.1, 106, 105, 112, 105.2, 105.1, 103.9, 104],
        "low": [99, 101, 102, 103, 103.5, 103.8, 105.1, 106, 105, 112, 105.2, 105.1, 103.9, 104],
        "close": [100, 102, 104, 103.5, 103.7, 105.1, 106, 104.9, 105.2, 105.1, 103.8, 104, 104.5, 104.7],
        "volume": [10000, 10000, 10000, 10000.5, 10000.7, 10000.1, 10000, 10000.9, 10000.2, 10000.1, 10000.8, 10000, 10000.5, 10000.7]
    }

params = {}
df = pd.DataFrame(data)                
strategy = Strategy(df, 1, 100)
strategy.create_backtest(params)




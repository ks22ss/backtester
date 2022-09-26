import pandas as pd
import itertools


class BacktestRunner():
    
    def __init__(self, df, warm_up, lot_size, debug=True):
        self.debug = debug
        self.df = df
        self.warm_up = warm_up
        self.lot_size = lot_size
        
        self.pos_states = {
            'pos_lots': 0,
            'pos_open_price': 0,
            'pos_close_price': 0
        }
        self.records = {
            'pnl_list' : [],
            'equity_list' : [],
            'dd_dollar_list' : [],
            'dd_pct_list' : []
        }
        
    def market_data(self, i, name):
        if name in self.df.columns:
            return self.df.loc[i, name]
        else:
            raise Exception(f"Column name {name} not found in df.")
    
    def get_pos_state(self, name):
        """
        pos_lots(Int): Number of Lots in current Position
        pos_open_price(Float): Open Price of current Position
        pos_close_price(Float): Close Price of current Position
        """
        return self.pos_states[name]
    
    def open_position(self, pos_open_price, pos_open_lots):
        print("Opening Position...")
        
        self.pos_states['pos_lots'] = pos_open_lots
        self.pos_states['pos_open_price'] = pos_open_price
        
        if self.debug:
            print(f"""\n
                Position Open @ Price = {self.pos_states['pos_open_price']}
            """)
    
    
    def close_position(self, pos_close_price, pos_close_lots):
        print("Closing Position...")
        
        self.pos_states['pos_close_price'] = pos_close_price
        
        pnl_share = (self.pos_states['pos_close_price'] - self.pos_states['pos_open_price']) 
        shares = pos_close_lots * self.lot_size
        pnl = pnl_share * shares
        
        self.records['pnl_list'].append(pnl)
        
        if self.pos_states['pos_lots'] >= pos_close_lots:
            self.pos_states['pos_lots'] = self.pos_states['pos_lots'] - pos_close_lots
        else:
            raise Exception("Number of Lots exceed position lots")
        
        if self.debug:
            print(f"""\n
                Position Close @ Price = {self.pos_states['pos_close_price']}
            """)
            
        self.reset_pos_state()
    
    def reset_pos_state(self):
        self.pos_states = {
            'pos_lots': 0,
            'pos_open_price': 0,
            'pos_close_price': 0
        }
    
        
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
            unrealize_pnl = round(self.pos_states['pos_lots'] * self.lot_size * (self.market_data(i,'close') - self.pos_states['pos_open_price']), 0)
            realize_pnl = round(sum(self.records['pnl_list']), 0)
            
            equity = round(realize_pnl + unrealize_pnl, 0)
            self.records['equity_list'].append(equity)
            
            highest_equity = max(self.records['equity_list'])
            dd_dollar = highest_equity - equity
            dd_pct = (equity / highest_equity) - 1
            self.records['dd_dollar_list'].append(dd_dollar)
            self.records['dd_pct_list'].append(dd_pct)
            
            if self.debug:
                print(f"""\n
                    pos_open_price: {self.pos_states['pos_open_price']}
                    pos_close_price: {self.pos_states['pos_close_price']}
                    pos_lots : {self.pos_states['pos_lots']}
                    unrealize_pnl: {unrealize_pnl}
                    realize_pnl: {realize_pnl}
                    pnl_list: {self.records['pnl_list']}
                    equity_list: {self.records['equity_list']}
                    dd_dollar_list: {self.records['dd_dollar_list']}
                    dd_pct_list: {self.records['dd_pct_list']}
                """)
                
            # 3. Trading Logic
            entry_logic = self.entry_logic(i, params)
            exit_logic = self.exit_logic(i, params)
            is_last = i == len(df)-1
            
                
            # 4. Close Position
            if self.pos_states['pos_lots'] != 0 and is_last and exit_logic_tp and exit_logic_sl:
                
                self.pos_states['pos_close_price'] = self.market_data(i,'close')
                
                pnl = (self.pos_states['pos_close_price'] - self.pos_states['pos_open_price']) * self.pos_states['pos_lots'] * self.lot_size
                self.records['pnl_list'].append(pnl)
                
                if self.debug:
                    print(f"""\n
                        Position Close @ Price = {self.pos_states['pos_close_price']}
                    """)
                    
                self.pos_states['pos_lots'] = 0
                self.pos_states['pos_open_price'] = 0
                self.pos_states['pos_close_price'] = 0
            
            
            # 5. Open Position
            if self.pos_states['pos_lots'] == 0 and entry_logic:
                self.pos_states['pos_lots'] = 1
                self.pos_states['pos_open_price'] = self.market_data(i,'close')
                
                if self.debug:
                    print(f"""\n
                        Position Open @ Price = {self.pos_states['pos_open_price']}
                    """)
        
        


class Strategy(BacktestRunner):
    def __init__(self, df, warm_up, lot_size, debug=True):
        super().__init__(df, warm_up, lot_size, debug)
    
    def entry_logic(self,i ,params):
        pass
    
        return True

    def exit_logic(self,i ,params):
        pass
    
        return True
        

    

 
        
        
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
                
                

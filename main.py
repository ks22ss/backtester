from Backtester import Backtester
import yfinance as yf

class MyCustomStrategy(Backtester):
    def __init__(self, para_dict={}, configs={}):
        super().__init__(para_dict, configs)

    def onData(self, df, context, params):

        # Get Market Data
        now_date = df.loc[context.i, 'date']
        now_open = df.loc[context.i, 'open']
        now_high = df.loc[context.i, 'high']
        now_low = df.loc[context.i, 'low']
        now_close = df.loc[context.i, 'close']
        now_pct_chg = df.loc[context.i, 'pct_chg']

        #print(f"{now_date} {now_open} {now_high} {now_low} {now_close} {now_pct_chg}")

        ### trade logic
        if context.num_of_share == 0 and now_pct_chg > params['thershold'] / 100:
            self.open_position()
        
        if context.num_of_share > 0 and (now_close - context.open_price) > (context.open_price * params['take_profit'] / 100):
            self.close_position()

        elif context.num_of_share > 0 and (context.open_price - now_close) > (context.open_price * params['stop_loss'] / 100):
            self.close_position()

if __name__ == '__main__':

    # Download Data
    start_date = "2022-06-01"
    end_date = "2022-08-05"
    data1 = yf.Ticker('SPY').history(start=start_date, end=end_date)

    # Create some factors
    data1['pct_chg'] = data1['Close'].pct_change()

    # Create a strategy
    b = MyCustomStrategy(para_dict={
        'thershold': [1],
        'stop_loss': [1,2,3],
        'take_profit':[2,4,6]
    })
    b.add_df(data1, 'SPY')
    b.backtest('SPY', params=b.para_combinations[0])


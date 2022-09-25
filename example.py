import pandas as pd
import itertools


# Helper Functions
def generate_param_set(**kwarg):
    param_keys = list(kwarg)
    param_values = list(kwarg.values())
    return param_keys, [dict(zip(param_keys, comb)) for comb in list(itertools.product(*param_values))]


# Data
data = {
    "time": ["01092022", "02092022", "03092022", "04092022", "05092022", "06092022", "07092022", "08092022", "09092022",
             "10092022", "11092022", "12092022", "13092022", "14092022"],
    "open": [99, 101, 102, 103, 103.5, 103.8, 105.1, 106, 105, 112, 105.2, 105.1, 103.9, 104],
    "close": [100, 102, 104, 103.5, 103.7, 105.1, 106, 104.9, 105.2, 105.1, 103.8, 104, 104.5, 104.7]
}

df = pd.DataFrame(data)

# Factors
df['pct_change'] = df['close'].pct_change()


def backtest(params, debug=True):
    # Initizalize
    lot_size = 100
    pos_lots = 0
    pos_open_price = 0
    pos_close_price = 0
    pnl = 0

    # Export List
    pnl_list = []
    equity_list = []
    dd_dollar_list = []
    dd_pct_list = []

    if debug:
        print(params)

    # Main Loop
    for i in range(params['warm_up'], len(df)):

        # 1. Market Data
        now_time = df.loc[i, 'time']
        now_close = df.loc[i, 'close']
        now_open = df.loc[i, 'open']
        now_pct_change = df.loc[i, 'pct_change']

        if debug:
            print(f"[{now_time}] [MARKET] Current Close {now_close} | Pct Change {now_pct_change}")

        # 2. Define Trading Logic
        entry_logic = now_pct_change < params['thershold']
        exit_logic_tp = now_close > pos_open_price * (1 + params['take_profit'])
        exit_logic_sl = now_close < pos_open_price * (1 - params['stop_loss'])
        is_last = i == len(df) - 1

        # 3. Equity
        unrealize_pnl = round(pos_lots * lot_size * (now_close - pos_open_price), 0)
        realize_pnl = round(sum(pnl_list), 0)
        equity = round(realize_pnl + unrealize_pnl, 0)
        equity_list.append(equity)
        highest_equity = max(equity_list)
        dd_dollar = highest_equity - equity
        dd_pct = (equity / highest_equity) - 1
        dd_dollar_list.append(dd_dollar)
        dd_pct_list.append(dd_pct)

        if debug:
            print(
                f"[{now_time}]   [ACCOUNT] Current Equity = {equity} | Unrealized PnL = {unrealize_pnl} | Realized PnL = {realize_pnl}")

        # 4. Close Position
        if pos_lots != 0 and (exit_logic_tp or exit_logic_sl or is_last):
            pos_close_price = now_close
            pnl = pos_lots * lot_size * (pos_close_price - pos_open_price)
            pnl_list.append(pnl)

            if debug:
                print(f"[{now_time}]   [TRADE] Position Closed @ price = {pos_close_price}")

            pos_lots = 0
            pos_close_price = 0
            pos_open_price = 0

        # 5. Open Position
        if pos_lots == 0 and entry_logic:
            pos_open_price = now_close
            pos_lots = 1

            if debug:
                print(f"[{now_time}]   [TRADE] Position Opened @ price = {pos_open_price}")

    # 6. Result
    return list(params.values()) + [sum(pnl_list)]


# Parameter to Optimize
warm_up = [1]
thershold = [-0.001, -0.002, -0.003]
take_profit = [0.01, 0.02, 0.03]
stop_loss = [0.01, 0.02]

param_keys, param_list = generate_param_set(warm_up=warm_up,
                                            thershold=thershold,
                                            take_profit=take_profit,
                                            stop_loss=stop_loss)

# Begin Optimization
results = [backtest(combination, debug=False) for combination in param_list]

# Label and Organize Results
columns = param_keys + ["total_pnl"]
result_df = pd.DataFrame(results, columns=columns) \
 \
    print(result_df)
import pandas as pd

df = pd.read_pickle('ticker_with_rsi_macd_df.pkl')
# df.to_excel("raw_data.xlsx")


stock_list = pd.Series({'ticker': df['ticker'].unique()})['ticker']
print(stock_list)
# stock_list = []
count_1 = 0
count_2 = 0
def localMinima(df, ind, col, row):
    try:
        if(row == 0 or row >= (df.shape[0]-1)):
            return False
        return (df[col][ind-1] > df[col][ind]) and (df[col][ind] < df[col][ind+1])
    except:
        global count_1
        count_1 = count_1 + 1
        return False

def localMaxima(df, ind, col, row):
    try:
        if(row == 0 or row >= (df.shape[0]-1)):
            return False
        # print(type(df[col][ind-1] ))
        return (df[col][ind-1] < df[col][ind]) and (df[col][ind] > df[col][ind+1]) 
    except:
        global count_2
        count_2 = count_2 + 1
        # print("as")
        return False

def addBuySell(df):
    df['call'] = 'hold'
    win=0 
    loose = 0
    stock_in_hand = False
    buy = 0
    buy_date = ""
    sell = 0
    row = 0
    total_profit = 0
    # print(df['Date'][ind])
    max_profit = -1
    max_profit_buy = 0
    max_profit_buy_date= 0
    max_profit_sell= 0
    max_profit_sell_date= 0
    for ind in df.index:
        # print(df['Date'][ind])
        # if(df['Date'][ind]=="2021-11-29" or df['Date'][ind]=="2021-11-28" or df['Date'][ind]=="2021-11-30"):
        #     print("date: , macd: ", df['Date'][ind], df['macd'][ind])
        ticker = df['ticker'][ind]
        if(localMinima(df, ind, "macd_h", row)):
            df['call'][ind] = 'buy'
            #buy call
            stock_in_hand = True
            buy = df['Open'][ind+1]
            buy_date = df['Date'][ind]
        elif(localMaxima(df, ind, "macd_h", row)):
            df['call'][ind] = 'sell'
            #sell call
            if(stock_in_hand):
                
                # print("buy: ", buy_date, buy)
                # print("sell: ",  df['Date'][ind] , df['Open'][ind+1])
                sell = df['Open'][ind+1]

                if(max_profit < (sell-buy)):
                    max_profit = sell-buy
                    max_profit_buy = buy
                    max_profit_buy_date = buy_date
                    max_profit_sell =  df['Open'][ind+1]
                    max_profit_sell_date = df['Date'][ind]
                total_profit = total_profit + (sell- buy)

                stock_in_hand = False
                if(buy < sell):
                    win = win+1
                else:
                    # print("loss")
                    # print("buy: ", buy_date, buy)
                    # print("sell: ",  df['Date'][ind] , df['Open'][ind+1])
                    loose = loose+1
        row= row+1
    # print("max profit")
    # print(max_profit)
    # print(max_profit_buy)
    # print(max_profit_buy_date)
    # print(max_profit_sell)
    # print(max_profit_sell_date)

    return df, win, loose , total_profit 
     
total_profit_all_stocks = 0
list_to_be_sorted = []
final_df = pd.DataFrame()
for stock in stock_list:
    print(stock)
    stock_df = df.query("ticker == @stock").sort_values(by = 'Date')
    stock_df, win, loose, total_profit = addBuySell(stock_df)
    total_profit_all_stocks = total_profit_all_stocks + total_profit
    # print(stock_df.query("Date == '2021-12-18'"))
    # print(stock_df.query("Date == '2021-12-21'"))
    # print(stock_df.query("Date == '2021-12-22'"))
    # print(count_1)
    # print(count_2)
    # print(stock_df)\
    print("added")
    final_df = final_df.append(stock_df, ignore_index=False)
    # diff = loose - win
    # if(diff> 0):
    #     print("bekar: ",stock)
    # elif(win/(loose+win) < .80):
    #     print("win percentage kam: ",stock)

    # win_percentage = win/(win+loose)



    # if(win!=0 and loose!=0):
    #     count_1 = count_1 + win
    #     count_2 = count_2 + loose
        # print("win: ",win)
        # print("loose: ",loose)
    # else:
        # print("bug")
    
    # list_to_be_sorted[win_percentage].add(stock)
    # list_to_be_sorted.append((win_percentage, stock))

print(count_1/(count_1+count_2))
print(total_profit_all_stocks)
print(count_1+count_2)
print("here final df")
print(final_df)
final_df.to_excel("raw_data.xlsx")

list_to_be_sorted.sort(key=lambda x: x[0])
print(list_to_be_sorted)
# newlist = sorted(list_to_be_sorted, key=itemgetter('win_percentage'), reverse=True)


# for ind in df.index:
#      ticker = df['ticker'][ind]+".NS" # or add .BO
#      company_name = df['Name'][ind]
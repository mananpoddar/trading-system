from bs4 import BeautifulSoup
import requests
import pandas as pd
import yfinance as yf
import numpy as np

url="https://www.screener.in/screen/raw/"
cookies = {'cookie': '_gcl_au=1.1.1388682109.1648099202; csrftoken=YM9mQCOHBjl9LfzTIYQDQ95lRVBj18s5qpEo75e9pbOWLUnbCfl0xNfPEBqYxWlV; sessionid=hz32q3qvhdhwnl3uam2drp3j8rqpmrv6'}
# Defining of the dataframe
df = pd.DataFrame(columns=['S_NO', 'Name', 'CMP', 'P_E', 'Mar_cap', 'div_yeild', 'np_qtr', 'Qtr_Profit_Var ', 'sales_qtr', 'qtr_sales_var', 'roce', 'ticker'])
for i in range(1, 10):

    params = {'query': "Sales growth 3Years > 15 AND Profit growth 3Years > 15 AND Return on equity > 15 AND Return on capital employed > 15 AND Pledged percentage < 5 AND Sales growth > 15 AND Profit growth > 15 AND Market Capitalization > 1000 AND Net Profit latest quarter > Net Profit preceding quarter", 'page':i}

    # Make a GET request to fetch the raw HTML content
    html_content = requests.get(url,  params=params, cookies=cookies).text

    # Parse the html content
    soup = BeautifulSoup(html_content, "lxml")
    # print(soup.prettify()) # print the parsed data of html
    # df = {}
    # Collecting Ddata
    for row in soup.find_all('tr'):    
        # Find all data for each column
        columns = row.find_all('td')
        
        if(columns != []):
            sno = columns[0].text.strip()
            name = columns[1].text.strip()
            CMP = columns[2].text.strip()
            pe = columns[3].text.strip()
            mar_cap = columns[4].text.strip()
            div_yeild = columns[5].text.strip()
            np_qtr = columns[6].text.strip()
            qtr_profit_val = columns[7].text.strip()
            sales_qtr = columns[8].text.strip()
            qtr_sales_var = columns[9].text.strip()
            roce = columns[10].text.strip()
            ticker = columns[1].find('a')['href'].split("/")[2]
            df = df.append({'S_NO': sno,  'Name': name, 'CMP': CMP, 
            'P_E': pe, 'Mar_cap': mar_cap, 'div_yeild': div_yeild
            ,'np_qtr': np_qtr,  'Qtr_Profit_Var': qtr_profit_val, 'sales_qtr': sales_qtr, 
            'qtr_sales_var':qtr_sales_var, 'roce': roce, 'ticker':ticker}, 
            ignore_index=True)

# df.head()
print(df)
# print(df.count())


#df contains fundamentally good stocks

#now get the time series data for these stocks to do TA
def calculateMACD(df):
    try:
        # Get the 26-day EMA of the closing price
        k = df['Close'].ewm(span=12, adjust=False).mean()
        # Get the 12-day EMA of the closing price
        d = df['Close'].ewm(span=26, adjust=False).mean()
        # Subtract the 26-day EMA from the 12-Day EMA to get the MACD
        macd = k - d
        # Get the 9-Day EMA of the MACD for the Trigger line
        macd_s = macd.ewm(span=9, adjust=False).mean()
        # Calculate the difference between the MACD - Trigger for the Convergence/Divergence value
        macd_h = macd - macd_s
        # Add all of our new values for the MACD to the dataframe
        df['macd'] = df.index.map(macd)
        df['macd_h'] = df.index.map(macd_h)
        df['macd_s'] = df.index.map(macd_s)
        return df
    except:
        return df

def calculateRSI(df):
     ## 14_Day RSI
    try:

    
        df['Adj Close'] = df['Close']
        df['Up Move'] = np.nan
        df['Down Move'] = np.nan
        df['Average Up'] = np.nan
        df['Average Down'] = np.nan
        # Relative Strength
        df['RS'] = np.nan
        # Relative Strength Index
        df['RSI'] = np.nan
        ## Calculate Up Move & Down Move
        for x in range(1, len(df)):
            df['Up Move'][x] = 0
            df['Down Move'][x] = 0
            
            if df['Adj Close'][x] > df['Adj Close'][x-1]:
                df['Up Move'][x] = df['Adj Close'][x] - df['Adj Close'][x-1]
                
            if df['Adj Close'][x] < df['Adj Close'][x-1]:
                df['Down Move'][x] = abs(df['Adj Close'][x] - df['Adj Close'][x-1])  
                
        ## Calculate initial Average Up & Down, RS and RSI
        df['Average Up'][14] = df['Up Move'][1:15].mean()
        df['Average Down'][14] = df['Down Move'][1:15].mean()
        df['RS'][14] = df['Average Up'][14] / df['Average Down'][14]
        df['RSI'][14] = 100 - (100/(1+df['RS'][14]))
        ## Calculate rest of Average Up, Average Down, RS, RSI
        for x in range(15, len(df)):
            df['Average Up'][x] = (df['Average Up'][x-1]*13+df['Up Move'][x])/14
            df['Average Down'][x] = (df['Average Down'][x-1]*13+df['Down Move'][x])/14
            df['RS'][x] = df['Average Up'][x] / df['Average Down'][x]
            df['RSI'][x] = 100 - (100/(1+df['RS'][x]))
        return df
    except:
        return df

ticker_with_rsi_macd_df = pd.DataFrame(columns=['Date','Open', 'High', 'Low', 'Close', 'Volume', 'Dividends', 'Stock Splits',
       'Adj Close', 'Up Move', 'Down Move', 'Average Up', 'Average Down', 'RS',
       'RSI', 'macd', 'macd_h', 'macd_s', 'ticker', 'company_name'])
for ind in df.index:
     ticker = df['ticker'][ind]+".NS" # or add .BO
     company_name = df['Name'][ind]
     yfInfo = yf.Ticker(ticker)
     hist = yfInfo.history(period="1d")
     if(len(hist)==0):
        ticker = df['ticker'][ind]+".BO" # or add .BO
        yfInfo = yf.Ticker(ticker)
        hist = yfInfo.history(period="1d")
     ticker_with_rsi_macd = calculateRSI(hist)
     ticker_with_rsi_macd = calculateMACD(ticker_with_rsi_macd)
     ticker_with_rsi_macd['ticker'] = ticker
     ticker_with_rsi_macd['company_name'] = company_name   
     print(ticker_with_rsi_macd.reset_index(inplace = True)) 
     print("add")
    #  ticker_with_rsi_macd_df = pd.concat([ticker_with_rsi_macd, ticker_with_rsi_macd_df], axis=1) 
     ticker_with_rsi_macd_df = ticker_with_rsi_macd_df.append(ticker_with_rsi_macd, ignore_index = True)
    #  print(ticker_with_rsi_macd_df)
     print("added")
    #  if ind > 2:
    #      break
 
print(ticker_with_rsi_macd_df.columns)
print(ticker_with_rsi_macd_df)
ticker_with_rsi_macd_df.to_pickle("./ticker_with_rsi_macd_df.pkl")  




import logging
from kiteconnect import KiteConnect
from kiteconnect import KiteTicker
import pandas as pd
import traceback

import datetime,time,os,random;

trd_portfolio = {779521: "SBIN"}

lastValue = 0;
quantity = 4000;
overall_profit = 0
kws = "";
kite = "";

api_k = "dysoztj41hntm1ma";  # api_key
api_s = "rzgyg4edlvcurw4vp83jl5io9b610x94";  # api_secret
access_token = "huIDGdTuSOSwC474ZImq1Ng6Isz5Ta63"
kws = KiteTicker(api_k, access_token)
self = KiteConnect(api_key=api_k, access_token=access_token)

#def TrueRange()

ohlc = {};  # python dictionary to store the ohlc data in it
ohlc_temp = pd.DataFrame(columns=["Symbol","Time", "Open", "High", "Low", "Close", "TR","ATR","SMA","TMA"])
ohlc_final_1min = pd.DataFrame(columns=["Symbol","Time", "Open", "High", "Low", "Close", "TR", "ATR","SMA","TMA"])
RENKO = {};  # python dictionary to store the renko chart data in it
RENKO_temp = pd.DataFrame(columns=["Symbol","Open", "Close", "Signal", "Position"])
RENKO_Final = pd.DataFrame(columns=["Symbol","Open", "Close", "Signal", "Position"])
profit = {};
profit_temp = pd.DataFrame(columns=["Symbol", "SELL Price", "BUY Price", "Profit"])
profit_Final = pd.DataFrame(columns=["Symbol", "SELL Price", "BUY Price", "Profit"])

for x in trd_portfolio:
    ohlc[x] = ["Symbol", "Time", 0, 0, 0, 0, 0, 0, 0, 0];  # [Symbol, Traded Time, Open, High, Low, Close, True Range, Average True Range, Simple Moving Average, Triangular moving average]
    RENKO[x] = ["Symbol", 0, 0, "Signal", "None"];
    profit[x] = ["Symbol", 0, 0, "Profit"]

def positions(token):
    pos = self.positions()['day']
    posdf = pd.DataFrame(pos)
    if posdf.empty:
        return 0
    else:
        final_pos = posdf.loc[posdf['instrument_token'] == token, ['quantity']]
        return final_pos.iloc[0, 0]


def calculate_ohlc_one_minute(company_data):
    global ohlc_final_1min, ohlc_temp, RENKO_temp, RENKO_Final
    try:
        # below if condition is to check the data being received, and the data present are of the same minute or not
        if (str(((company_data["timestamp"]).replace(second=0))) != ohlc[company_data['instrument_token']][1]) and (ohlc[company_data['instrument_token']][1]!= "Time"):
            ohlc_temp = pd.DataFrame([ohlc[x]], columns=["Symbol","Time", "Open", "High", "Low", "Close","TR","ATR","SMA","TMA"])
        # Calculating True Range
            if (len(ohlc_final_1min) > 0):
                ohlc_temp.iloc[-1, 6] = max((abs((ohlc_temp.iloc[-1, 3]) - (ohlc_temp.iloc[-1, 4])),
                                                   abs((ohlc_temp.iloc[-1, 3]) - (ohlc_final_1min.iloc[-1, 4])),
                                                   abs((ohlc_temp.iloc[-1, 4]) - (ohlc_final_1min.iloc[-1, 4]))))
            else:
                ohlc_temp.iloc[-1, 6] = (abs((ohlc_temp.iloc[-1, 3]) - (ohlc_temp.iloc[-1, 4])))
        # True Range Calculation complete
        # Calculating ATR
            if (len(ohlc_final_1min)<13):
                ohlc_temp.iloc[-1, 7] = 0

            elif (len(ohlc_final_1min) == 13):
                a = [ohlc_temp.iloc[-1, 6], ohlc_final_1min.iloc[-1, 6], ohlc_final_1min.iloc[-2, 6], ohlc_final_1min.iloc[-3, 6], ohlc_final_1min.iloc[-4, 6],
                     ohlc_final_1min.iloc[-5, 6], ohlc_final_1min.iloc[-6, 6], ohlc_final_1min.iloc[-7, 6], ohlc_final_1min.iloc[-8, 6], ohlc_final_1min.iloc[-9, 6],
                ohlc_final_1min.iloc[-10, 6], ohlc_final_1min.iloc[-11, 6], ohlc_final_1min.iloc[-12, 6]]
                ohlc_temp.iloc[-1, 7] = sum(a)/13

            elif (len(ohlc_final_1min) > 13):
                ohlc_temp.iloc[-1, 7] = ((ohlc_final_1min.iloc[-1, 7]*13) + ohlc_temp.iloc[-1, 6])/14
        # Calculating ATR complete
        # Calculating SMA
            if (len(ohlc_final_1min) < 10):
                ohlc_temp.iloc[-1, 8] = 0
            elif (len(ohlc_final_1min) >= 10):
                b = [ohlc_temp.iloc[-1, 5], ohlc_final_1min.iloc[-1, 5], ohlc_final_1min.iloc[-2, 5], ohlc_final_1min.iloc[-3, 5], ohlc_final_1min.iloc[-4, 5],
                     ohlc_final_1min.iloc[-5, 5], ohlc_final_1min.iloc[-6, 5], ohlc_final_1min.iloc[-7, 5], ohlc_final_1min.iloc[-8, 5], ohlc_final_1min.iloc[-9, 5]]
                ohlc_temp.iloc[-1, 8] = sum(b) / 10
        # SMA Calculation complete

        # Calculating Triangular moving average
            if (len(ohlc_final_1min) < 19):
                ohlc_temp.iloc[-1, 9] = 0
            elif (len(ohlc_final_1min) >= 19):
                c = [ohlc_temp.iloc[-1, 8], ohlc_final_1min.iloc[-1, 8], ohlc_final_1min.iloc[-2, 8], ohlc_final_1min.iloc[-3, 8], ohlc_final_1min.iloc[-4, 8],
                     ohlc_final_1min.iloc[-5, 8], ohlc_final_1min.iloc[-6, 8], ohlc_final_1min.iloc[-7, 8], ohlc_final_1min.iloc[-8, 8], ohlc_final_1min.iloc[-9, 8]]
                ohlc_temp.iloc[-1, 9] = sum(c) / 10
        # TMA calculation complete

        # adding the row into the final ohlc table
            ohlc_final_1min = ohlc_final_1min.append(ohlc_temp)
            print(ohlc[company_data['instrument_token']][0], ":", ohlc[company_data['instrument_token']][1], ":", ohlc[company_data['instrument_token']][2], ":",
                  ohlc[company_data['instrument_token']][3], ":", ohlc[company_data['instrument_token']][4], ":", ohlc[company_data['instrument_token']][5])

            # making ohlc for new candle
            ohlc[company_data['instrument_token']][2] = company_data['last_price'];  # open
            ohlc[company_data['instrument_token']][3] = company_data['last_price'];  # high
            ohlc[company_data['instrument_token']][4] = company_data['last_price'];  # low
            ohlc[company_data['instrument_token']][5] = company_data['last_price'];  # close
            ohlc[company_data['instrument_token']][0] = trd_portfolio[company_data['instrument_token']];

        if ohlc[company_data['instrument_token']][3] < company_data['last_price']:  # calculating high
            ohlc[company_data['instrument_token']][3] = company_data['last_price']

        if ohlc[company_data['instrument_token']][4] > company_data['last_price'] or \
                ohlc[company_data['instrument_token']][4] == 0:  # calculating low
            ohlc[company_data['instrument_token']][4] = company_data['last_price']

        ohlc[company_data['instrument_token']][5] = company_data['last_price']  # closing price
        ohlc[company_data['instrument_token']][1] = str(((company_data["timestamp"]).replace(second=0)));

        if len(ohlc_final_1min) > 0:  #checking if there is atleast 1 candle in OHLC Dataframe
            if ohlc_final_1min.iloc[-1, 7] != 0:  #checking that we do not have the ATR value as 0
                if RENKO[company_data['instrument_token']][0] == "Symbol":
                    RENKO[company_data['instrument_token']][0] = trd_portfolio[company_data['instrument_token']];
                ########################################################
                if RENKO[company_data['instrument_token']][1] == 0:  # assigning the first, last price of the tick to open
                    RENKO[company_data['instrument_token']][1] = company_data['last_price']
                ########################################################
                if RENKO[company_data['instrument_token']][3] == "Signal":
                    if (company_data['last_price'] >= ohlc_final_1min.iloc[-1, 7] + RENKO[company_data['instrument_token']][1]):
                        RENKO[company_data['instrument_token']][2] = RENKO[company_data['instrument_token']][1] + ohlc_final_1min.iloc[-1, 7]
                        RENKO[company_data['instrument_token']][3] = "BUY"
                        RENKO_temp = pd.DataFrame([RENKO[x]], columns=["Symbol", "Open", "Close", "Signal", "Position"])
                        RENKO_Final = RENKO_Final.append(RENKO_temp, sort=False)
                        #print(RENKO_Final.tail(3))
                        RENKO[company_data['instrument_token']][1] = RENKO_Final.iloc[-1, 2]
                    elif (company_data['last_price']<= RENKO[company_data['instrument_token']][1] - ohlc_final_1min.iloc[-1, 7]):
                        RENKO[company_data['instrument_token']][2] = RENKO[company_data['instrument_token']][1] - ohlc_final_1min.iloc[-1, 7]
                        RENKO[company_data['instrument_token']][3] = "SELL"
                        RENKO_temp = pd.DataFrame([RENKO[x]], columns=["Symbol", "Open", "Close", "Signal", "Position"])
                        RENKO_Final = RENKO_Final.append(RENKO_temp, sort=False)
                        #print(RENKO_Final.tail(3))
                        RENKO[company_data['instrument_token']][1] = RENKO_Final.iloc[-1, 2]

                if RENKO[company_data['instrument_token']][3] == "BUY":
                    if (company_data['last_price'] >= ohlc_final_1min.iloc[-1, 7] + RENKO[company_data['instrument_token']][1]):
                        RENKO[company_data['instrument_token']][2] = RENKO[company_data['instrument_token']][1] + ohlc_final_1min.iloc[-1, 7]
                        RENKO[company_data['instrument_token']][3] = "BUY"
                        RENKO_temp = pd.DataFrame([RENKO[x]], columns=["Symbol", "Open", "Close", "Signal", "Position"])
                        RENKO_Final = RENKO_Final.append(RENKO_temp, sort=False)
                        #print(RENKO_Final.tail(3))
                        RENKO[company_data['instrument_token']][1] = RENKO_Final.iloc[-1, 2]
                    elif company_data['last_price'] <= RENKO[company_data['instrument_token']][1] - (RENKO_Final.iloc[-1, 2] - RENKO_Final.iloc[-1, 1]) - ohlc_final_1min.iloc[-1, 7]:
                        RENKO[company_data['instrument_token']][1] = RENKO_Final.iloc[-1, 1]
                        RENKO[company_data['instrument_token']][2] = RENKO_Final.iloc[-1, 1] - ohlc_final_1min.iloc[-1, 7]
                        RENKO[company_data['instrument_token']][3] = "SELL"
                        RENKO_temp = pd.DataFrame([RENKO[x]], columns=["Symbol", "Open", "Close", "Signal", "Position"])
                        RENKO_Final = RENKO_Final.append(RENKO_temp, sort=False)
                        #print(RENKO_Final.tail(3))
                        RENKO[company_data['instrument_token']][1] = RENKO_Final.iloc[-1, 2]
                if RENKO[company_data['instrument_token']][3] == "SELL":
                    if (company_data['last_price']<= RENKO[company_data['instrument_token']][1] - ohlc_final_1min.iloc[-1, 7]):
                        RENKO[company_data['instrument_token']][2] = RENKO[company_data['instrument_token']][1] - ohlc_final_1min.iloc[-1, 7]
                        RENKO[company_data['instrument_token']][3] = "SELL"
                        RENKO_temp = pd.DataFrame([RENKO[x]], columns=["Symbol", "Open", "Close", "Signal", "Position"])
                        RENKO_Final = RENKO_Final.append(RENKO_temp, sort=False)
                        #print(RENKO_Final.tail(3))
                        RENKO[company_data['instrument_token']][1] = RENKO_Final.iloc[-1, 2]
                    elif company_data['last_price'] >= RENKO[company_data['instrument_token']][1] + (RENKO_Final.iloc[-1, 1] - RENKO_Final.iloc[-1, 2]) + ohlc_final_1min.iloc[-1, 7]:
                        RENKO[company_data['instrument_token']][1] = RENKO_Final.iloc[-1, 1]
                        RENKO[company_data['instrument_token']][2] = RENKO_Final.iloc[-1, 1] + ohlc_final_1min.iloc[-1, 7]
                        RENKO[company_data['instrument_token']][3] = "BUY"
                        RENKO_temp = pd.DataFrame([RENKO[x]], columns=["Symbol", "Open", "Close", "Signal", "Position"])
                        RENKO_Final = RENKO_Final.append(RENKO_temp, sort=False)
                        #print(RENKO_Final.tail(3))
                        RENKO[company_data['instrument_token']][1] = RENKO_Final.iloc[-1, 2]

    except Exception as e:
            traceback.print_exc()


def calcpsoitions(Token, quantity, Last_price, Signal):
    global profit_Final, profit_temp, profit, overall_profit
    profit[Token][0] = trd_portfolio[Token]
    if Signal == "SELL":
        profit[Token][1] = Last_price
    elif Signal == "BUY":
        profit[Token][2] = Last_price
    if profit[Token][1]!=0 and profit[Token][2]!=0:
        BuyBrokerage = min((((profit[Token][2])*quantity)*(.01/100)),20)
        SellBrokerage = min((((profit[Token][1]) * quantity) * (.01 / 100)), 20)
        STT = ((profit[Token][2])*quantity) * (.025/100)
        TNXChrgs = ((profit[Token][2])*quantity) * (.00325/100)
        GST = (STT + TNXChrgs) * (18/100)
        SEBIChrgs = ((profit[Token][2] + profit[Token][1]) * quantity) * (.0000015/100)
        StampDuty = ((profit[Token][2] + profit[Token][1]) * quantity) * (.003/100)
        profit[Token][3] = ((profit[Token][1] - profit[Token][2]) * quantity) - (BuyBrokerage + SellBrokerage + STT + TNXChrgs + GST + SEBIChrgs + StampDuty)
        profit_temp = pd.DataFrame([profit[x]], columns=["Symbol", "SELL Price", "BUY Price", "Profit"])
        profit_Final = profit_Final.append(profit_temp, sort=False)
        overall_profit += profit_Final.iloc[-1, 3]
        profit[Token][1] = 0
        profit[Token][2] = 0
        print(profit_Final.tail(3))
        print(overall_profit)

def on_ticks(ws, ticks):  # retrive continius ticks in JSON format
    global ohlc_final_1min, RENKO_Final, quantity
    try:
        for company_data in ticks:
            calculate_ohlc_one_minute(company_data);
            if len(RENKO_Final) > 0:
                if ohlc_final_1min.iloc[-1,9]!=0:
                    if RENKO_Final.iloc[-1,3] == "SELL" and RENKO_Final.iloc[-1,1] < ohlc_final_1min.iloc[-1,9] and RENKO_Final.iloc[-1,2] < ohlc_final_1min.iloc[-1,9] and RENKO[company_data['instrument_token']][4]!= "SHORT":
                        print('Sell at ', str(company_data['last_price']))
                        calcpsoitions(company_data['instrument_token'], quantity, company_data['last_price'], "SELL")
                        if RENKO[company_data['instrument_token']][4] != "None":
                            print('Sell at ', str(company_data['last_price']))
                            calcpsoitions(company_data['instrument_token'], quantity, company_data['last_price'],"SELL")
                        RENKO[company_data['instrument_token']][4] = "SHORT"
                    elif RENKO_Final.iloc[-1,3] == "BUY" and RENKO_Final.iloc[-1,1] > ohlc_final_1min.iloc[-1,9] and RENKO_Final.iloc[-1,2] > ohlc_final_1min.iloc[-1,9] and RENKO[company_data['instrument_token']][4]!="LONG":
                        print('Buy at ', str(company_data['last_price']))
                        calcpsoitions(company_data['instrument_token'], quantity, company_data['last_price'], "BUY")
                        if RENKO[company_data['instrument_token']][4] != "None":
                            print('Buy at ', str(company_data['last_price']))
                            calcpsoitions(company_data['instrument_token'], quantity, company_data['last_price'], "BUY")
                        RENKO[company_data['instrument_token']][4] = "LONG"
    except Exception as e:
        traceback.print_exc()

def on_connect(ws, response):
    ws.subscribe([x for x in trd_portfolio])
    ws.set_mode(ws.MODE_FULL, [x for x in trd_portfolio])

# Assign the callbacks.
kws.on_ticks = on_ticks
kws.on_connect = on_connect

kws.connect()
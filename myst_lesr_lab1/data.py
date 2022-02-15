# -*- coding: utf-8 -*-
"""
Created on Mon Feb 14 17:33:37 2022

@author: luis_
"""
from os import listdir, path
from os.path import isfile, join
import pandas_datareader.data as web
import yfinance as yf
import pandas as pd
import numpy as np

def conversion_cash(df): 
    # Cambiamos tickers a cash (KOFL.MX, KOFUBL.MX, USD.MXN, BSMXB.MX, NMKA.MX ) quitamos tambien MXN para poder usar en funcion de descarga de precios
    deltickers = ['MXN.MX','KOFL.MX', 'KOFUBL.MX', 'USD.MX', 'BSMXB.MX', 'NMKA.MX','NEMAKA.MX']
    df = df[~df['Ticker'].isin(deltickers)]
    return df

def price_adj_close(tickers, start_date=None, end_date=None, freq=None):
    closes = pd.DataFrame(columns=tickers, index=web.YahooDailyReader(tickers[0], start=start_date, end=end_date
                                                                      , interval=freq).read().index)
    for i in tickers:
        df = web.YahooDailyReader(symbols=i, start=start_date, end=end_date, interval=freq).read()
        closes[i] = df['Adj Close']
    closes.index_name = 'Date'
    closes = closes.sort_index()
    return closes

def df_of_data(files):
    data_files = {}
    for i in files:
        data = pd.read_csv("files/" + i + ".csv", skiprows=2, header=0)
        data['Ticker'] = [i.replace("*","") for i in data["Ticker"]]
        data['Ticker'] = data['Ticker'] + '.MX' 
        data['Date'] = i
        data['Date'] = [i.replace('NAFTRAC_','') for i in data['Date']]
        data['Date'] = [i.replace('.csv','') for i in data['Date']]
        data['Peso (%)'] = [i/100 for i in data["Peso (%)"]]
        data_files[i] = data

    naftrac = pd.concat(data_files)
    naftrac.dropna(subset = ["Nombre"], inplace=True)
    naftrac['Ticker'] = naftrac['Ticker'].replace('MEXCHEM.MX', 'ORBIA.MX')
    naftrac['Ticker'] = naftrac['Ticker'].replace('LIVEPOLC.1.MX', 'LIVEPOLC-1.MX')
    naftrac['Ticker'] = naftrac['Ticker'].replace('SITESB.1.MX', 'SITESB-1.MX')
    naftrac['Ticker'] = naftrac['Ticker'].replace('GFREGIOO.MX', 'RA.MX')
    naftrac['Date'] = pd.to_datetime(naftrac['Date'],format='%Y%m%d')
    naftrac = naftrac.set_index("Date")
    return naftrac

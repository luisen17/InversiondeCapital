# -*- coding: utf-8 -*-
"""
Created on Mon Feb 14 17:33:41 2022

@author: luis_
"""

from os import listdir, path
from data import *
from functions import *
from os.path import isfile, join
import datetime
import pandas as pd
import numpy as np


#%%
abspath = path.abspath("files/")
files = [f[8:-4] for f in listdir(abspath) if isfile(join(abspath, f))]
files = ["NAFTRAC_" + i.strftime("%Y%m%d") for i in sorted(pd.to_datetime(files))]
naftrac_complete = df_of_data(files)
dates = get_dates(files)
naftrac_complete = conversion_cash(naftrac_complete) 
naftrac_stats = naftrac_complete[['Ticker', 'Peso (%)']]
all_tickers = list(naftrac_stats['Ticker'].unique())

#%%
closes = price_adj_close(all_tickers, dates[0],dates[-1], freq="d")
monthly_closes = closes[closes.index.isin(dates)]

#%%
naftrac_stats = df_act_prices(naftrac_stats, monthly_closes, dates)



#%% 
comision = 0.00125 
capital = 1000000
portafolio_pasivo_prepandemia = inv_pasiva_posicion(naftrac_stats, dates[0], capital, comision)
lapso_prepandemia = dates[0:25]
df_pasiva_a = pasive_invstmnt_rend(portafolio_pasivo_prepandemia, lapso_prepandemia, capital, naftrac_stats)
portafolio_pasivo_enpandemia = inv_pasiva_posicion(naftrac_stats, dates[25], capital, comision)
lapso_enpandemia = dates[25:]
df_pasiva_b = pasive_invstmnt_rend(portafolio_pasivo_enpandemia, lapso_enpandemia, capital, naftrac_stats)

#%% 
comision = 0.00125 
capital = 1000000
portafolio_activo = inv_pasiva_posicion(naftrac_stats, dates[0], capital, comision)
naftrac_stats_active = limpia_activos(naftrac_stats, portafolio_activo)
trading_activo = trading_bot(naftrac_stats_active)
trading_activo = dec_filter(trading_activo)




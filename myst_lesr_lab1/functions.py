# -*- coding: utf-8 -*-
"""
Created on Mon Feb 14 17:33:40 2022

@author: luis_
"""
import datetime
import numpy as np
import pandas as pd

def trading_bot(naftrac_stats_active):
    df_active = naftrac_stats_active
    df_active = df_active.sort_values(by=['Ticker','Date'], ascending=True)
    df_active['Change'] = df_active['Close'].pct_change()
    df_active.loc[df_active['Date'] == df_active['Date'][0], ['Change']] = 'nan'
    df_active = df_active[df_active['Change'] !=  'nan']
    a= 0.05
    df_active['buy'] = 0
    df_active['buy'] = np.where(df_active['Change']>= a, 1,0)
    b= -0.05
    df_active['sell'] = 0
    df_active['sell'] = np.where(df_active['Change']<= b, 1,0)
    del df_active['Peso (%)']
    return df_active

def df_act_prices(naftrac_stats, monthly_closes, dates):
    mezcla = {}
    for date in dates:
        mezcla[date] = naftrac_stats[naftrac_stats.index == date].reset_index().set_index('Ticker').T

    for date in dates:
        mezcla[date].loc['Close'] = 0
        for ticker in monthly_closes.columns:
            mezcla[date].loc['Close'][ticker] = monthly_closes.loc[date][ticker]
            mezcla[date].columns.sort_values()

    mezcla_lt = [v for k, v in mezcla.items()]
    final = pd.concat(mezcla_lt, axis=1)
    final = final.T
    final = final.reset_index()
    
    return final


def inv_pasiva_posicion(df_stats, date, capital, comision):
    Pesos_df = df_stats.loc[df_stats['Date'] == date]
    Pesos_df['Acciones'] = np.floor((capital*Pesos_df['Peso (%)'])/Pesos_df['Close'])
    Pesos_df['$ Total'] = Pesos_df['Acciones']*Pesos_df['Close']
    Pesos_df['Comisión'] = Pesos_df['$ Total']*comision
    return Pesos_df


def pasive_invstmnt_rend(portafolio_pasivo, lapso, capital, naftrac_stats):
    total_comision = portafolio_pasivo['Comisión'].sum()
    cash = (1 - portafolio_pasivo['Peso (%)'].sum())*capital
    n_s_pandemia = naftrac_stats.loc[naftrac_stats['Date'].isin(lapso)]
    del n_s_pandemia['Peso (%)']
    prueba = pd.merge(portafolio_pasivo,n_s_pandemia,on='Ticker' ,how='outer')
    del prueba['Date_x']
    del prueba['Peso (%)']
    del prueba['Close_x']
    del prueba['$ Total']
    del prueba['Comisión']
    prueba['Valor Posición'] = prueba['Acciones']*prueba['Close_y']
    pd.to_numeric(prueba['Valor Posición'])
    prueba = prueba.dropna()
    prueba = prueba.set_index("Date_y")
    prueba = prueba.sort_index(ascending=True)
    prueba = prueba.resample('D').sum()
    prueba = prueba.loc[~(prueba==0).all(axis=1)]
    prueba['capital'] = prueba['Valor Posición'] + cash - total_comision 
    del prueba['Ticker']
    del prueba['Acciones']
    del prueba['Close_y']
    del prueba['Valor Posición']
    ini = {'Date_y': [portafolio_pasivo.iloc[0,1]-datetime.timedelta(1)], 'capital': [capital]}
    ini = pd.DataFrame(ini)
    ini = ini.set_index('Date_y')
    prueba = ini.append(prueba)
    prueba['rend'] = prueba['capital']/prueba['capital'].shift(1)-1
    prueba['rend'] = prueba['rend'].fillna(0)
    prueba['rend_acum'] = prueba['rend']
    for i in range(len(prueba)):
        prueba['rend_acum'][i] = (prueba['capital'][i]/prueba['capital'][0])-1
    prueba.index.names = ['timestamp']
    return prueba

def limpia_activos(naftrac_stats, portafolio_activo):
    naftrac_stats_active = naftrac_stats
    lista_tickers_activo = portafolio_activo['Ticker'].unique()
    lista_tickers_activo = list(lista_tickers_activo) 
    naftrac_stats_active = naftrac_stats_active[naftrac_stats_active['Ticker'].isin(lista_tickers_activo)]
    return naftrac_stats_active

def dec_filter(trading_activo):
    filter = trading_activo
    filter['filter'] = 0
    filter.loc[filter['buy'] == 1, ['filter']] = 1
    filter.loc[filter['sell'] == 1, ['filter']] = 1
    filter = filter[filter['filter'] != 0]
    del filter['filter']
    filter = filter.sort_values(by=['Date'], ascending=True)
    return filter

def mad(df_pasiva_a,df_pasiva_b,df_activa):
    mad = pd.DataFrame({
            'descripción': ['Rendimiento Promedio Mensual','Rendimiento mensual acumulado','Sharpe Ratio 	'],
            'inv_activa': ['0','0','0'],
            'inv_pasiva_a': [df_pasiva_a['rend'].mean()*12,df_pasiva_a['rend_acum'].mean()*12,(df_pasiva_a['rend'].mean()*12-0.0429)/df_pasiva_a['rend'].std()],
            'inv_pasiva_b': [df_pasiva_b['rend'].mean()*12,df_pasiva_b['rend_acum'].mean()*12,(df_pasiva_b['rend'].mean()*12-0.0429)/df_pasiva_b['rend'].std()],
            
        
        },index=['rend_m', 'rend_c', 'sharpe'])
    df_activa =0

    return mad

def get_dates(list_of_files):
    dates = [i.strftime('%Y-%m-%d') for i in sorted([pd.to_datetime(i[8:]).date() for i in list_of_files])]
    return dates

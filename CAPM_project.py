# importing libraries
import pandas as pd
import streamlit as st
import yfinance as yf
import pandas_datareader.data as web
import datetime
import capm_functions
import numpy as np

st.set_page_config(page_title='CAPM',
     page_icon='Chart_with_upwards_trend',
     layout='wide')
st.title('Capital Asset Pricing Model') 

# User Input

col1,col2 = st.columns([1,1])
with col1:
    stocks_list = st.multiselect('Choose 4 stocks',('TSLA','APPL','NFLX','MSFT','MGM','AMZN','NVDA','GOOGL'),['TSLA','APPL','AMZN','GOOGL'])
with col2:
    year=st.number_input('Number of years:',1,10)

# downloading data for S&P500
try:
    
    end = datetime.date.today() 
    start = datetime.date(datetime.date.today().year-year,datetime.date.today().month,datetime.date.today().day)

    SP500 = web.DataReader(['SP500'],'fred',start,end)
    print(SP500.head())
    print(SP500.tail())

    # downloading data for Stock_list

    stocks_df = pd.DataFrame()

    for stock in stocks_list:
        data = yf.download(stock,period=f'{year}y')
        stocks_df[f'{stock}'] = data['Close']
    print(stocks_df.head())

    # merging or joining the SP500,stocks_df based on date column

    stocks_df.reset_index(inplace=True)
    SP500.reset_index(inplace = True)
    SP500.columns = ['Date','SP500']
    print(stocks_df.dtypes)
    print(SP500.dtypes)
    stocks_df['Date'] = stocks_df['Date'].apply(lambda x :str(x)[:10])
    stocks_df['Date'] = pd.to_datetime(stocks_df['Date'])
    stocks_df = pd.merge(stocks_df,SP500, on = 'Date',how = 'inner')
    print(stocks_df)
    col1,col2 = st.columns([1,1]) 
    with col1:
        st.markdown("### Dataframe Head")
        st.dataframe(stocks_df.head(),use_container_width= True)

    with col2:
        st.markdown("### Dataframe Tail")
        st.dataframe(stocks_df.tail(),use_container_width= True)

    # calling interactive_pltly function
    col1,col2 = st.columns([1,1])
    with col1:
        st.markdown('### Price of all stocks')
        st.plotly_chart(capm_functions.interactive_plot(stocks_df))
    with col2:
        print(capm_functions.normalize(stocks_df))
        st.markdown('### Price of noramlized stocks')
        st.plotly_chart(capm_functions.interactive_plot((capm_functions.normalize(stocks_df))))

    stocks_daily_return = capm_functions.daily_return(stocks_df)
    print(stocks_daily_return.head())

    beta = {}
    alpha = {}

    for i in stocks_daily_return.columns:
        if i != 'Date'and i != 'SP500':
          b,a = capm_functions.calculate_beta(stocks_daily_return, i)
            
          beta[i] = b
          alpha[i] = a

    print(beta,alpha)

    # calcularing CAPM

    beta_df = pd.DataFrame(columns= ['Stock','Beta Value'])
    beta_df['Stock'] = beta.keys() 
    beta_df['Beta Value'] = [str(round(i,2))for i in beta.values()]

    with col1:
        st.markdown('### Calculated Beta Value')
        st.dataframe(beta_df,use_container_width= True)

    # calculation of return(Part of CAPM)
    rf = 0
    rm = stocks_daily_return['SP500'].mean()*252

    return_df = pd.DataFrame()                                   # empty dataset for storing value
    return_value = []                                          #empty list for storing calculated return value
    for stock, value in beta.items():
        return_value.append(str(round(rf+(value*(rm-rf )),2)))                # formula for CAPM
    return_df['Stock'] = stocks_list
    return_df['Return Value']   = return_value

    with col2:
        st.markdown('### Calculated return using CAPM')
        st.dataframe(return_df, use_container_width= True)
except:
    st.write('please select valid input')        
     
 
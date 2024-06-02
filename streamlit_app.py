import streamlit as st
from Trading_main import Futures_bot
import time  # to simulate a real time data, time loop
import extra_streamlit_components as stx
import Sharing_data
import time
import os

start_time = time.time()

st.set_page_config(
    page_title="Crypto trading",
    page_icon="✅",
    layout="wide",
)

folder_path = 'data/'

def app_init():
    # Initialize session_state if it doesn't exist
    if 'display_data' not in st.session_state:
        st.session_state['display_data'] = False
    if 'crypto_list' not in st.session_state:
        st.session_state['crypto_list'] = []
    # Loop through the .data folder
    for filename in os.listdir(folder_path):
        if filename.endswith('.json'):
            file_name_without_ext = filename[:-5]  # Remove the .json extension
            # Add the file name and init variable to the session state list
            st.session_state['crypto_list'].append({'symbol': file_name_without_ext, 'init': False})
    if 'tabs' not in st.session_state:
        st.session_state["tabs"] = [
            stx.TabBarItemData(id="Resume", title="Resume", description=""),
            stx.TabBarItemData(id="Help", title="Help", description="")]
        for crypto in st.session_state.crypto_list:
            new_tab = stx.TabBarItemData(id=f"{crypto['symbol']}", title=f"{crypto['symbol']}", description="")
            st.session_state["tabs"].append(new_tab)
        
        #st.rerun()

def render_trace(crypto):
    df = Sharing_data.read_json(filename=folder_path + crypto['symbol']+'.json')

    if f"{crypto['symbol']}" not in st.session_state:
        st.session_state[f"{crypto['symbol']}"] = 'init done'
        st.session_state[f"{crypto['symbol']}_line_chart_price"] = st.line_chart(
           df, x='timestamp', y='close', color=["#FF0000"]  # Optional
        )
        st.session_state[f"{crypto['symbol']}_line_chart_macd"] = st.line_chart(
           df, x='timestamp', y=['MACD', 'MACDs'], color=["#FF0000", "#0000FF"]  # Optional
        )
        st.session_state[f"{crypto['symbol']}_line_chart_df"] = st.dataframe(df)
    else:
        st.session_state[f"{crypto['symbol']}_line_chart_price"].line_chart(
           df, x='timestamp', y='close', color=["#FF0000"]  # Optional
        )
        st.session_state[f"{crypto['symbol']}_line_chart_macd"].line_chart(
           df, x='timestamp', y=['MACD', 'MACDs'], color=["#FF0000", "#0000FF"]  # Optional
        )
        st.session_state[f"{crypto['symbol']}_line_chart_df"].dataframe(df)

# This is the title of the app
st.title('Crypto trading App')

# layout and param
app_init()


tabs = stx.tab_bar(st.session_state["tabs"], default="Resume")

#Sharing_data.append_to_file(f"Streamlit app init time execution {time.time() - start_time}")
#print(f"Streamlit app init time execution {time.time() - start_time}")

while True:

    if tabs =='Resume':
        if st.session_state.display_data:
            Sharing_data.read_and_display_file()
            st.session_state.display_data = False
    else:
        st.session_state.display_data = True

    for crypto in st.session_state.crypto_list:
        if tabs ==crypto['symbol']:
            render_trace(crypto)


    time.sleep(1)

   

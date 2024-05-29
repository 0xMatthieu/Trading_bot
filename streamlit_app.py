import streamlit as st
from Trading_main import Futures_bot
import time  # to simulate a real time data, time loop
import extra_streamlit_components as stx
import Trading_tools
import time

start_time = time.time()

st.set_page_config(
    page_title="Crypto trading",
    page_icon="✅",
    layout="wide",
)

def app_init():
    # Initialize session_state if it doesn't exist
    if 'futures_bot' not in st.session_state:
        st.session_state['futures_bot'] = Futures_bot()
    if 'display_data' not in st.session_state:
        Trading_tools.erase_file_data()
        st.session_state['display_data'] = False
    if 'tabs' not in st.session_state:
        st.session_state["tabs"] = [
            stx.TabBarItemData(id="Resume", title="Resume", description=""),
            stx.TabBarItemData(id="Help", title="Help", description="")]
        for crypto in st.session_state.futures_bot.crypto:
            new_tab = stx.TabBarItemData(id=f'{crypto.symbol_spot}', title=f'{crypto.symbol_spot}', description="")
            #new_tab = st.text_input("Crypto symbol spot", f'{crypto.symbol_spot}')
            st.session_state["tabs"].append(new_tab)
        #st.session_state["tabs"] = ['Resume']
        #st.session_state["tabs"].append('Help')
        
        #st.rerun()

def run_algo(futures_bot):
    futures_bot.run_main()

def render_trace(crypto):
    if crypto.init_render == False:
        crypto.init_render = True
        crypto.line_chart_price = st.line_chart(
           crypto.df, x='timestamp', y='close', color=["#FF0000"]  # Optional
        )
        crypto.line_chart_macd = st.line_chart(
           crypto.df, x='timestamp', y=['MACD', 'Signal'], color=["#FF0000", "#0000FF"]  # Optional
        )
        crypto.line_chart_df = st.dataframe(crypto.df)
    else:
        crypto.line_chart_price.line_chart(
           crypto.df, x='timestamp', y='close', color=["#FF0000"]  # Optional
        )
        crypto.line_chart_macd.line_chart(
           crypto.df, x='timestamp', y=['MACD', 'Signal'], color=["#FF0000", "#0000FF"]  # Optional
        )
        crypto.line_chart_df.dataframe(crypto.df)

# This is the title of the app
st.title('Crypto trading App')

# layout and param
app_init()


tabs = stx.tab_bar(st.session_state["tabs"], default="Resume")

Trading_tools.append_to_file(f"Streamlit app init time execution {time.time() - start_time}")
print(f"Streamlit app init time execution {time.time() - start_time}")

while True:
    #run functions
    run_algo(st.session_state.futures_bot)

    if tabs =='Resume':
        if st.session_state.display_data:
            Trading_tools.read_and_display_file()
            st.session_state.display_data = False
    else:
        st.session_state.display_data = True

    for crypto in st.session_state.futures_bot.crypto:
        if tabs ==crypto.symbol_spot:
            render_trace(crypto)


    time.sleep(1)

   

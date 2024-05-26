import streamlit as st
from Trading_main import Futures_bot
import time  # to simulate a real time data, time loop
import extra_streamlit_components as stx

st.set_page_config(
    page_title="Crypto trading",
    page_icon="✅",
    layout="wide",
)

# Function to erase content and start with a fresh new file
def erase_file_data(file_path="data.txt"):
    with open(file_path, 'w') as file:
        # Opening the file in write mode will truncate the file
        pass

# Function to append a string input to a text file if the input is not None
def append_to_file(input_string, file_path="data.txt"):
    if input_string:
        with open(file_path, "a") as file:
            file.write(input_string + "\n")

# Function to read the file and write content using st.write, one line per sentence
def read_and_display_file(file_path="data.txt"):
    try:
        with open(file_path, "r") as file:
            lines = file.readlines()
            for line in lines:
                st.write(line.strip())
    except FileNotFoundError:
        st.write("File not found. Please add some content first.")

def app_init():
    # Initialize session_state if it doesn't exist
    if 'futures_bot' not in st.session_state:
        st.session_state['futures_bot'] = Futures_bot()
    if 'display_data' not in st.session_state:
        erase_file_data()
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
        
        st.rerun()

def run_algo(futures_bot):
    futures_bot.run_main()

def render_trace(df):
    st.line_chart(
       df, x='timestamp', y='close', color=["#FF0000"]  # Optional
    )
    st.line_chart(
       df, x='timestamp', y=['MACD', 'Signal'], color=["#FF0000", "#0000FF"]  # Optional
    )

# This is the title of the app
st.title('Crypto trading App')

# layout and param
app_init()



#tabs = st.tabs(st.session_state.tabs)
tabs = stx.tab_bar(st.session_state["tabs"], default="Resume")

while True:
    #run functions
    run_algo(st.session_state.futures_bot)

    if tabs =='Resume':
        if st.session_state.display_data:
            read_and_display_file()
            st.session_state.display_data = False
    else:
        st.session_state.display_data = True

    for crypto in st.session_state.futures_bot.crypto:
        if crypto.print is not None:
            append_to_file(crypto.print)
            st.session_state.display_data = True
        if tabs ==crypto.symbol_spot:
            render_trace(crypto.df)

    time.sleep(1)

   

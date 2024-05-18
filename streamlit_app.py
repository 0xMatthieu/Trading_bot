import streamlit as st
from Kucoin_trade import Kucoin


def app_init():
    # Initialize session_state if it doesn't exist
    if 'kucoin' not in st.session_state:
        st.session_state['kucoin'] = Kucoin()


# This is the title of the app
st.title('Crypto trading App')

# layout and param
app_init()




   

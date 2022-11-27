# Crypto_arbitrage_bot

how to start
run python My_discord.py

# what should it do ?

Goal is to provide an arbitrage bot on predefined CEX (centralized exchange). The software implements an abstraction layer to separate logic from IO (in this case requests to CEX)
There is 3 different functions executed:
- a discord bot to implement a kind of remote session. Mainly used to get notified for each events, but could be used to also interact with the bot
- an abitrage function which has 2 purposes (depending on the field "job")
  - the first one is to use REST API to fetch all crypto prices and try to find arbitrage opportunity. The REST API rate is too slow to execute all trades (2s refreshing rate). Instead the function fill a list (a JSON file) with all opportunities found
  - the second one opens a websocket to subscribe to all pairs listed in the JSON file, looks over the list and perform arbitrage trade if an opportunity exists. Web socket refresh rate is faster (<150 ms)
  
 # general information
  - CEX implements around 1200 crypto trading pairs but websocket API allows only 100 requests https://docs.kucoin.com/#request-rate-limit 
  
  ![image](https://user-images.githubusercontent.com/111059326/186150000-cbbfaf66-9fcf-4032-8096-313703da779c.png)



# current situation

problem is: how to run asychrone or in parallel the software to speed up the whole process
Kucoin_trade.websocket_get_tickers_and_account_balance(0) use asyncio by default, it comes from an asbraction library (python-kucoin) which implements a websocket reading stream with asyncio
The fact that a mandatory part implements asyncio creates some issues
 - pandas is not asynchone by design
 - using thread in python is concurrent and not parallel, means that it slow the websocket read function anf lead after few seconds to lost the connection with the stream (I didn't find the root cause)
 - using concurrent futures seems to not start the web socket read while arbitrage function is working quite well 

Currently the main code is in My_discord.py in discord_arbitrage_run(). 

A solution might be to use asyncio to run asyn tasks and run_in_executor for arbitrage (which includes pandas) but after some tests it seems that the websocket stream is never awaited. It is fine cause I would like to read the stream as fast as possible but also run the run arbitrage function with job "do_arbitrage" to perform arbitrage and also update_list to use the REST api to find new opportunities.

# update 11/09/2022

New software with concurrent.futures
Problems to fix:
- share settings_kucoin data between files
- If REST API used, lead to an error
  Comment to avoid

    print('start thread kucoin list')
    executor.submit(
      update_list_arbitrage
    )


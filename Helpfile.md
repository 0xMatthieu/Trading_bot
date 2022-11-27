

python -i My_discord.py

scp -r /Users/matthieu/Documents/Python/Binance/Crypto_arbitrage_bot matthieu@192.168.1.19:/home/matthieu/python/Binance/

python -m pip install discord
python -m pip install python-kucoin
python -m pip install python-dotenv
python -m pip install tqdm
python -m pip install nest-asyncio

lxterminal -e "cd /home/matthieu/python/Binance/220605_Arbitrage/ ; python Main_Arbitrage.py"

source : https://medium.com/geekculture/automated-triangular-arbitrage-of-cryptos-in-4-steps-a678f7b01ce7

220605  - first version

220702	- add kucoin exchange

git help
git rm .env --cached
git commit -a -m "Stopped tracking .env File"
git push -u origin main
git filter-branch --index-filter "git rm -rf --cached --ignore-unmatch .env"  --> push --force ensuite https://stackoverflow.com/questions/54750229/remove-virtualenv-files-from-all-previous-commits-after-removing-from-repository
git pull --allow-unrelated-histories origin main  forcer le pull d un code local
git rev-parse --abbrev-ref HEAD

https://gist.github.com/KedrikG/f7b955dc371b1204ec76ce862e2dcd2e token et sublime text
https://docs.github.com/en/get-started/importing-your-projects-to-github/importing-source-code-to-github/adding-locally-hosted-code-to-github
https://github.com/Kunena/Kunena-Forum/wiki/Create-a-new-branch-with-git-and-manage-branches

scp -r /Users/matthieu/Documents/Python/Binance/Binance 192.168.1.19:/home/matthieu/python/


27/07/2021
money_available a ete remplace par crypto et fiat
log_money_available devient juste money_available

enlever commentaire acces lecture asset dans Binance_trade

449, 147, 63 = 
313, 152, 17
302, 0, 204

supertrend
changement get historical

#add stop loss
        #order = sb.client.order_market_buy(symbol=Currency.Currency, quantity=quantity)
        """
        order = sb.client.futures_create_order(
            symbol='ADAUSDT', side='BUY', type='MARKET', quantity=10, isolated=True)
        client.futures_create_order(
            symbol='ETHUSDT', side=SIDE_SELL, type='STOP_MARKET', quantity=quantity, positionSide=positionSide, stopPrice=stopLoss, timeInForce=TIME_IN_FORCE_GTC)
        client.futures_create_order(
            symbol='ETHUSDT', side=SIDE_SELL, type=FUTURE_ORDER_TYPE_TAKE_PROFIT_MARKET, quantity=quantity, positionSide=positionSide, stopPrice=takeProfit, timeInForce=TIME_IN_FORCE_GTC)
            sb.client._delete('openOrders', True, data={'symbol': 'ADAUSDT'})
        """

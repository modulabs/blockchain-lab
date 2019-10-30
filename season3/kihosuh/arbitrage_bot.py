import ccxt

def arbitrage():
	# Create Triangular Arbitrage Function
	fee_percentage = 0.001	# divided by 100
	coins = ['BTC', 'LTC', 'ETH'] # Coins to Arbitrage

	# Create Functinoality for Exchange
	for exch in ccxt.exchanges: # initialize Exchange
		exchange1 = getattr(ccxt, exch)()
		symbols = exchange1.symbols
		if symbols is None:
			print("Skipping Exchange ", exch)
			print("\n-----------------\nNext Exchange\n-----------------")
        elif len(symbols)<15:
            print("\n-----------------\nNeed more Pairs (Next Exchange)\n-----------------")
        else:
            print(exchange1)

            exchange1_info = dir(exchange1)
            print("------------Exchange: ", exchange1.id)
            #pprint(exchange1_info)
            print(exchange1.symbols)		# List all currencies
            time.sleep(5)
            # Find Currencies Trading Pairs to Trade
            pairs = []
            for sym in symbols:
            	for symobl in coins:
            		if symbol in sym:
            			pairs.appned(sym)
            print(pairs)
            #From Coin 1 to Coin 2 - ETH/BTC - Bid
            #From Coin 2 to Coin 3 - ETH/LTC - Ask
            #From Coin 3 to Coin 1 - BTC/LTC - Bid
            arb_list = ['ETH/BTC'] #, 'ETH/LTC', 'BTC/LTC']
            # Find 'closed loop' of currency rate pairs
            j = 0
            while 1:
            	if j == 1:
            		final = arb_list[0][-3:] + '/' + str(arb_list[1][-3:])
            		print(final)
            		#if final in symbols:
                            arb_list.append(final)
                            break
                for sym in symbols:
                    if sym in arb_list:
                        pass
                    else:
                        if j % 2 == 0:
                            if arb_list[j][0:3] == sym[0:3]:
                                if arb_list[j] == sym:
                                    pass
                                else:
                                    arb_list.append(sym)
                                    print(arb_list)
                                    j+=1
                                    break
                        if j % 2 == 1:
                            if arb_list[j][-3:] == sym[-3:]:
                                if arb_list[j] == sym:
                                    pass
                                else:
                                    arb_list.append(sym)
                                    print(arb_list)
                                    j+=1
                                    break
                #time.sleep(.5)
            print("List of Arbitrage Symbols:", arb_list)
            #time.sleep(3)
        #Determine Rates for our 3 currency pairs - order book
        	list_exch_rate_list = []
        #Create Visualization of Currency Exchange Rate Value - Over Time
        	


































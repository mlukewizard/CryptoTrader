#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#This is the script which you actually run, the rest of the files are either
#function or object declaration files.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from CryptoTrader.tradingStrategy import *

#This line says 'I'm going to make an object of type LukesFirstStrategy' and
#I'm going to name that strategy 'strategy1'
strategy1 = LukesFirstStrategy()

#This line produces a graph showing how much money you would have made if
#you had traded on this strategy.
strategy1.backtest('Training')
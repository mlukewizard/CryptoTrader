#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#This file is where I declare the strategy objects, as strategy object is
#a thing which can tell you what it would buy and sell on any given day and
#importantly it can also test itself.

#~~~Features of a strategy object:~~~
#-->evaluateStrategyAtCurrentTime - when this function is run, the returned
#   value must be a list of 4 numbers indicating the requested CHANGE in
#   holdings of each of a set of assets at the particular date specified.
#   The set of assets depends on whether the dataSetType is set to training
#   or crypto, and your function should return different values accordingly.
#   Getting a good one of these functions is the big challenge.
#-->backtest - when this function is run, the strategy is to be evaluated.
#   You probably wont need to change this. It basically just runs through
#   a set of dates and trades upon what evaluateStrategyAtCurrentTime tells
#   it to do. And then produces a graph at the end for you to see how it did.
#
#Lastly you should know what the two datasets are. I'm going to write it here
#so that you dont need to look into apiWrapper.py (because its pretty grim).
#The Crypto set is simply prices for LTC, ETH and BTC for the last 6 months (I'm
#working on making that longer). The Training set is very important, this is
#the one you will be running most of your tests on and you can optimise your
#training strategy as much as you want on it. It consists of 6 prices, the first
#one is the polish zloty to GBP exchange rate, and the second is the inverse of
#that exchange rate (we need to make sure our algorithms aren't gonna lose us
#money if the market turns downwards). The third is chinese Yuan to GBP and the
#4th is that inverse. The 5th is Stellar Lumens crypto prices, and the 6th is
#that inverse.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from CryptoTrader.handyFunctions import *
from CryptoTrader.apiWrapper import *
#The functions available from apiWrapper are:
#1) getAvailableCurrencies() This was really just my first tester function, this
# is what GDAX offers for trading through their api
#2) getHistoricCryptoPrices(startdate, enddate, timeInterval) This gets you the
#crypto data for between the specified dates - NB you cant get more than 6 months
#atm. NB timeInterval of 84600 is 1 day
#3) getHistoricTrainingPrices(startdate, enddate) This gets you the training data
#There is no time interval because you can only get prices daily
import datetime
import numpy as np
import matplotlib.pyplot as plt

#So this is a 'base' class (object) for a trading strategy, all our other strategies
#should inherit from this. It'll give you the backtest function so you don't need
#to write your own
class TradingStrategy():
    def __init__(self):
        print('This is a placeholder for a function you need to create, and when you do that this one will be ignored, this line should never be run')

    #Tests your strategy
    def backtest(self, dataSetType):
        if dataSetType == 'Training':
            testStartDate = '2017-07-01'
            trainingPrices = getHistoricTrainingPrices(datetime.datetime.strptime(testStartDate, '%Y-%m-%d').date() - datetime.timedelta(days=1), datetime.date.today())
        elif dataSetType == 'Crypto':
            testStartDate = '2017-07-01'
            trainingPrices = getHistoricCryptoPrices(datetime.datetime.strptime(testStartDate, '%Y-%m-%d').date() - datetime.timedelta(days=1), datetime.date.today(), 86400)


        dateRange = dateTimeRange(testStartDate, datetime.date.today())
        profitAndLoss = np.zeros(len(dateRange)) #Defines an array showing you the profit on each day of trading with that strategy
        currentHoldings = np.zeros(trainingPrices.shape[0])
        for i in range(len(dateRange)):
            element = dateRange[i]
            #Queries the strategy for what it would do
            strategyOutput = self.evaluateStrategyAtCurrentTime(element, 'Training')
            #Adds its recommendation to the portfolio holdings
            currentHoldings = currentHoldings + strategyOutput
            #Goes through the holdings and adds up the profit made from holding each asset on this day
            for j in range(len(currentHoldings)):
                profitAndLoss[i] = profitAndLoss[i-1] + currentHoldings[j]*(trainingPrices[j, i] - trainingPrices[j, i-1])
        #plots the results
        plt.plot(dateRange, profitAndLoss)
        plt.show()

    def evaluateStrategyAtCurrentTime(self, time, dataSetType):
        print('This is a placeholder for a function you need to create, and when you do that this one will be ignored, this line should never be run')


#This is my tester strategy, you should study this carefully. It has two functions both of which
#overwrite function in the base class you can see above. The first is an initialiser __init__(self)
#which is run when the object is created (like in line 10 of main.py), and the second is my genius
#insightful trading strategy (lol jk its not very genius).
class LukesFirstStrategy(TradingStrategy):
    # NB. 'self' is a name for the strategy object.
    def __init__(self):
        #Gets the training prices into your object
        self.trainingPrices = getHistoricTrainingPrices('2017-01-01', datetime.date.today())
        # Gets the crypto prices into your object
        self.cryptoPrices = getHistoricCryptoPrices('2017-06-01', datetime.date.today(), 86400)
        #Makes an array of dates, just because it comes in handy
        self.dates = dateTimeRange('2017-06-01', datetime.date.today())
        #Defines a data structure (dictionary) which the strategy can store future trades it intends
        #to make in
        self.futureTrades = {}

    def evaluateStrategyAtCurrentTime(self, thisDaysDate, dataSetType):
        #This changes the numbers used in the evaluation of the strategy, depending on which dataset
        #it's being requested to use
        if dataSetType == 'Training':
            assetPrices = self.trainingPrices
        elif dataSetType == 'Crypto':
            assetPrices = self.cryptoPrices
        #finds todays date in the date array
        todaysIndex = self.dates.index(thisDaysDate)
        #restricts the prices you can use for your strategy, you cant use future prices in your strategy
        #because that would be cheating!
        useablePrices = assetPrices[:, 0:todaysIndex]

        #Checks if the strategy has any planned trades for today
        if thisDaysDate in self.futureTrades:
            futureCommitments = self.futureTrades[thisDaysDate]
        else:
            futureCommitments = np.zeros(useablePrices.shape[0])

        todaysTrade = np.zeros(useablePrices.shape[0])

        for i in range(len(useablePrices)): #iterates through the different cryptos we're looking at
            commodity = useablePrices[i, :]
            #And this is where my mega advanced algorithm is! It simply says that if the price of the
            #asset went up yesterday and the day before, then I think we should invest!!!
            if commodity[-2] < commodity[-1] and commodity[-3] < commodity[-2]:
                todaysTrade[i] = 10/commodity[-1] #Buy 10 dollars worth of that asset
        self.futureTrades[thisDaysDate + datetime.timedelta(days=3)] = -todaysTrade #Sell 10 dollars of that asset again in 3 days time
        return todaysTrade + futureCommitments #returns an array detailing the request change in holdings


class MattsFirstStrategy(TradingStrategy):
    def __init__(self):
        self.trainingPrices = getHistoricTrainingPrices('2017-06-01', datetime.date.today())
        self.cryptoPrices = getHistoricCryptoPrices('2017-06-01', datetime.date.today(), 86400)
        self.dates = dateTimeRange('2017-06-01', datetime.date.today())
        self.futureTrades = {}

    def evaluateStrategyAtCurrentTime(self, thisDaysDate, dataSetType):
        if dataSetType == 'Training':
            assetPrices = self.trainingPrices
        elif dataSetType == 'Crypto':
            assetPrices = self.cryptoPrices
        todaysIndex = self.dates.index(thisDaysDate)
        useablePrices = assetPrices[:, 0:todaysIndex]

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        #Your genius strategy goes here!
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        return
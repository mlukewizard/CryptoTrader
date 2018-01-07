import requests
import json
import datetime
import time
import numpy as np
from CryptoTrader.handyFunctions import *
import os
import csv

def getAvailableCurrencies():
    currencyList = []
    apiData = requests.request('GET', 'https://api.gdax.com/products', params=None)
    apiData = json.loads(apiData.content.decode("utf-8"))
    for element in apiData:
        currencyList.append(element['id'])
    return currencyList

def getHistoricCryptoPrices(startdate, enddate, timeInterval):
    dateList = dateTimeRange(startdate, enddate)
    if not isinstance(startdate, str):
        startdate = datetime.datetime.strftime(startdate, '%Y-%m-%d')
    if not isinstance(enddate, str):
        enddate = datetime.datetime.strftime(enddate, '%Y-%m-%d')
    coins = ['LTC-USD', 'ETH-USD', 'BTC-USD']
    priceList = np.ndarray([len(coins), len(dateList)])
    for i in range(len(coins)):
        productID = coins[i]
        apiData = []
        numTrys = 0
        statusCode = 400
        while statusCode != 200 or len(apiData) != len(dateList):
            numTrys = numTrys + 1
            apiData = requests.request('GET', 'https://api.gdax.com/products/' + productID + '/candles', params={'start':startdate, 'end':enddate, 'granularity':timeInterval})
            statusCode = apiData.status_code
            apiData = json.loads(apiData.content.decode("utf-8"))
            if (statusCode != 200 or len(apiData) != len(dateList)) and numTrys > 4:
                raise Exception('This is luke speaking, your crypto API request has returned an error, error message is: ' + apiData.text)
        for j in range(len(apiData)):
            priceList[i, -j-1] = apiData[j][4] #index 4 is the closing price
    return priceList

def getHistoricTrainingPrices(startdate, enddate):
    if not os.path.exists('./dataFolder'):
        os.mkdir('./dataFolder')
    dateList = dateTimeRange(startdate, enddate)
    if isinstance(startdate, str):
        startdate = datetime.datetime.strptime(startdate, '%Y-%m-%d').date()
    if isinstance(enddate, str):
        enddate = datetime.datetime.strptime(enddate, '%Y-%m-%d').date()
    priceList = np.zeros([6, len(dateList)])
    currencyCodes = ['XUDLBK47', 'XUDLBK89'] #Zloty then Yuan
    for i in range(len(currencyCodes)):
        currency = currencyCodes[i]
        numTrys = 0;
        statusCode = 400
        while statusCode != 200:
            numTrys = numTrys + 1
            apiData = requests.request('GET', 'http://www.quandl.com/api/v3/datasets/BOE/' + currency, params={'api_key':'juGuShBrptwQ-umhLsGy'})
            statusCode = apiData.status_code
            if apiData.status_code != 200 and numTrys > 4:
                raise Exception('This is luke speaking, your training API request has returned an error, error message is: ' + apiData.text)
        apiData = json.loads(apiData.content.decode("utf-8"))
        for element in apiData['dataset']['data']:
            if datetime.datetime.strptime(element[0], '%Y-%m-%d').date() >= startdate and datetime.datetime.strptime(element[0], '%Y-%m-%d').date() <= enddate:
                dateIndex = dateList.index(datetime.datetime.strptime(element[0], '%Y-%m-%d').date())
                priceList[2*i, dateIndex] = element[1]
        for j in range(len(priceList[2*i, :])):
            if priceList[2*i, j] == 0 and j >0:
                priceList[2*i, j] = priceList[2*i, j-1]
        for j in range(len(priceList[2*i, :])):
            if priceList[2*i, -j] == 0:
                priceList[2*i, -j] = priceList[2*i, -j+1]
        priceList[2*i+1, :] = 1/priceList[2*i, :]
    for i in range(len(dateList)):
        element = dateList[i]
        if element != datetime.date.today():
            adjustedDate = element + datetime.timedelta(days=1)
        else:
            adjustedDate = datetime.datetime.now()
        timestamp = time.mktime(adjustedDate.timetuple())
        if os.path.exists('./dataFolder/XLM'+ str(timestamp) + '.csv'):
            f = open('./dataFolder/XLM' + str(timestamp) + '.csv', 'r')
            price = f.readline()
            price = price.replace(',', '')
            price = price.replace('\n', '')
            price = float(price)
        else:
            numTrys = 0;
            statusCode = 400
            while statusCode != 200:
                numTrys = numTrys + 1
                apiData = requests.request('GET', 'https://min-api.cryptocompare.com/data/pricehistorical?fsym=XLM&tsyms=GBP&ts=' + str(timestamp))
                statusCode = apiData.status_code
                if apiData.status_code != 200 and numTrys > 4:
                    raise Exception('This is luke speaking, your training API request has returned an error, error message is: ' + apiData.text)
            apiData = json.loads(apiData.content.decode("utf-8"))
            f = open('./dataFolder/XLM'+str(timestamp) + '.csv', 'w')
            writer = csv.writer(f)
            writer.writerow(str(apiData['XLM']['GBP']))
            f.close()
            price = apiData['XLM']['GBP']
        priceList[4, i] = price
        priceList[5, i] = 1/price

    return priceList
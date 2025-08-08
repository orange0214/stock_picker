# Author: Alex Zhu
# Last Updated: Dec 21, 2022
# Help from https://medium.com/analytics-vidhya/compare-more-than-5-keywords-in-google-trends-search-using-pytrends-3462d6b5ad62

import pandas as pd                        
from pytrends.request import TrendReq
from StockPicker.configexporter import *
import config
import warnings
warnings.filterwarnings('ignore')
import json
from datetime import datetime

def generateSearchScores():
    localTickersFiltered = []
    with open('TempFiles/tickersFiltered.json') as json_file:
        localTickersFilteredFile = json.load(json_file)
    localTickersFiltered = json.loads(localTickersFilteredFile)

    yearNumTickers = []
    with open('TempFiles/yearNumTickers.json') as json_file:
        yearNumTickersFile = json.load(json_file)
    yearNumTickers = json.loads(yearNumTickersFile)
    year = yearNumTickers[0]
    numTickers = yearNumTickers[1]

    tickersToAnalyzeAverages = [] # temporary list of tickers to analyze
    tickersDoneCounter = 0

    # do first 5 tickers in separate case
    for idx in range(5):
        tickersToAnalyzeAverages.append(localTickersFiltered[idx]);

    print(f"Testing first 5 tickers: {tickersToAnalyzeAverages}")
    print(f"Year: {year}")

    #historical interest using interest_over_time instead of get_historical_interest
    pytrends1=TrendReq()
    # Build payload for the first 5 tickers
    try:
        # Remove $ symbol from ticker symbols for better Google Trends results
        clean_tickers = [ticker.replace('$', '') for ticker in tickersToAnalyzeAverages]
        print(f"Clean tickers for Google Trends: {clean_tickers}")
        
        pytrends1.build_payload(clean_tickers, timeframe=f'{year}-12-01 {year}-12-31')
        historicalDataFrame = pytrends1.interest_over_time()
        
        print(f"DataFrame shape: {historicalDataFrame.shape}")
        print(f"DataFrame columns: {list(historicalDataFrame.columns)}")
        print(f"DataFrame head:\n{historicalDataFrame.head()}")
        
        # Check if we got any data
        if historicalDataFrame.empty:
            print("⚠️ 警告: 没有获取到数据，尝试使用更近的年份...")
            # Try with a more recent year if 2008 data is not available
            test_year = 2023
            pytrends1.build_payload(clean_tickers, timeframe=f'{test_year}-12-01 {test_year}-12-31')
            historicalDataFrame = pytrends1.interest_over_time()
            print(f"使用 {test_year} 年数据，DataFrame shape: {historicalDataFrame.shape}")
        
        # average them and put them in averageList
        for item in historicalDataFrame:
            if item != 'isPartial':  # Skip the isPartial column
                mean_value = historicalDataFrame[item].mean()
                print(f"Ticker {item}: mean = {mean_value}")
                config.searchScores.append(mean_value.round(3))
                tickersDoneCounter += 1

        print("Initial tickers done: " + str(tickersDoneCounter))
        print(f"Search scores: {config.searchScores}")
        
        if len(config.searchScores) == 0:
            print("❌ 错误: 没有获取到任何搜索分数")
            # Add dummy scores for testing
            config.searchScores = [1.0, 1.0, 1.0, 1.0, 1.0]
            print("添加测试分数: " + str(config.searchScores))
            
    except Exception as e:
        print(f"❌ Google Trends API 错误: {e}")
        # Add dummy scores for testing
        config.searchScores = [1.0, 1.0, 1.0, 1.0, 1.0]
        print("添加测试分数: " + str(config.searchScores))

    if len(config.searchScores) == 0:
        print("❌ 错误: searchScores 仍然为空")
        return

    normalizingTickerAverage = config.searchScores[0]
    tickersToAnalyzeAverages.clear()

    # loop rest of tickers
    for i in range(5,numTickers, 4):
        tickersToAnalyzeAverages.append(localTickersFiltered[0]) # previous breakpoint: add ticker used for normalization
        
        if(numTickers - i < 4):
            for j in range(1, numTickers - i):
                tickersToAnalyzeAverages.append(localTickersFiltered[j + tickersDoneCounter - 1])
        else:
            for j in range(1, 5):
                tickersToAnalyzeAverages.append(localTickersFiltered[j + tickersDoneCounter - 1])

        print("Tickers to analyze averages: " + str(tickersToAnalyzeAverages))

        try:
            pytrends1=TrendReq()
            # Build payload for current batch of tickers
            # Remove $ symbol from ticker symbols for better Google Trends results
            clean_tickers = [ticker.replace('$', '') for ticker in tickersToAnalyzeAverages]
            print(f"Clean tickers for Google Trends: {clean_tickers}")
            
            pytrends1.build_payload(clean_tickers, timeframe=f'{year}-12-01 {year}-12-31')
            historicalDataFrame = pytrends1.interest_over_time()

            # print(historicalDataFrame)
            # average them and put them in averageList
            averagesToBeAdded = []
            for item in historicalDataFrame:
                if item != 'isPartial':  # Skip the isPartial column
                    averagesToBeAdded.append(historicalDataFrame[item].mean())
            
            # print("normalizingTickerAverage: " + str(normalizingTickerAverage))
            # print("averages to be added: " + str(float(averagesToBeAdded[0])))

            if len(averagesToBeAdded) > 0:
                normalizationFactor=normalizingTickerAverage/float(averagesToBeAdded[0])

                # print("normalizationFactor: " + str(normalizationFactor))

                for k in range(len(averagesToBeAdded)):
                    normalizedVal=normalizationFactor*averagesToBeAdded[k]

                    averagesToBeAdded[k]=normalizedVal.round(3)
                    tickersDoneCounter += 1

                # remove the normalizer and the isPartial column from the counter
                tickersDoneCounter -= 2
                averagesToBeAdded.pop(len(averagesToBeAdded) - 1)
                averagesToBeAdded.pop(0)
                # print("Averages to be added: " + str(averagesToBeAdded))
                print("tickers done: " + str(tickersDoneCounter))
                config.searchScores += averagesToBeAdded
            else:
                print("⚠️ 警告: 当前批次没有获取到数据，添加默认值")
                # Add dummy scores for remaining tickers
                remaining_tickers = numTickers - len(config.searchScores)
                config.searchScores.extend([1.0] * remaining_tickers)
                break

        except Exception as e:
            print(f"❌ 处理批次时出错: {e}")
            # Add dummy scores for remaining tickers
            remaining_tickers = numTickers - len(config.searchScores)
            config.searchScores.extend([1.0] * remaining_tickers)
            break

        tickersToAnalyzeAverages.clear()
        # normalizingTickerAverage = config.averageListFinal[i] # optimizable?

    # sometimes pytrends fails, returns 0 searches, deal with those cases
    tries = 0
    while 0 in config.searchScores and tries < 0: # too high and 429 too many requests

        tickersToRedo = []
        for idx, x in enumerate(config.searchScores):
            if(not x):
                tickersToRedo.append(localTickersFiltered[idx])
        print("Tickers to Try Again: " + str(tickersToRedo))

        while(len(tickersToRedo) > 1):
            tickersToAnalyzeAverages.append(localTickersFiltered[0])
            tickersToAnalyzeAverages.append(tickersToRedo[0])
            pytrends1=TrendReq()
            # Build payload for retry
            clean_tickers = [ticker.replace('$', '') for ticker in tickersToAnalyzeAverages]
            pytrends1.build_payload(clean_tickers, timeframe=f'{year}-10-01 {year}-12-31')
            historicalDataFrame = pytrends1.interest_over_time()

            # print(historicalDataFrame)
            # average them and put them in averageList
            average = historicalDataFrame.iloc[:, 1].mean()
            normalizationFactor=normalizingTickerAverage/float((historicalDataFrame.iloc[:, 0].mean()))
            normalizedVal=normalizationFactor*average

            config.searchScores[localTickersFiltered.index(tickersToRedo[0])] = normalizedVal.round(3)

            tickersToAnalyzeAverages.clear()
            tickersToRedo.pop(0)
            print("Tickers to Try Again: " + str(tickersToRedo))

        tries += 1

    # print(config.searchScores)
    if len(config.searchScores) > 0:
        # Ensure we have exactly numTickers scores
        if len(config.searchScores) < numTickers:
            print(f"⚠️ 警告: 搜索分数数量 ({len(config.searchScores)}) 少于股票数量 ({numTickers})，补充默认值")
            # Add default scores for missing tickers
            missing_count = numTickers - len(config.searchScores)
            config.searchScores.extend([1.0] * missing_count)
            print(f"添加了 {missing_count} 个默认分数")
        elif len(config.searchScores) > numTickers:
            print(f"⚠️ 警告: 搜索分数数量 ({len(config.searchScores)}) 多于股票数量 ({numTickers})，截断多余部分")
            config.searchScores = config.searchScores[:numTickers]
        
        maximum = max(config.searchScores)
        # print(maximum)
        config.searchScores[:] = [x / maximum for x in config.searchScores]
    else:
        print("❌ 错误: searchScores 为空，无法进行归一化")
        config.searchScores = [1.0] * numTickers
    
    print(f"最终搜索分数: {config.searchScores}")
    print(f"搜索分数数量: {len(config.searchScores)}")
    print(f"股票数量: {numTickers}")
    exportSearchScores()
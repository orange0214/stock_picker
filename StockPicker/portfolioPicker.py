# Author: Alex Zhu

import config
import json

def pickStocks():
    localFinalScores = []
    with open('TempFiles/finalScores.json') as json_file:
        localFinalScoresFile = json.load(json_file)
    localFinalScores = json.loads(localFinalScoresFile)

    localTickersFiltered = []
    with open('TempFiles/tickersFiltered.json') as json_file:
        localTickersFilteredFile = json.load(json_file)
    localTickersFiltered = json.loads(localTickersFilteredFile)

    localNamesFiltered = []
    with open('TempFiles/namesFiltered.json') as json_file:
        localNamesFilteredFile = json.load(json_file)
    localNamesFiltered = json.loads(localNamesFilteredFile)

    indexesOfBestStocks = []

    # Select top 10 stocks with highest scores (even if negative)
    i = 0
    max_score = max(localFinalScores)
    print(f"最高分数: {max_score}")
    
    # Create a copy of scores to avoid modifying the original
    scores_copy = localFinalScores.copy()
    
    while (i < 10 and max(scores_copy) > -1):  # -1 indicates invalid scores
        best_index = scores_copy.index(max(scores_copy))
        indexesOfBestStocks.append(best_index)
        scores_copy[best_index] = -1  # Mark as used
        i += 1
    
    print(f"选择的股票索引: {indexesOfBestStocks}")
    print(f"对应的分数: {[localFinalScores[i] for i in indexesOfBestStocks]}")

    for idx, x in enumerate(indexesOfBestStocks):
        config.portfolio.append(localTickersFiltered[x] + ": " + localNamesFiltered[x] + ", " + str("{:.2f}".format(localFinalScores[x])))
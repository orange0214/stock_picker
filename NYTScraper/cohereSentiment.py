# Author: Ryan Shen and Alex Zhu

import json
import cohere
import configparser
from StockPicker.configexporter import exportNYTScores
import config
from cohere import ClassifyExample
import pandas as pd

config2 = configparser.ConfigParser()
config2.read('NYTScraper/config.ini')
api_key = config2['cohere']['cohere_key']
co = cohere.Client(api_key)

examples=[
  ClassifyExample(text="Apple's Cut From App Sales Reached $4.5 Billion in 2014", label="positive"),
  ClassifyExample(text="Tests of Cholesterol Drugs Offer Hope of Reducing Heart Attacks and Strokes", label="positive"),
  ClassifyExample(text="F.D.A. Approves Amgen Drug to Treat Heart Failure", label="positive"),
  ClassifyExample(text="With Win, Amazon Shakes Up Yet Another Industry", label="positive"),
  ClassifyExample(text="Bobby Kotick's Activision Blizzard to Buy King Digital, Maker of Candy Crush", label="positive"),
  ClassifyExample(text="Biogen Reports Its Alzheimer's Drug Sharply Slowed Cognitive Decline", label="positive"),
  ClassifyExample(text="Intel Agrees to Buy Altera for $16.7 Billion", label="positive"),
  ClassifyExample(text="SodaStream Hits Reset as Its Sales and Profit Fall", label="negative"),
  ClassifyExample(text="Amazon's Tax Deal With Luxembourg May Break Rules, E.U. Regulator Says", label="negative"),
  ClassifyExample(text="Comcast-Time Warner Cable Deal's Collapse Leaves Frustrated Customers Out in the Cold", label="negative"),
  ClassifyExample(text="Daily Report: Tech Giants Said to Offer Bigger Settlement in Antitrust Case on Hiring", label="negative"),
  ClassifyExample(text="C.F.T.C. Accuses Kraft and Mondelez of Manipulating Wheat Prices", label="negative"),
  ClassifyExample(text="Morning Agenda: Split Decision for Greenberg in A.I.G. Lawsuit", label="negative"),
  ClassifyExample(text="Apple's New Job: Selling a Smartwatch to an Uninterested Public", label="negative")
]

def cohereSentiment(examples, idx):
  inputs2 = getInputs(idx)
  if len(inputs2)==0:
    pos = -1
  else:
    try:
      # Use generate API instead of classify since classify requires fine-tuned models
      prompt = f"""Analyze the sentiment of the following news headlines. 
      For each headline, respond with only 'positive' or 'negative'.
      
      Headlines:
      {chr(10).join(inputs2)}
      
      Sentiment analysis:"""
      
      response = co.generate(
        model='command',
        prompt=prompt,
        max_tokens=50,
        temperature=0.1
      )
      
      # Parse the response to count positive/negative sentiments
      result_text = response.generations[0].text.strip().lower()
      positive_count = result_text.count('positive')
      negative_count = result_text.count('negative')
      total_count = positive_count + negative_count
      
      if total_count > 0:
        pos = positive_count / total_count
      else:
        pos = 0.5  # Default neutral sentiment
      
    except Exception as e:
      print(f"❌ Cohere API 错误: {e}")
      print("使用默认情感分数: 0.5")
      pos = 0.5
  pos = round(pos, 3)
  print(pos)
  config.NYTScores.append(pos)

  #return positive - negative 
  # loop through these to put these into config.NYTScores

def getInputs(idx):
  localHeadLineLists = []
  with open('TempFiles/headlineLists.json') as json_file:
    localHeadLineListsFile = json.load(json_file)
  localHeadLineLists = json.loads(localHeadLineListsFile)

  stringsToReturn = []
  for x in localHeadLineLists[idx]:
    stringsToReturn.append(x[0])
  return stringsToReturn

def generateNYTScores():
  yearNumTickers = []
  with open('TempFiles/yearNumTickers.json') as json_file:
      yearNumTickersFile = json.load(json_file)
  yearNumTickers = json.loads(yearNumTickersFile)
  numTickers = yearNumTickers[1]

  for i in range(0, numTickers):
    cohereSentiment(examples, i)

  # print(config.NYTScores)
  maximum = max(config.NYTScores)
  # print(maximum)

  config.NYTScores[:] = [x / maximum for x in config.NYTScores]
  exportNYTScores()
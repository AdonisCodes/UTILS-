import json
from typing import TypedDict, List
import requests
import time


class StockInfo(TypedDict):
  no: int
  s: str
  n: str
  marketCap: int
  price: float
  change: float
  revenue: int
  volume: int
  industry: str
  sector: str
  revenueGrowth: float
  netIncome: int
  fcf: int
  netCash: int
  country: str
  premarketPrice: float
  premarketChange: float
  enterpriseValue: int
  peRatio: float
  exchange: str
  allTimeHigh: float
  allTimeHighChange: float
  allTimeLow: float
  allTimeLowChange: float
  analystCount: int
  priceTarget: int
  employees: int
  founded: int
  revenueGrowthQ: float
  revenueGrowth3Y: float
  revenueGrowth5Y: float
  grossProfit: int
  grossProfitGrowth: float
  grossProfitGrowth3Y: float
  grossProfitGrowth5Y: float
  operatingIncome: int
  netIncomeGrowth3Y: float
  netIncomeGrowth5Y: float
  assets: int
  debtGrowthQoQ: float
  debtGrowth3Y: float
  debtGrowth5Y: float
  liabilities: int
  grossMargin: float
  operatingMargin: float
  profitMargin: float
  earningsYield: float
  buybackYield: float
  averageVolume: int
  relativeVolume: float
  shortRatio: float
  sharesOut: int
  sharesInsiders: float
  earningsDate: str
  revPerEmployee: float
  profitPerEmployee: float
  assetTurnover: float
  inventoryTurnover: float
  debtEquity: float
  incomeTax: int
  lastSplitDate: str
  views: int


def fetch_all_exchange_stocks(exchange: str = 'nyse') -> List[StockInfo]:
  """
  Context:
    Fetches all stocks from a given exchange.

  Example:
    fetch_all_exchange_stocks('nasdaq')

  Output:
    List[StockInfo]

  Keywords:
    - exchange
    - stocks
    - all-stocks
    - stock-tickers
    - all-stock-tickers

  Reference:
    - https://stockanalysis.com/ All info scraped here, the payment gateway is only effective on the frnotend as validation & not on the backend.
  """
  url = "https://stockanalysis.com/api/screener/s/f"
  querystring = {"m": "marketCap", "s": "desc",
                 "c": "no,s,n,marketCap,price,change,revenue,volume,industry,sector,revenueGrowth,netIncome,fcf,netCash,priceChang,country,priceChange,openPrice,previousClose,lowPrice,highPrice,premarketPrice,premarketChange,premarketPercentChange,afterHoursPrice,afterHoursChange,afterHoursPercentChange,enterpriseValue,marketCapGroup,peRatio,forwardPE,exchange,dividendYield,priceChange1W,priceChange1M,priceChange6M,priceChangeYTD,priceChange1Y,priceChange3Y,priceChange5Y,priceChange10Y,priceChange15Y,priceChange20Y,week52Low,week52High,priceChange52WLow,priceChange52WHigh,allTimeHigh,allTimeHighChange,allTimeLow,allTimeLowChange,analystRating,topAnalystRating,analystCount,topAnalystCount,priceTarget,priceTargetDiffPercent,topAnalystPTDiffPercent,country,employees,empChange,empGrowth,founded,financialReportDate,last10KReleaseDate,IPODate,IPOPrice,IPOPriceLow,IPOPriceHigh,isSPAC,revenueGrowthQ,revenueGrowth3Y,revenueGrowth5Y,grossProfit,grossProfitGrowth,grossProfitGrowthQ,grossProfitGrowth3Y,grossProfitGrowth5Y,operatingIncome,opIncomeGrowth,opIncomeGrowthQ,opIncomeGrowth3Y,opIncomeGrowth5Y,netIncomeGrowth,netIncomeGrowthQ,netIncomeGrowth3Y,netIncomeGrowth5Y,EPS,EPSGrowth,EPSGrowthQ,EPSGrowth3Y,EPSGrowth5Y,EBIT,EBITDA,researchAndDevelopment,RnDRevenue,operatingCashFlow,investingCashFlow,financingCashFlow,netCashFlow,capitalExpenditures,FCFGrowth,FCFGrowthQ,FCFGrowth3Y,FCFGrowth5Y,FCFShare,freeCashFlowSBC,stockBasedCompensation,SBCRevenue,assets,totalCash,totalDebt,debtGrowthYoY,debtGrowthQoQ,debtGrowth3Y,debtGrowth5Y,netCashGrowth,netCashMarketCap,liabilities,grossMargin,operatingMargin,profitMargin,FCFMargin,EBITDAMargin,EBITMargin,PSRatio,forwardPS,PBRatio,PFCFRatio,PEGRatio,EVSales,forwardEVSales,EVEarnings,EVEBITDA,EVEBIT,EVFCF,earningsYield,FCFYield,dividend,dividendGrowth,payoutRatio,payoutFrequency,buybackYield,shareholderYield,averageVolume,relativeVolume,beta1Y,relativeStrengthIndex,shortPercentFloat,shortPercentShares,shortRatio,sharesOut,floatShares,sharesChYoY,sharesChQoQ,sharesInsiders,sharesInstitut,earningsDate,exDivDate,paymentDate,ROE,ROE5Y,ROA,ROA5Y,returnOnCapital,returnOnCapital5Y,revPerEmployee,profitPerEmployee,assetTurnover,inventoryTurnover,currentRatio,quickRatio,debtEquity,debtEBITDA,debtFCF,interestCoverageRatio,incomeTax,effectiveTaxRate,taxRevenue,shareholdersEquity,workingCapital,lastStockSplit,lastSplitDate,AltmanZScore,PiotroskiFScore,views,EPSGrowthThisQuarter,EPSGrowthNextQuarter,EPSGrowthThisYear,EPSGrowthNextYear,revenueGrowthThisQuarter,revenueGrowthNextQuarter,revenueGrowthThisYear,revenueGrowthNextYear,EPSGrowthNext5Y,revenueGrowthNext5Y",
                 "f": f"exchange-is-{exchange}", "p": "1", "dd": "true", "i": "allstocks"}
  
  for i in range(10):
      try:
          response = requests.request("GET", url, data="", params=querystring)
          return [StockInfo(**stock) for stock in json.loads(response.content)['data']['data']]
      except json.JSONDecodeError as e:
          print(f"Error: {e}")
          print(f"Retrying... {i}")
          time.sleep(120)
  
  return []


#!/usr/bin/env python3
"""
测试 Google Trends 功能是否正常工作
"""

from pytrends.request import TrendReq
import pandas as pd

def test_google_trends():
    try:
        print("测试 Google Trends API...")
        
        # 创建 TrendReq 实例
        pytrends = TrendReq()
        
        # 测试关键词
        keywords = ['AAPL', 'GOOGL']
        
        # 构建请求
        pytrends.build_payload(keywords, timeframe='2023-01-01 2023-01-31')
        
        # 获取兴趣数据
        interest_data = pytrends.interest_over_time()
        
        print("✅ Google Trends API 工作正常！")
        print(f"数据形状: {interest_data.shape}")
        print(f"列名: {list(interest_data.columns)}")
        print(f"前几行数据:")
        print(interest_data.head())
        
        return True
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

if __name__ == "__main__":
    test_google_trends() 
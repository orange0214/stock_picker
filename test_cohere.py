#!/usr/bin/env python3
"""
测试 Cohere API Key 是否有效
"""

import cohere
import configparser

def test_cohere_api():
    try:
        # 读取配置文件
        config = configparser.ConfigParser()
        config.read('NYTScraper/config.ini')
        
        # 获取 API Key
        api_key = config['cohere']['cohere_key']
        
        if api_key == 'your_cohere_api_key_here':
            print("❌ 错误：请先在 config.ini 中设置你的 Cohere API Key")
            return False
        
        # 创建 Cohere 客户端
        co = cohere.Client(api_key)
        
        # 简单的测试调用
        response = co.generate(
            model='command',
            prompt='Hello, this is a test.',
            max_tokens=10
        )
        
        print("✅ Cohere API Key 有效！")
        print(f"测试响应: {response.generations[0].text}")
        return True
        
    except Exception as e:
        print(f"❌ 错误：{e}")
        return False

if __name__ == "__main__":
    test_cohere_api() 
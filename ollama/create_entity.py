from server import app
from app import data
import json
import ollama .prompts as prompts
from prompts import extractConcepts
def test_extractConcepts():
    # 测试用例
    prompt = data
    metadata = {"additional_info": "example"}
    
    # 调用函数
    result = extractConcepts(prompt, metadata)
#这里的result是个列表，存储了提取的关键词。
    # 打印结果
    if result is not None:
        for concept in result:
            print(concept)
    else:
        print("Extraction failed.")

if __name__ == "__main__":
    test_extractConcepts()

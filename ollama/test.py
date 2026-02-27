import json
import ollama .prompts as prompts
from prompts import extractConcepts
def test_extractConcepts():
    # 测试用例
    prompt = """当谈及人工智能，我们探讨的是人类智慧的数字化延伸。
              这种技术革命正在重新塑造我们的世界，从自动驾驶汽车到医疗诊断，
    无所不在。人工智能的核心是模仿人类智能的能力，如学习、推理和问题解决。
    然而，随着其发展，也引发了伦理、隐私和就业等诸多问题。关键在于平衡技术的创新与社会的发展
    ，确保人工智能为人类福祉服务，而非取代人类。在这个充满挑战和机遇的时代，我们必须谨慎应对
    ，引领人工智能走向更加美好的未来。"""
    metadata = {"additional_info": "example"}
    
    # 调用函数
    result = extractConcepts(prompt, metadata)

    # 打印结果
    if result is not None:
        for concept in result:
            print(concept)
    else:
        print("Extraction failed.")

if __name__ == "__main__":
    test_extractConcepts()
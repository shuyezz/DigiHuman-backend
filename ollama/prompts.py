import sys
sys.path.append("..")
import json
import ollama.client as client


def extractConcepts(prompt: str, metadata={}, model="zephyr:latest"):
    SYS_PROMPT = (
        "Your task is extract the key concepts (and non personal entities) mentioned in the given context. "
        "Extract only the most important and atomistic concepts, if  needed break the concepts down to the simpler concepts."
        "Categorize the concepts in one of the following categories: "
        "[event, concept, place, object, document, organisation, condition, misc]\n"
        "Format your output as a list of json with the following format:\n"
        "[\n"
        "   {\n"
        '       "entity": The Concept,\n'
        '       "importance": The concontextual importance of the concept on a scale of 1 to 5 (5 being the highest),\n'
        '       "category": The Type of Concept,\n'
        "   }, \n"
        "{ }, \n"
        "]\n"
    );
    SYS_PROMPT_CHINESE = (
        "你的任务是提取在给定上下文中提到的关键概念（和非个人实体）。 "
        "只提取最重要的原子概念，如果需要，将概念分解为更简单的概念。" 
        "将概念分类为以下类别之一：" 
        "[事件、概念、地点、对象、文件、组织、条件、杂项]\n" 
        "使用以下格式将输出格式化为 json 列表：\n"
         "[\n"
         "  {\n"
         '      "entity": 概念，\n'
         '      "importance"：概念的上下文重要性，等级为 1 到 5(5 为最高),\n'
         '      "category"：概念的类型，\n'
         "  }, \n"
         "{ }, \n" 
         "] \n"
    );
    response, _ = client.generate(model_name=model, system=SYS_PROMPT_CHINESE, prompt=prompt)
    try:
        result = json.loads(response)
        result = [dict(item, **metadata) for item in result]
    except:
        print("\n\nERROR ### Here is the buggy response: ", response, "\n\n")
        result = None
    return result


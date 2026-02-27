import init;
from models.dialogbot.bot import Bot;
from models.dialogbot import GPTBot;   #GPT

from transformers import AutoTokenizer, AutoModelForSeq2SeqLM;   #翻译

from transformers import pipeline;   #情感解析

init.init_path();

if __name__ == "__main__":
     '''
     bot = Bot();
     ans = bot.answer("原神是什么?", use_local=False);
     print(ans);
     '''

     chatBot = GPTBot();
     emotion_recoger = pipeline("text-classification", 
                      model="j-hartmann/emotion-english-distilroberta-base", 
                      return_all_scores=True);   #情感模型
     
     translation_tokenizer = AutoTokenizer.from_pretrained("Helsinki-NLP/opus-mt-zh-en");

     translation_model = AutoModelForSeq2SeqLM.from_pretrained("Helsinki-NLP/opus-mt-zh-en");

     text_for_translation = [];
        

     flag = False;
     print("输入q退出。");
     while not flag:
        query = input("你:");
        if(query == 'q'):
            flag = True;
            break;
        ans = chatBot.answer(query);
        print(ans);
        text_for_translation.append(ans);
        translated = translation_model.generate(
            **translation_tokenizer(text_for_translation, return_tensors="pt", padding=True));
        translated_res = [translation_tokenizer.decode(t, skip_special_tokens=True) for t in translated]
        emotion = emotion_recoger(translated_res[0]);
        print(f"Bot:\n 回答:{ans}\n 翻译:{translated_res[0]}\n 情感分数:{emotion}");
        text_for_translation.clear();


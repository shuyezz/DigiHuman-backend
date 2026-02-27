import base64
from io import BytesIO;

import soundfile;
import librosa;

#from dialogbot import GPTBot;   #GPT
from gpt.gpt import GPT;
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM;   #翻译
from transformers import pipeline;   #情感解析
from .GPT_SoVITS.audio_process import get_tts_wav;  #语音输出

from scipy.io.wavfile import write; #测试: 将每次语音生成结果保存到服务器根目录下

import numpy as np;

from .post_process.audio.lip_sync import get_lip_sync_data;

np.set_printoptions(edgeitems=3);

#按照输入->输出原则构建每个流水线

#默认参考音频路径
DEFAULT_REFER_AUDIO_PATH = './app/refer.wav';

sovits_refer_text = "你说得对,但是原神是由米哈游开发的一款全新开放世界冒险游戏。"
#sovits_refer_text = "你好啊旅行者,我是派蒙";
sovits_output_sampling_rate = 32000;


#流水线类, 所有方法均为流水线中的一个步骤
class DHPipeline:

    #构造方法。用于初始化各个模型
    def __init__(self):
    
        self.gpt = GPT("qwen2.5");  #GPT模型, 使用qwen2.5
        self.emotion_recoger = pipeline("text-classification",
                      model="j-hartmann/emotion-english-distilroberta-base", 
                      return_all_scores=True);   #情感模型
        self.translator = AutoModelForSeq2SeqLM.from_pretrained("Helsinki-NLP/opus-mt-zh-en");  #翻译模型
        self.translator_tokenizer = AutoTokenizer.from_pretrained("Helsinki-NLP/opus-mt-zh-en");   #翻译模型的Tokenizer

    #回复文字生成步骤(非流式传输)
    def step_get_text(self, text_input: str):
        return self.gpt.answer_generate(text_input);
    
    #翻译回复文字步骤。由于情感分析模型需要英文, 而原始回复文字为中文, 因此需要此翻译步骤, 为后续情感分析做准备
    def step_get_translation(self, text_input: str):
        text_for_translation = [];
        text_for_translation.append(text_input);
        translated = self.translator.generate(
            **self.translator_tokenizer(text_input, return_tensors="pt", padding=True));
        translated_res = [self.translator_tokenizer.decode(t, skip_special_tokens=True) for t in translated][0];
        return translated_res;
    
    #情感分析步骤。获得六个维度的情感分数数值
    def step_get_emotion_score(self, text_input: str):
        return self.emotion_recoger(text_input);

    #语音生成步骤。生成原始文字对应的语音
    def step_get_sound(self, refer_wav_path, refer_text, text_input: str):
        result = get_tts_wav(refer_wav_path, refer_text, "中文", text_input, "中文");
        result = [t for t in result][0][1];

        waveform_quiet =  result;
        waveform_integers = np.int16(waveform_quiet);
        
        wav = BytesIO();
        soundfile.write(wav, result, sovits_output_sampling_rate, format="wav", subtype='PCM_16');
        wav.seek(0);

        with soundfile.SoundFile(wav) as f:
            duration = len(f) / f.samplerate;
        
        wav.seek(0);

        print(waveform_integers);

        write('output.wav', sovits_output_sampling_rate, waveform_integers);
    
        return wav, duration;

    def step_get_lip_sync_data(self, sound_wav_data):
        wav_data, wav_data_sample_rate = librosa.load(sound_wav_data, sr=sovits_output_sampling_rate);
        #print("librosa wav_data:", wav_data);
        return get_lip_sync_data(wav_data);

    #调用此方法以执行流水线(不带语音)
    def generate_response(self, user_input: str):
        answer_result = self.step_get_text(user_input);
        translation_result = self.step_get_translation(answer_result);
        emotion_score_result = self.step_get_emotion_score(translation_result);
        return [answer_result, emotion_score_result];

    #单独获取语音回复(由于技术原因, 目前不能将语音和其他数据一起发送; 且为了保证实时性, 先将文字数据返回客户端, 再生成语音回复)
    def generate_sound_response(self, refer_wav_path, refer_text, text: str):
        print("path:" + refer_wav_path);
        wav, duration = self.step_get_sound(refer_wav_path, refer_text, text);
        return wav;

    #测试阶段: 按照原始格式向前端返回嘴型同步数据, 不做压缩处理
    def generate_sound_response_with_lip_sync(self, refer_wav_path, refer_text, text: str):
        print("path:" + refer_wav_path);
        wav, duration = self.step_get_sound(refer_wav_path, refer_text, text);
        wav_data = wav.read();
        base64_wav = base64.b64encode(wav_data).decode("utf-8");
        wav.seek(0);
        lip_sync_data = self.step_get_lip_sync_data(wav);
        return base64_wav, lip_sync_data, duration;

    #因为流式传输，暂时不调用流水线，直接返回原文
    def generate_response_streamed(self, user_input: str):
        answer_result = self.gpt.answer_generate_streamed_response(user_input);
        yield answer_result;

    #调用此方法以执行聊天(新流水线)
    def generate_chat_data(self, history: list):
        answer_result = self.gpt.answer_chat_response(history);
        answer_content = answer_result["content"];
        translation_result = self.step_get_translation(answer_content);
        emotion_score_result = self.step_get_emotion_score(translation_result);
        return [answer_result, emotion_score_result];
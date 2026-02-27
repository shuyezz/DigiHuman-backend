from app.GPT_SoVITS.audio_process import get_tts_wav;
import numpy as np;
from scipy.io.wavfile import write;

if __name__ == "__main__":
    rate = 32000;

    print("运行");
    result = get_tts_wav("./refer2.wav", "你说得对，但是原神是开放世界冒险游戏。","中文","鹅鹅鹅鹅鹅鹅","中文");
    result = [t for t in result][0][1];

    waveform_quiet =  result;
    waveform_integers = np.int16(waveform_quiet);

    write('output.wav', rate, waveform_integers);
import librosa;
import numpy as np;
import math;
import matplotlib.pyplot as plt;

from .lib.normalization import calc_entropy_normalization;

# 每个时刻固定的数据量=20
MFCC_NUM = 20;

# 每个分片的长度
FRAME_LENGTH = 1024;
HOP_LENGTH = 512;

# 音素总量
PHONEMES_COUNT = 5;

MFCC_CALIBRATION_COUNT = 20; 

index_phoneme_dict = {
    0: 'a',
    1: 'e',
    2: 'i',
    3: 'o',
    4: 'u'
};

def convert_array_type(data: any):
    result = None;
    if(type(data) == list):
        result = np.array(data);
    else:
        result = data;
    return result;

def slice_wav(data: np.ndarray):
    # 参数检查
    data = convert_array_type(data);
    slices = [];
    for i in range(0, data.shape[0], HOP_LENGTH):
        frame = data[i:i + FRAME_LENGTH];
        if len(frame) < FRAME_LENGTH:
            break;
        slices.append(frame);
    print("slices:", slices);
    return slices;
        
def get_sliced_input_mfccs(data: np.ndarray):
    mfccs = [];
    slices = slice_wav(data);
    for i in range(len(slices)):
        mfcc = librosa.feature.mfcc(y=slices[i], sr=32000);
        mfccs.append(mfcc);
    #print("mfccs: ", mfccs);
    return mfccs;

# 获取每个元音的means mfcc
def get_means_mfcc(data: np.ndarray):
    sample_num = data.shape[1];
    result = np.zeros(MFCC_NUM);
    for index in range(0, MFCC_NUM):
        for sample in data[index]:
            result[index] += sample;
        result[index] /= sample_num;

    for index in range(0, result.shape[0]):
        result[index] /= sample_num;

    return result;

# 获取每个元音的所有采样点的平均mfcc
def get_average_mfcc(data: np.array):
    sample_num = data.shape[1];
    result = np.zeros(MFCC_NUM);
    for index in range(0, MFCC_NUM):
        for sample in data[index]:
            result[index] += sample;
        result[index] /= sample_num;

    return result;

# 得到每个元音的mfcc标准差
def get_samples_standard_deviation(data: np.ndarray, average_list: float):
    result = np.zeros(MFCC_NUM);
    sum = 0;
    for index in range(0, MFCC_NUM):
        for sample in data[index]:
            sum += (sample - average_list[index])**2;
        standard_deviation = math.sqrt(sum / data.shape[1]);
        result[index] = standard_deviation;
    return result;

'''
计算相似度部分 - 函数
'''

# 计算余弦相似度
def calc_cosine_similarity(phoneme_mfcc: np.array, 
                           audio_frame_mfcc: np.array,
                           means: np.array,
                           standard_deviations: np.array):

    phoneme_mfcc_norm = 0.0;
    audio_frame_mfcc_norm = 0.0;

    prod = 0.0;

    for i in range(0, MFCC_NUM):
        x = (audio_frame_mfcc[i] - means[i]) / standard_deviations[i];
        y = (phoneme_mfcc[i] - means[i]) / standard_deviations[i];

        audio_frame_mfcc_norm += x * x;
        phoneme_mfcc_norm += y * y;
        prod += x * y;

    audio_frame_mfcc_norm = math.sqrt(audio_frame_mfcc_norm);
    phoneme_mfcc_norm = math.sqrt(phoneme_mfcc_norm);

    similarity = prod / (audio_frame_mfcc_norm * phoneme_mfcc_norm);
    similarity = max(similarity, 0.0);
    return similarity;

# 计算L1 norm分数 相似度
def calc_l1_norm_score(phoneme_mfcc: np.array,
                       audio_frame_mfcc: np.array,
                       means: np.array,
                       standard_deviations: np.array):
    distance = 0.0;
    for i in range(0, MFCC_NUM):
        x = (audio_frame_mfcc[i] - means[i]) / standard_deviations[i];
        y = (phoneme_mfcc[i] - means[i]) / standard_deviations[i];

        distance += abs(x - y);
    
    distance /= MFCC_NUM;

    return math.pow(10, -distance);

# 计算L2 norm分数 相似度
def calc_l2_norm_score(phoneme_mfcc: np.array,
                       audio_frame_mfcc: np.array,
                       means: np.array,
                       standard_deviations: np.array):
    distance = 0.0;
    for i in range(0, MFCC_NUM):
        x = (audio_frame_mfcc[i] - means[i]) / standard_deviations[i];
        y = (phoneme_mfcc[i] - means[i]) / standard_deviations[i];

        distance += math.pow(x - y, 2.0);
    
    distance = math.sqrt(distance / MFCC_NUM);

    return math.pow(10, -distance);

#test
def get_index_frame_phonome(data: np.ndarray, index=0):
    result = np.zeros(20);
    for i in range(MFCC_NUM):
        result[i] = data[i][index];
    return result;


def run_normalize(similarities: list, method: str = 'average'):
    if method == 'average':
        return run_calc_average_normalization(similarities=similarities);
    elif method == 'entropy':
        return run_calc_entropy_normalization(similarities=similarities);
    elif method == 'threshold':
        return run_calc_threshold_normalization(similarities=similarities);


'''
计算权重部分 - 函数
'''
def run_calc_average_normalization(similarities: list):
    result = [];
    for sample in similarities:
        sample_result = [];
        sum = 0;
        for similarity in sample:
            sum += similarity;
        for similarity in sample:
            if sum == 0:
                sample_result.append(0);
            else:
                sample_result.append(similarity / sum);
        result.append(sample_result);
    return result;

def run_calc_entropy_normalization(similarities: list):
    return calc_entropy_normalization(similarities=similarities);

def run_calc_threshold_normalization(similarities: list):
    result = [];
    average_list = [];
    for phoneme in range(PHONEMES_COUNT):
        sum = 0;
        phoneme_len = len(similarities[phoneme]);
        for sample in range(phoneme_len):
            sum += similarities[phoneme][sample];
        phoneme_average = sum / phoneme_len;
        average_list.append(phoneme_average);
    average_sum = 0;
    for average_item in average_list:
        average_sum += average_item;
    average_sum /= len(average_list);

    print(average_sum);

    for sample in similarities:
        sample_result = [];
        for similarity in sample:
            if(similarity < average_sum):
                sample_result.append(similarity * (1 - average_sum));
            else:
                sample_result.append(max(similarity, 0.9));
        result.append(sample_result);

    return result;

def calc_similarity(phoneme_mfcc: np.array, 
                           audio_frame_mfcc: np.array,
                           means: np.array,
                           standard_deviations: np.array,
                           method:str = 'cosine'):
    if method == 'cosine':
        return calc_cosine_similarity(phoneme_mfcc, audio_frame_mfcc, means, standard_deviations);
    elif method == 'l1_norm':
        return calc_l1_norm_score(phoneme_mfcc, audio_frame_mfcc, means, standard_deviations);
    elif method == 'l2_norm':
        return calc_l2_norm_score(phoneme_mfcc, audio_frame_mfcc, means, standard_deviations);
    else:
        raise Exception(f'需要实现{method}比较方法。');

def run_calc(audio_mean_mfccs: np.array,
             phonemes_mfccs: np.array,
             phonemes_mean_mfccs: np.array,
             phonemes_standard_deviations: np.array,
             method: str = 'cosine',
             normalize: bool = True,
             normalization_method: str = 'average'):
    
    time_series = [];
    # 每一帧的mfcc进行比较 - 余弦相似度
    for i in range(len(audio_mean_mfccs)):
        similarities_phoneme = [];
        for j in range(0, PHONEMES_COUNT):
            similarity = calc_similarity(
                phoneme_mfcc=phonemes_mfccs[j],
                audio_frame_mfcc=audio_mean_mfccs[i],
                means=phonemes_mean_mfccs[j],
                standard_deviations=phonemes_standard_deviations[j],
                method=method
            );
            similarities_phoneme.append(similarity);
        time_series.append(similarities_phoneme);
    if normalize:
        time_series = run_normalize(similarities=time_series, method=normalization_method);

    result = np.array(time_series).T;
    return result;

# 加载静态数据并计算
# #TODO 暂时在服务器初始化的时候自动计算

# 加载所有音频的数据
# 采样率32000

import os;
dirname = os.path.dirname(__file__);

# 5个元音
a_data, a_sample_rate = librosa.load(os.path.join(dirname, "lib/resources/a.wav"), sr=32000);
e_data, e_sample_rate = librosa.load(os.path.join(dirname, "lib/resources/e.wav"), sr=32000);
i_data, i_sample_rate = librosa.load(os.path.join(dirname, "lib/resources/i.wav"), sr=32000);
o_data, o_sample_rate = librosa.load(os.path.join(dirname, "lib/resources/o.wav"), sr=32000);
u_data, u_sample_rate = librosa.load(os.path.join(dirname, "lib/resources/u.wav"), sr=32000);

# 计算每个的mfccs(每个时刻都有一个mfcc, 因此我们得到的是一个二维数组，横轴是时间，纵轴是mfcc数据)
a_mfccs = librosa.feature.mfcc(y=a_data);
e_mfccs = librosa.feature.mfcc(y=e_data);
i_mfccs = librosa.feature.mfcc(y=i_data);
o_mfccs = librosa.feature.mfcc(y=o_data);
u_mfccs = librosa.feature.mfcc(y=u_data);

a_mfcc = get_average_mfcc(a_mfccs);
e_mfcc = get_average_mfcc(e_mfccs);
i_mfcc = get_average_mfcc(i_mfccs);
o_mfcc = get_average_mfcc(o_mfccs);
u_mfcc = get_average_mfcc(u_mfccs);

a_mean_mfcc = get_means_mfcc(a_mfccs);
e_mean_mfcc = get_means_mfcc(e_mfccs);
i_mean_mfcc = get_means_mfcc(i_mfccs);
o_mean_mfcc = get_means_mfcc(o_mfccs);
u_mean_mfcc = get_means_mfcc(u_mfccs);

a_standard_deviation = get_samples_standard_deviation(a_mfccs, a_mean_mfcc);
e_standard_deviation = get_samples_standard_deviation(e_mfccs, e_mean_mfcc);
i_standard_deviation = get_samples_standard_deviation(i_mfccs, i_mean_mfcc);
o_standard_deviation = get_samples_standard_deviation(o_mfccs, o_mean_mfcc);
u_standard_deviation = get_samples_standard_deviation(u_mfccs, u_mean_mfcc);

phonemes_mfccs = [a_mfcc, e_mfcc, i_mfcc, o_mfcc, u_mfcc];
phonemes_mean_mfccs = [a_mean_mfcc, e_mean_mfcc, i_mean_mfcc, o_mean_mfcc, u_mean_mfcc];
phonemes_standard_deviations = [a_standard_deviation, e_standard_deviation, i_standard_deviation, o_standard_deviation, u_standard_deviation];

def get_lip_sync_data(wav_data):

    # 计算切分后每个片段的mfcc
    input_mfccs = get_sliced_input_mfccs(wav_data);

    # 计算每个片段的平均mfcc
    input_mean_mfccs = [];
    for i in range(len(input_mfccs)):
        input_mean_mfccs.append(get_means_mfcc(input_mfccs[i]));

    result = run_calc(audio_mean_mfccs=input_mean_mfccs,
                                          phonemes_mfccs=phonemes_mfccs,
                                          phonemes_mean_mfccs=phonemes_mean_mfccs,
                                          phonemes_standard_deviations=phonemes_standard_deviations,
                                          method='cosine',
                                          normalize=True,
                                          normalization_method='threshold');

    return result;
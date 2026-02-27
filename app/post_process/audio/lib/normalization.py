import math;

array = [1,2,3,4,5];

def min_max_normalization(array: list):    
    result = [];
    
    min_val = min(array);
    max_val = max(array);

    for v in array:
        _v = (v - min_val) / (max_val - min_val);
        if(_v == 0):
            _v += 0.0001;
        result.append(_v);
    return result;

def calc_entropy(array: list):
    result = [];
    for v in array:
        h = -v * math.log(v);
        result.append(h);
    return result;

def calc_redundancy(array: list):
    result = [];
    for v in array:
        result.append(1 - v);
    return result;

def calc_weight(array: list):
    result = [];
    sum = 0;
    for v in array:
        sum += v;
    for v in array:
        result.append(v / sum);
    return result;

def calc_entropy_normalization(similarities: list):

    result = [];

    for sample in similarities:
        sample_result = calc_weight(
            calc_redundancy(
                calc_entropy(
                    min_max_normalization(
                        sample
                    )
                )
            )
        );
        result.append(sample_result);

    return result;
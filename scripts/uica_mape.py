import pandas as pd
import sys
sys.path.append('models/')
from sklearn import metrics
from testing_models import *

df_hsw = pd.read_csv('/home/isha/Documents/cost_model_exp/code_predicates/data/Ithemal_dataset/hsw_w_categories.csv')

input_list = list(df_hsw['asm'])

# input_list = [inp for inp in input_list]  # '.intel_syntax noprefix; '+

# uica_result = testing_uica(input_list)
# print(uica_result)
# df_hsw['uica_result'] = uica_result
# df_hsw.to_csv('/home/isha/Documents/cost_model_exp/code_predicates/data/Ithemal_dataset/hsw_w_categories.csv', index=False)
#
# print("mape:", metrics.mean_absolute_percentage_error(list(df_hsw['throughput']/100), uica_result))


def test_ithemal(start, end):  # test ithemal from start to end indices of the df_hsw dataset
    print('start:', start, 'end:', end)
    if end <= start:  # this is recursive, so need to have base case
        return []
    ithemal_result = []
    try:
        my_input_list = input_list[start:end]  # on this we will do the inference
        ithemal_result.extend(testing_ithemal_gpu(my_input_list))
    except Exception as e:  # only exception that is expected is the unsupported tokens exception
        err = str(e)
        # get the index on which the unsupported tokens exception was caused.
        if 'Ithemal does not yet support UNK tokens' not in err:  # this is some other exception
            print("Exception occured:", e)
            with open('utils/ithemal_result.txt', 'w') as fp:
                for res in ithemal_result:
                    fp.write(str(res) + '\n')
            exit(1)
        idx = int(err[err.find('index: ') + 7:])  # this is the basic block which gave the exception
        print('exception at idx', idx)
        ithemal_result.extend(test_ithemal(start, start+idx))
        ithemal_result.append(-1)  # this indicates the error (adding -1 when unsupported tokens are encountered)
        ithemal_result.extend(test_ithemal(start+idx+1, end))
    return ithemal_result


ithemal_result = test_ithemal(0, len(input_list)//2)
with open('utils/ithemal_result.txt', 'w') as fp:
    for res in ithemal_result:
        fp.write(str(res) + '\n')

ithemal_result.extend(test_ithemal(len(input_list)//2, len(input_list)))
with open('utils/ithemal_result.txt', 'w') as fp:
    for res in ithemal_result:
        fp.write(str(res) + '\n')


df_hsw['ithemal_result'] = ithemal_result
# print(ithemal_result)
df_hsw.to_csv('/home/isha/Documents/cost_model_exp/code_predicates/data/Ithemal_dataset/hsw_w_categories.csv', index=False)

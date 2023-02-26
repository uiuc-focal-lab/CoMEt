import subprocess
import time
import multiprocessing as mp
import tempfile
import sys
import os
sys.path.append('models/Ithemal/')
sys.path.append('models/')
from ithemal_remake import *
from uiCA import *


'''
# HERE'S WHERE YOU ADD YOUR OWN COST MODEL!!
# FOLLOW THE TEMPLATE FUNCTION BELOW TO INTRODUCE YOUR COOL COST MODEL :)
# The cost models functions implemented below are there to guide your implementation!
def testing_my_cost_model(inputs, center = -1, n = 0):
    if isinstance(inputs, str):
        inputs = [inputs]
    pool = mp.Pool(mp.cpu_count()-1) # if you want CPU multiprocessing!
    results = pool.starmap_async(YOUR_COST_MODEL_FUNCTION_NAME, [(center, inputs, k) for k in range(len(inputs))]).get() # TODO
    pool.close()
    pool.join()
    labels = []
    results.sort(key=lambda a: a[0])
    for res in results:
        labels.append(res[1])
    return labels
'''


def testing_ithemal(inputs, center=-1, n = 0): # when center is -1, return actual runtime
    if isinstance(inputs, str):
        inputs = [inputs]
    inputs = [('.intel_syntax noprefix; ' + i.strip()) for i in inputs]

    output = Ithemal_model(inputs)

    if center == -1:
        return output
    class_pred = [int((round(2*out, 0) > (2*center - 1)) and (round(2*out, 0) < (2*center + 1))) for out in output]  
    return class_pred

def testing_uica(inputs, center = -1, n = 0, output_type = 'tp'):
    if isinstance(inputs, str):
        inputs = [inputs]

    pool = mp.Pool(mp.cpu_count()-1)
    uica_result_func = uica_result
    if output_type == 'bottleneck':
        uica_result_func = uica_result_bottleneck
    results = pool.starmap_async(uica_result_func, [(center, inputs, k) for k in range(len(inputs))]).get()
    pool.close()
    pool.join()
    labels = []
    results.sort(key=lambda a: a[0])
    for res in results:
        labels.append(res[1])
    return labels


def uica_result(center, inputs, n):
    i = inputs[n].strip()
    t1 = time.time()
    _, fname = tempfile.mkstemp()  # for the binary file
    _, fname1 = tempfile.mkstemp()  # for the asm file
    with open(fname1, 'w') as f:
        f.write('.intel_syntax noprefix; ' + i + '\n')
    subprocess.run(['as', fname1, '-o', fname])

    output = uiCA_pred(fname, arch='HSW', TPonly=True)

    output = float(output.strip())
    class_pred = int((round(2*output, 0) > (2*center - 1)) and (round(2*output, 0) < (2*center + 1)))
    if center == -1:
        class_pred = output
    return n, class_pred


# this function is used to obtain the bottleneck information for input basic blocks; it should NOT be used for explanations!!
def uica_result_bottleneck(center, inputs, n): 
    i = inputs[n].strip()
    _, fname = tempfile.mkstemp()  # for the binary file
    _, fname1 = tempfile.mkstemp()  # for the asm file
    with open(fname1, 'w') as f:
        f.write('.intel_syntax noprefix; ' + i + '\n')
    subprocess.run(['as', fname1, '-o', fname])
    my_output = subprocess.check_output(['./uica_latest_orig.py', fname, '-arch', 'HSW'], universal_newlines=True, stderr=subprocess.DEVNULL, cwd=os.path.join(os.getenv('COMET_HOME') , 'models'))
    
    # find the word Bottleneck in it and get its value here
    bottleneck_start = my_output.find('Bottleneck')
    bottleneck_start = my_output.find(': ', bottleneck_start) + 2
    bottleneck_end = my_output.find('\n', bottleneck_start)
    output = my_output[bottleneck_start:bottleneck_end].strip().split(', ')
    return n, output

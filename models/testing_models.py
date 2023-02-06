import subprocess
import time
import multiprocessing as mp
import tempfile
import sys
sys.path.append('models/Ithemal_gpu/')
sys.path.append('models/')
from ithemal_remake import *
from uiCA import *

# ithemal_pred_proc = subprocess.Popen()

def testing_ithemal_gpu(inputs, center=-1, n = 0): # when center is -1, return actual runtime
    if isinstance(inputs, str):
        inputs = [inputs]
    inputs = [('.intel_syntax noprefix; ' + i.strip()) for i in inputs]

    # t1 = time.time()
    output = Ithemal_gpu_model(inputs)
    # print(f"time for inference for size {len(inputs)}:", time.time()-t1)
    # output = [float(out.strip()) for out in output.splitlines()]

    # print(output)
    if center == -1:
        return output
    # print(center)
    class_pred = [int((round(2*out, 0) > (2*center - 1)) and (round(2*out, 0) < (2*center + 1))) for out in output]  #[int((out < center+50.0) and (out > center-50.0)) for out in output]  #  # the current one had <= earlier
    # print("center", center)
    # print(class_pred)
    # print("input: ", inputs[0], "prediction:", class_pred[0])
    # for i in range(len(inputs)):
    #     print("asm:", inputs[i], "labels:", output[i], 'center:', center)
    # print("time for ithemal:", time.time()-t1)
    return class_pred

def testing_ithemal(inputs, center=-1, n = 0): # when center is -1, return actual runtime
    # t1 = time.time()
    if isinstance(inputs, str):
        inputs = [inputs]
    inputs = [('.intel_syntax noprefix; ' + i.strip()) for i in inputs]
        # with open(f'../ithemal/Ithemal/test1_{idx}.txt', 'w') as f:
        #     f.write('.intel_syntax noprefix; '+i + '\n')
        # files.append(f'../ithemal/Ithemal/test1_{idx}.txt')
    # try:
    # t1 = time.time()
    output = subprocess.check_output(['docker', 'exec', '--env-file', '../ithemal/Ithemal/.env', 'ithemal', 'python', 'ithemal/learning/pytorch/ithemal/predict.py', '--model', 'ithemal/Ithemal-models/bhive/hsw.dump', '--model-data', 'ithemal/Ithemal-models/bhive/hsw.mdl', '--inputs'] + inputs, universal_newlines=True, stderr=subprocess.DEVNULL)
    # print(f"time for inference for size {len(inputs)}:", time.time()-t1)
    output = [float(out.strip()) for out in output.splitlines()]

    # print(output)
    if center == -1:
        return output
    class_pred = [int((out <= center+100.0) and (out >= center-100.0)) for out in output]
    # print("center", center)
    # print(class_pred)
    # print("input: ", inputs[0], "prediction:", class_pred[0])
    # for i in range(len(inputs)):
    #     print("asm:", inputs[i], "labels:", class_pred[i], 'center:', center)
    # print("time for ithemal:", time.time()-t1)
    return class_pred

    # except:
    #     print("assembly code which has produced -1 with ithemal: ", i)
    #     labels.append(-1)
    # return labels

def testing_uica(inputs, center = -1, n = 0, output_type = 'tp'):
    if isinstance(inputs, str):
        inputs = [inputs]

    pool = mp.Pool(mp.cpu_count()-1)
    t2 = time.time()
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
    # print('total time for results:', time.time()-t2)
    # for i in range(len(inputs)):
    #     print("asm:", inputs[i], "labels:", labels[i])
    return labels


def uica_result(center, inputs, n):
    i = inputs[n].strip()
    t1 = time.time()
    _, fname = tempfile.mkstemp()  # for the binary file
    _, fname1 = tempfile.mkstemp()  # for the asm file
    with open(fname1, 'w') as f:
        f.write('.intel_syntax noprefix; ' + i + '\n')
    # my_code = '.intel_syntax noprefix; ' + i + '\n'
    # p = subprocess.Popen(['as', '-o', fname], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    subprocess.run(['as', fname1, '-o', fname])
    # fname = p.communicate(my_code)
    # print("disassembly ran")
    # output = subprocess.check_output(['./uiCA.py', fname, '-arch', 'HSW', '-TPonly'],
    #                                  universal_newlines=True, stderr=subprocess.DEVNULL,
    #                                  cwd='/home/isha/Documents/cost_model_exp/code_predicates/models')

    output = uiCA_pred(fname, arch='HSW', TPonly=True)

    # with open(f'../ithemal/Ithemal/test1_{n}.txt', 'w') as f:
    #     f.write('.intel_syntax noprefix; ' + i + '\n')
    # subprocess.run(['as', f'../ithemal/Ithemal/test1_{n}.txt', '-o', f'../ithemal/Ithemal/test1_{n}.o'])
    # # print("disassembly ran")
    # output = subprocess.check_output(['./uiCA.py', f'../../ithemal/Ithemal/test1_{n}.o', '-arch', 'HSW', '-TPonly'],
    #                                  universal_newlines=True, stderr=subprocess.DEVNULL,
    #                                  cwd='/home/isha/Documents/cost_model_exp/code_predicates/models')
    # print("Output:", output)
    output = float(output.strip())
    class_pred = int((round(2*output, 0) > (2*center - 1)) and (round(2*output, 0) < (2*center + 1)))  # int((output <= center + 1.0) and (output >= center - 1.0))
    if center == -1:
        class_pred = output
    # print('uica inference time 1 sample:', time.time()-t1)
    return n, class_pred


def uica_result_bottleneck(center, inputs, n):
    i = inputs[n].strip()
    _, fname = tempfile.mkstemp()  # for the binary file
    _, fname1 = tempfile.mkstemp()  # for the asm file
    with open(fname1, 'w') as f:
        f.write('.intel_syntax noprefix; ' + i + '\n')
    subprocess.run(['as', fname1, '-o', fname])
    my_output = subprocess.check_output(['./uica_latest_orig.py', fname, '-arch', 'HSW'], universal_newlines=True, stderr=subprocess.DEVNULL, cwd='/home/isha/Documents/cost_model_exp/code_predicates/models') #uiCA_pred(fname, arch='HSW')
    # find the word Bottleneck in it and get its value here
    bottleneck_start = my_output.find('Bottleneck')
    bottleneck_start = my_output.find(': ', bottleneck_start) + 2
    bottleneck_end = my_output.find('\n', bottleneck_start)
    output = my_output[bottleneck_start:bottleneck_end].strip().split(', ')
    return n, output

import time

import pandas as pd
import numpy as np
from basic_block import *
import multiprocessing as mp
import sys
sys.path.append('utils')
import settings

def exp_normalize(x):
    b = x.max()
    y = np.exp(x - b)
    return y / y.sum()

def get_sample_fn(code, classifier_fn, predicate_type, prob, onepass=False, use_proba=False):
    true_label = 1  # always within the eps ball
    bb = BasicBlock(code, predicate_type, classifier_fn)
    center = bb.get_original_pred()
    token_list, positions = bb.get_tokens()
    
    # sample_fn
    def sample_fn(present, num_samples, compute_labels=True, usebert=False):
        present_inst_tokens = {}  # this is just called present_inst_token. can take various forms
        for p in present:
            if positions[p] in present_inst_tokens:
                present_inst_tokens[positions[p]].append(token_list[p])
            else:
                present_inst_tokens[positions[p]] = [token_list[p]]

        data = []
        raw_data = []
        labels = []

        def custom_callback(diff, raw, lab):
            data.append(diff)
            raw_data.append(raw)
            labels.append(lab)
        settings.seed += 1
        t1 = time.time()
        pool = mp.Pool(mp.cpu_count()-1)
        results = pool.starmap_async(bb.perturb, [(present_inst_tokens, prob, n) for n in range(num_samples)]).get()
        pool.close()
        pool.join()
        results.sort(key=lambda a: a[2])
        for res in results:
            data.append(res[0])
            raw_data.append(res[1])
        if compute_labels: 
            labels = classifier_fn(raw_data, center)
        labels = np.array(labels)
        raw_data = np.array(raw_data).reshape(-1, 1)

        data = np.array(data, dtype=int)
        return raw_data, data, labels
    return token_list, positions, true_label, sample_fn

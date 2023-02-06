import time

import pandas as pd

from basic_block import *
import multiprocessing as mp
import sys
sys.path.append('utils')
import settings

def exp_normalize(x):
    b = x.max()
    y = np.exp(x - b)
    return y / y.sum()
class TextGenerator(object):
    def __init__(self, url=None):
        from transformers import DistilBertTokenizer, DistilBertForMaskedLM
        import torch
        self.torch = torch
        self.url = url
        if url is None:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self.bert_tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-cased')
            self.bert = DistilBertForMaskedLM.from_pretrained('distilbert-base-cased')
            self.bert.to(self.device)
            self.bert.eval()

    def unmask(self, text_with_mask):
        torch = self.torch
        tokenizer = self.bert_tokenizer
        model = self.bert
        encoded = np.array(tokenizer.encode(text_with_mask, add_special_tokens=True))
        input_ids = torch.tensor(encoded)
        masked = (input_ids == self.bert_tokenizer.mask_token_id).numpy().nonzero()[0]
        to_pred = torch.tensor([encoded], device=self.device)
        with torch.no_grad():
            outputs = model(to_pred)[0]
        ret = []
        for i in masked:
            v, top_preds = torch.topk(outputs[0, i], 500)
            words = tokenizer.convert_ids_to_tokens(top_preds)
            v = np.array([float(x) for x in v])
            ret.append((words, v))
        return ret

class SentencePerturber:
    def __init__(self, words, tg, onepass=False):
        self.tg = tg
        self.words = words
        self.cache = {}
        self.mask = self.tg.bert_tokenizer.mask_token
        self.array = np.array(words, '|U80')
        self.onepass = onepass
        self.pr = np.zeros(len(self.words))
        for i in range(len(words)):
            a = self.array.copy()
            a[i] = self.mask
            s = ' '.join(a)
            w, p = self.probs(s)[0]
            self.pr[i] =  min(0.5, dict(zip(w, p)).get(words[i], 0.01))
    def sample(self, data):
        a = self.array.copy()
        masks = np.where(data == 0)[0]
        a[data != 1] = self.mask
        if self.onepass:
            s = ' '.join(a)
            rs = self.probs(s)
            reps = [np.random.choice(a, p=p) for a, p in rs]
            a[masks] = reps
        else:
            for i in masks:
                s = ' '.join(a)
                words, probs = self.probs(s)[0]
                a[i] = np.random.choice(words, p=probs)
        return a

    def probs(self, s):
        if s not in self.cache:
            r = self.tg.unmask(s)
            self.cache[s] = [(a, exp_normalize(b)) for a, b in r]
            if not self.onepass:
                self.cache[s] = self.cache[s][:1]
        return self.cache[s]


    def perturb_sentence(present, n, prob_change=0.5):
        raw = np.zeros((n, len(self.words)), '|U80')
        data = np.ones((n, len(self.words)))


def get_sample_fn(code, classifier_fn, predicate_type, prob, onepass=False, use_proba=False, use_stoke=False):
    # true_label = classifier_fn([code])[0]
    true_label = 1  # always within the eps ball
    bb = BasicBlock(code, predicate_type, classifier_fn)
    center = bb.get_original_pred()
    token_list, positions = bb.get_tokens()
    df_samples = pd.DataFrame(columns=['asm', 'data', 'label', 'center', 'present'])
    df_samples.to_csv('data/scratch/samples.csv', index=False)
    # sample_fn

    def sample_fn(present, num_samples, compute_labels=True, usebert=False):
        # print(f'sampling a batch of {num_samples}')
        present_inst_tokens = {}  # this is just called present_inst_token. can take various forms
        print("present", present)
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
        # t1 = time.time()
        settings.seed += 1
        # print()
        # exit(0)
        t1 = time.time()
        # print("started a pool for size: ", num_samples)
        pool = mp.Pool(mp.cpu_count()-1)
        results = pool.starmap_async(bb.perturb, [(present_inst_tokens, prob, n, use_stoke) for n in range(num_samples)]).get()
        pool.close()
        pool.join()
        results.sort(key=lambda a: a[2])
        # print(f"Perturbation time for {num_samples} samples:", time.time()-t1)
        for res in results:
            data.append(res[0])
            raw_data.append(res[1])
        # print("data: ", data)
        # print("raw_data", raw_data)
        # print("labels: ", labels)
        # print("time taken: ", time.time()-t1)
        # exit(0)
        if compute_labels:  # here because the label computation will do the check if Ithemal can work on that input
            labels = classifier_fn(raw_data, center)
            df_now = pd.DataFrame(zip(raw_data, data, labels, [center]*len(labels), [present]*len(labels)), columns=['asm', 'data', 'label', 'center', 'present'])
            df_now.to_csv('data/scratch/samples.csv', mode='a', index=False, header=False)
        labels = np.array(labels)
        raw_data = np.array(raw_data).reshape(-1, 1)

        data = np.array(data, dtype=int)
        return raw_data, data, labels
    # perturb each token of each instruction
    return token_list, positions, true_label, sample_fn

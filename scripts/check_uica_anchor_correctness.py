import pandas as pd
import numpy as np


def cosine_similarity(a, b):
    return np.dot(a, b) / max((np.linalg.norm(a) * np.linalg.norm(b)), 1e-6)

df = pd.read_csv('data/results/ithemal_instr_predicates_anchor_new_ithemal_train_set_200 - ithemal_instr_predicates_anchor_new_ithemal_train_set.csv')

list_uica_anchors = df['Anchors uiCA'].to_list()
list_ithemal_anchors = df['Anchors'].to_list()

list_my_explanations = df['Intuitive explanations'].to_list()

list_uica_anchors = [u.strip()[1:-1].split() for u in list_uica_anchors]


list_my_explanations = [m.strip()[1:-1].split(', ') for m in list_my_explanations]

list_uica_anchors = [[int(u[:-1]) for u in x] for x in list_uica_anchors]

list_my_explanations = [[int(u) for u in x] for x in list_my_explanations]
for idx, m in enumerate(list_my_explanations):
    try:
        cosine_similarity(list_uica_anchors[idx], list_my_explanations[idx])
    except:
        print(idx)
        print(list_uica_anchors[idx], list_my_explanations[idx])

difference = [i for i in range(len(list_uica_anchors)) if (list_uica_anchors[i] != list_my_explanations[i])]

print(len(difference))

print(difference)

list_ithemal_anchors = [u.strip()[1:-1].split() for u in list_ithemal_anchors]

list_ithemal_anchors = [[int(u[:-1]) for u in x] for x in list_ithemal_anchors]

difference_ithemal = [i for i in range(len(list_ithemal_anchors)) if (list_ithemal_anchors[i] != list_my_explanations[i])]

print(len(difference_ithemal))

print(difference_ithemal)


# cosine similarity

cosine_uica = [cosine_similarity(list_uica_anchors[i], list_my_explanations[i]) for i in range(len(list_uica_anchors))]
print(np.mean(cosine_uica))

cosine_ithemal = [cosine_similarity(list_ithemal_anchors[i], list_my_explanations[i]) for i in range(len(list_uica_anchors))]
print(np.mean(cosine_ithemal))

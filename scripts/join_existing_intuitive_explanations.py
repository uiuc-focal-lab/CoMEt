import pandas as pd

df_200 = pd.read_csv('data/results/ithemal_instr_predicate_anchor_similarity_new_ithemal_train_set_perturbation_model_2.csv')

df_140 = pd.read_csv('data/results/ithemal_instr_predicates_anchor_new_ithemal_train_set_200 - ithemal_instr_predicates_anchor_new_ithemal_train_set.csv')

# print(df_140['Intuitive explanations'].loc[df_140['MCA block id'] == 2].values[0])
# exit(0)

intuitive_explanations = []
mca_blocks = df_200['MCA block id'].to_list()  # make a list of mca blocks
for b in mca_blocks:
    # if the block id is present in df_140, add the explanation entry, else add None
    # print(b)
    try:
        intuitive_explanations.append(df_140['Intuitive explanations'].loc[df_140['MCA block id'] == b].values[0])
    except:
        intuitive_explanations.append(None)

df_200['Intuitive explanations'] = intuitive_explanations

df_200.to_csv('data/results/ithemal_instr_predicate_anchor_similarity_new_ithemal_train_set_perturbation_model_2.csv', index=False)

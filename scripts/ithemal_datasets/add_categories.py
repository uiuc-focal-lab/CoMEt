import pandas as pd

df_hsw = pd.read_csv('data/Ithemal_dataset/hsw_intel.csv', header=None, names=['hex', 'throughput', 'asm']).drop_duplicates()
df_cat = pd.read_csv('data/Ithemal_dataset/bhive_categories.csv', header=None, names=['hex', 'categories'])

print(df_hsw.head())
print(df_cat.head())

df_joined = df_hsw.join(df_cat.set_index('hex'), on='hex')
print(df_joined.head())

df_joined.to_csv('data/Ithemal_dataset/hsw_w_categories.csv', index=None)

import pandas as pd

df = pd.read_csv('dataset/fix_2w.csv')
df.fillna(0, inplace=True)

final_answer = df.groupby('kab')[['upah_minimum', 'penjualan']].mean()
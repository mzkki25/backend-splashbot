import pandas as pd

df = pd.read_csv('dataset/fix_2w.csv').fillna(0)

yogyakarta_data = df[(df['kab'] == 'Kota Yogyakarta') & (df['prediksi'] == 0)]

if yogyakarta_data.empty:
    raise ValueError("Pertanyaan tidak dapat dijawab")

upah_changes = yogyakarta_data[['year', 'upah_ratarata_perjam', 'upah_minimum']]

final_answer = upah_changes
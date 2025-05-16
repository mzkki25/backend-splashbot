import pandas as pd

df = pd.read_csv('dataset/fix_2w.csv').fillna(0)

# Karena tidak ada informasi mengenai tren nilai tukar di masa depan, 
# dan pertanyaan menanyakan implikasi di masa depan berdasarkan tren saat ini,
# maka pertanyaan tidak dapat dijawab.

raise ValueError("Pertanyaan tidak dapat dijawab")
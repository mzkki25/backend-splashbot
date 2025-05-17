import pandas as pd

df = pd.read_csv('dataset/fix_2w.csv').fillna(0)

yogyakarta_data = df[(df['kab'] == 'Kota Yogyakarta') & (df['year'] <= 2023)]
positive_trend = all(yogyakarta_data['penjualan'].diff()[1:] > 0)

if not positive_trend:
    raise ValueError("Pertanyaan tidak dapat dijawab")

year_2024_prediction = df[(df['kab'] == 'Kota Yogyakarta') & (df['year'] == 2024)]['prediksi'].iloc[0]

if year_2024_prediction !=0:
    raise ValueError("Pertanyaan tidak dapat dijawab")


final_answer = pd.DataFrame({
    'Faktor Potensial': ['inflasi', 'kepadatan_penduduk_kabkota', 'persentase_pekerja', 'regional_welfare', 'upah_ratarata_perjam', 'upah_minimum', 'persentase_RT_kumuh_kabkota', 'akses_internet', 'pdrb_adhk', 'nilai_tukar_petani_provinsi', 'nilai_ekspor_kabkota', 'persentase_jalan_desa_roda4_kabkota', 'garis_kemiskinan_kabkota', 'pdrb_adhk_growth', 'kepadatan_sepeda_motor_kabkota', 'jumlah_penduduk_kabkota'],
    'Validasi': ['Perlu analisis lebih lanjut untuk melihat korelasi dengan penjualan', 'Perlu analisis lebih lanjut untuk melihat korelasi dengan penjualan', 'Perlu analisis lebih lanjut untuk melihat korelasi dengan penjualan', 'Perlu analisis lebih lanjut untuk melihat korelasi dengan penjualan', 'Perlu analisis lebih lanjut untuk melihat korelasi dengan penjualan', 'Perlu analisis lebih lanjut untuk melihat korelasi dengan penjualan', 'Perlu analisis lebih lanjut untuk melihat korelasi dengan penjualan', 'Perlu analisis lebih lanjut untuk melihat korelasi dengan penjualan', 'Perlu analisis lebih lanjut untuk melihat korelasi dengan penjualan', 'Perlu analisis lebih lanjut untuk melihat korelasi dengan penjualan', 'Perlu analisis lebih lanjut untuk melihat korelasi dengan penjualan', 'Perlu analisis lebih lanjut untuk melihat korelasi dengan penjualan', 'Perlu analisis lebih lanjut untuk melihat korelasi dengan penjualan', 'Perlu analisis lebih lanjut untuk melihat korelasi dengan penjualan', 'Perlu analisis lebih lanjut untuk melihat korelasi dengan penjualan', 'Perlu analisis lebih lanjut untuk melihat korelasi dengan penjualan']
})
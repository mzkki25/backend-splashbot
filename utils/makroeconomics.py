import pandas as pd
from core.gemini import model

def two_wheels_model(text):
    df = pd.read_csv('dataset/2w_dataset.csv')

    try:
        prompt = f"""
            Kamu adalah asisten data analyst. Tugasmu adalah membuat blok kode Python (bisa lebih dari satu baris, menggunakan pandas dan scikit-learn) 
            untuk menjawab pertanyaan berikut dari DataFrame bernama `df`.

            Kolom DataFrame: {df.columns.tolist()}
            Nama Kota yang ada di DataFrame: {df['kab'].unique().tolist()}
            Nama Provinsi yang ada di DataFrame: {df['prov'].unique().tolist()}
            Distribusi Tahun yang ada di DataFrame: {df['year'].unique().tolist()}
            Distribusi Cluster yang ada di DataFrame: {df['cluster'].unique().tolist()}

            Diketahui data penjualan (data target) adalah `delta_jumlah_sepeda_motor_kabkota` dalam satuan unit.
            Sebagai tambahan, nilai kategorikal hanya ada di kolom `prov`, dan `kab`, selain kolom tersebut merupakan data numerik.
            Kolom cluster adalah nilai numerikal yang dihasilkan dari clustering dengan menggunakan KMeans.

            Pertanyaan: "{text}"

            PENTING:
            Pastikan jawabanmu adalah **blok kode Python tanpa penjelasan tambahan**.
            Jika ada nilai nan pada DataFrame, gunakan metode `fillna()` untuk mengisi nilai tersebut dengan 0.
            Jika hasil akhir bukan merupakan DataFrame, maka tampilkan hasil akhir tersebut dalam bentuk DataFrame.
            Hasil akhirnya **disimpan dalam variabel bernama `final_answer`** agar bisa dievaluasi setelahnya dengan maksimal 5 kolom dan maksimal 10 baris data. 
        """

        response = model.generate_content(contents=prompt).text.replace("```python", "").replace("```", "").strip()

        local_ns = {'df': df}
        exec(response, {}, local_ns)
        answer_the_code = local_ns.get('final_answer').head(10) if 'final_answer' in local_ns else None

        prompt_2 = f"""
            Pertanyaan dari user adalah "{text}".
            Kode yang dihasilkan adalah:\n\n{response}

            Diketahui bahwa hasil jawaban aktualnya adalah {answer_the_code}.
            Analisislah diikuti dengan data dari jawaban aktualnya tanpa perlu menjelaskan algoritmanya sama sekali, fokus pada sisi bisnis saja. 
            Jawaban berupa kesimpulan dari hasil analisis berbentuk poin by poin.
            Bagian yang penting dapat di bold kan.
        """
        explanation = model.generate_content(contents=prompt_2).text.replace("```python", "").replace("```", "").strip()

        formatted_result = ""
        if isinstance(answer_the_code, pd.DataFrame):
            formatted_result += answer_the_code.to_markdown(index=False, tablefmt="github")
        elif isinstance(answer_the_code, pd.Series):
            formatted_result += answer_the_code.to_frame().to_markdown(tablefmt="github")
        elif isinstance(answer_the_code, (list)):
            formatted_result += f"\n{answer_the_code}\n"
        elif isinstance(answer_the_code, (dict)):
            formatted_result += pd.DataFrame(answer_the_code.items(), columns=['Key', 'Value']).to_markdown(index=False, tablefmt="github")
        else:
            formatted_result += str(answer_the_code)

        return f"### Jawaban SPLASHBot:\n{explanation}\n\n---\n{formatted_result}"

    except Exception as e:
        fallback_response = model.generate_content(
            contents=f"""
                Kamu tidak dapat memberikan jawaban spesifik dari:

                Pertanyaan: "{text}"
                Kolom DataFrame: {df.columns.tolist()}
                Nama Kota yang ada di DataFrame: {df['kab'].unique().tolist()}
                Nama Provinsi yang ada di DataFrame: {df['prov'].unique().tolist()}

                Namun, kamu bisa memberikan penjelasan umum tentang data tersebut.
            """
        ).text.replace("```python", "").replace("```", "").strip()

        return f"### Jawaban SPLASHBot:\n{fallback_response}"
    
def four_wheels_model(text):
    answer = "Four wheels model masih dalam tahap pengembangan dan belum tersedia untuk digunakan. Silakan coba lagi nanti."
    return answer
    
def retail_general_model(text):
    answer = "Retail general model masih dalam tahap pengembangan dan belum tersedia untuk digunakan. Silakan coba lagi nanti."
    return answer
    
def retail_beauty_model(text):
    answer = "Retail beauty model masih dalam tahap pengembangan dan belum tersedia untuk digunakan. Silakan coba lagi nanti."
    return answer
    
def retail_fnb_model(text):
    answer = "Retail FnB model masih dalam tahap pengembangan dan belum tersedia untuk digunakan. Silakan coba lagi nanti."
    return answer
    
def retail_drugstore_model(text):
    answer = "Retail drugstore model masih dalam tahap pengembangan dan belum tersedia untuk digunakan. Silakan coba lagi nanti."
    return answer
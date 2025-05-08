import pandas as pd
from core.gemini import model

def two_wheels_model(text):
    df = pd.read_csv('dataset/2w_dataset.csv')

    try:
        prompt = f"""
            Kamu adalah **SPLASHBot**, sebuah AI Agent yang bertugas membuat **blok kode Python** untuk menjawab pertanyaan berbasis data menggunakan **pandas** dan **scikit-learn**.

            ### Data yang Disediakan:
            - Nama DataFrame: `df`
            - Kolom: {df.columns.tolist()}
            - Kota (`kab`): {df['kab'].unique().tolist()}
            - Provinsi (`prov`): {df['prov'].unique().tolist()}
            - Tahun (`year`): {df['year'].unique().tolist()}
            - Cluster (`cluster`): {df['cluster'].unique().tolist()}
            - Target variabel (penjualan): `delta_jumlah_sepeda_motor_kabkota` (dalam satuan unit)

            ### Informasi Penting:
            - Nilai kategorikal hanya terdapat pada kolom `prov` dan `kab`
            - Semua kolom lainnya adalah numerik
            - Kolom `cluster` adalah hasil KMeans (numerik)
            - Jika ada nilai NaN, isi menggunakan `fillna(0)`
            - Jika hasil akhir **bukan DataFrame**, ubah ke bentuk DataFrame
            - Hasil akhir harus disimpan ke dalam variabel bernama **`final_answer`**
            - Batasi hasil akhir: maksimal **5 kolom** dan **10 baris**
            - **Tidak perlu menambahkan penjelasan apapun**—**hanya blok kode Python**

            ### Pertanyaan dari Pengguna:
            **"{text}"**

            ### Tugas Anda:
            Buat dan tampilkan **blok kode Python** untuk menjawab pertanyaan tersebut, sesuai instruksi di atas.
        """

        response = model.generate_content(contents=prompt).text.replace("```python", "").replace("```", "").strip()
        print(response)

        local_ns = {'df': df}
        exec(response, {}, local_ns)
        answer_the_code = local_ns.get('final_answer').head(10) if 'final_answer' in local_ns else None

        prompt_2 = f"""
            ### Konteks:
            Pengguna mengajukan pertanyaan berikut:  
            **"{text}"**

            Model menghasilkan kode sebagai respons:  
            {response}

            Setelah kode dijalankan, diperoleh hasil output aktual sebagai berikut:  
            {answer_the_code}

            ### Tugas Anda:
            Lakukan **analisis terhadap hasil aktual tersebut** dengan **fokus pada sisi bisnis** (bukan teknis atau algoritmik).  
            **Jangan menjelaskan logika atau algoritma kode**. Soroti **implikasi bisnis, insight, dan dampak nyata** dari hasil tersebut.

            ### Format Jawaban:
            - Berikan jawaban dalam bentuk **poin-poin ringkas dan padat**.
            - Soroti hal-hal yang **penting dengan cetak tebal (bold)**.
            - Fokus pada **kesimpulan dan dampak bisnis** dari hasil tersebut.

            Jika hasil aktual tidak mengandung informasi bermakna secara bisnis, sampaikan hal itu secara ringkas dan profesional.
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

        return f"### SPLASHBot Tidak Dapat Menjawab:\n{fallback_response}"
    
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
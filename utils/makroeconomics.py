import pandas as pd
import re
import uuid
import os
import time
import ast

from utils.preprocessing import clean_code, save_code, read_clean_python_file
from core.gemini import model


from core.logging_logger import setup_logger
logger = setup_logger(__name__)

def two_wheels_model(text):
    df = pd.read_csv('dataset/fix_2w.csv')

    try:
        prompt = f"""
            Kamu adalah **SPLASHBot**, sebuah AI Agent yang bertugas membuat **blok kode Python** untuk menjawab pertanyaan berbasis data 2 wheels menggunakan **pandas**.

            ### Konteks Dataset:
            - Dataset: `df = pd.read_csv('dataset/fix_2w.csv')` (sudah di-load sebelumnya)
            - Kolom: {df.columns.tolist()}
            - Provinsi (`prov`): {df['prov'].unique().tolist()}
            - Kota (`kab`): {df['kab'].unique().tolist()}
            - Tahun (`year`): {df['year'].unique().tolist()}
            - Target utama: `penjualan` (unit)
            - Prediksi: `prediksi` (unit)
            - Kolom numerik: Semua selain `prov`, `kab` (termasuk `cluster` hasil KMeans)
            - Data NaN harus diisi dengan `fillna(0)`
            - **Hasil akhir harus disimpan ke variabel bernama `final_answer`**

            ### Aturan Wajib:
            1. Jawaban hanya boleh berupa **blok kode Python**, tanpa penjelasan atau komentar apapun.
            2. Jika **pertanyaan TIDAK RELEVAN atau TIDAK DAPAT dijawab** menggunakan dataset tersebut, tampilkan:
            `raise ValueError("Pertanyaan tidak dapat dijawab")`
            3. Jika **pertanyaan DAPAT dijawab**, maka:
            - Gunakan `pandas` untuk manipulasi datanya.
            - Simpan hasil akhir dalam `final_answer` (dalam bentuk DataFrame).
            4. Jangan buat asumsi atau interpolasi data yang tidak ada di dataset.
            5. Jangan mencetak apapun, hanya deklarasi kode.

            ### Pertanyaan dari Pengguna:
            **"{text}"**

            ### Tugas Anda:
            Tulis blok kode Python yang valid dan sesuai dengan instruksi di atas.
        """

        generated_code = model.generate_content(contents=prompt).text
        generated_code = clean_code(generated_code)

        uid = str(uuid.uuid4())
        save_code(generated_code, f"utils/_generated_code_{uid}.py")
        
        filepath = f"utils/_generated_code_{uid}.py"
        generated_code = read_clean_python_file(filepath)

        logger.info(f"Generated code: {generated_code}")

        local_ns = {'df': df}
        exec(generated_code, {}, local_ns)
        answer_the_code = local_ns.get('final_answer') if 'final_answer' in local_ns else None

        time.sleep(0.03)

        for file in os.listdir("utils"):
            if file.startswith("_generated_code_"):
                os.remove(os.path.join("utils", file))

        prompt_2 = f"""
            ### Konteks:

            Model menghasilkan kode sebagai respons:  
            {generated_code}

            Setelah kode dijalankan, diperoleh hasil output aktual sebagai berikut:  
            {answer_the_code}

            Pengguna mengajukan pertanyaan berikut:  
            **"{text}"**

            ### Konteks Dataset:
            - Fitur: {df.columns.tolist()}
            - Target utama: `penjualan` (unit) -> tidak null untuk tahun 2020 sd 2023 dan null untuk tahun 2024 dan 2025 (karena tahun 2024 dan 2025 adalah data yang hanya ada di `prediksi`)
            - Prediksi: `prediksi` (unit) -> tidak null untuk tahun 2020 sd 2025
            - Error Value: `error_value` -> nilai error dari model yang dilatih sebelumnya -> tidak null untuk tahun 2020 sd 2023 dan null untuk tahun 2024 dan 2025 (karena tahun 2024 dan 2025 adalah data yang hanya ada di `prediksi`)
            - Absolute Percentage Error: `APE` -> selisih dari `prediksi` dan `penjualan` (unit) dibagi `penjualan` (unit) -> tidak null untuk tahun 2020 sd 2023 dan null untuk tahun 2024 dan 2025 (karena tahun 2024 dan 2025 adalah data yang hanya ada di `prediksi`)
            - Kolom numerik: Semua selain `prov`, `kab` (termasuk `cluster` hasil KMeans)

            ### Tugas Anda:
            - Lakukan **analisis terhadap hasil aktual tersebut** dengan **fokus pada sisi bisnis** (bukan teknis atau algoritmik).  
            - **Jangan menjelaskan logika atau algoritma kode**. Soroti **implikasi bisnis, insight, dan dampak nyata** dari hasil tersebut.

            ### Format Jawaban:
            - Berikan jawaban dalam bentuk **poin-poin ringkas dan padat**.
            - Soroti hal-hal yang **penting dengan cetak tebal (bold)**.
            - Fokus pada **kesimpulan dan dampak bisnis** dari hasil tersebut.
            - Berikan **saran atau rekomendasi** jika relevan.

            Jika hasil aktual tidak mengandung informasi bermakna secara bisnis, sampaikan hal itu secara ringkas dan profesional.
        """
        explanation = model.generate_content(contents=prompt_2).text.replace("```python", "").replace("```", "").strip()

        formatted_result = ""
        if isinstance(answer_the_code, pd.DataFrame):
            formatted_result += answer_the_code.head(10).to_markdown(index=False, tablefmt="github")
        elif isinstance(answer_the_code, pd.Series):
            formatted_result += answer_the_code.head(10).to_frame().to_markdown(tablefmt="github")
        elif isinstance(answer_the_code, (list)):
            formatted_result += f"\n{answer_the_code.head(10)}\n"
        elif isinstance(answer_the_code, (dict)):
            formatted_result += pd.DataFrame(answer_the_code.head(10).items(), columns=['Key', 'Value']).to_markdown(index=False, tablefmt="github")
        else:
            formatted_result += str(answer_the_code)

        return f"### Ringkasan Temuan SPLASHBot 🤖:\n{explanation}\n\n---\n{formatted_result}"

    except Exception as e:
        logger.error(f"Error in two_wheels_model: {e}")

        for file in os.listdir("utils"):
            if file.startswith("_generated_code_"):
                os.remove(os.path.join("utils", file))

        fallback_response = model.generate_content(
            contents=f"""
                Kamu tidak dapat memberikan jawaban spesifik dari:

                Pertanyaan: "{text}"
                Kolom DataFrame: {df.columns.tolist()}
                Nama Kota yang ada di DataFrame: {df['kab'].unique().tolist()}
                Nama Provinsi yang ada di DataFrame: {df['prov'].unique().tolist()}

                Namun, kamu bisa memberikan penjelasan/jawaban umum tentang pertanyaan tersebut.
            """
        ).text.replace("```python", "").replace("```", "").strip()

        return f"### Maaf, SPLASHBot Belum Dapat Menjawab 😢:\n{fallback_response}"   
     
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
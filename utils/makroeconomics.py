import pandas as pd
from core.gemini import model

def two_wheels_model(text):
    df = pd.read_csv('dataset/2w_dataset.csv')

    try:
        prompt = f"""
            Kamu adalah asisten data analyst. Tugasmu adalah membuat satu baris kode Python (menggunakan pandas) 
            untuk menjawab pertanyaan berikut dari DataFrame bernama `df`.

            Kolom DataFrame: {df.columns.tolist()}
            Nama Kota yang ada di DataFrame: {df['kab'].unique().tolist()}
            Nama Provinsi yang ada di DataFrame: {df['prov'].unique().tolist()}
            Distribusi Tahun yang ada di DataFrame: {df['year'].unique().tolist()}
            Distribusi Cluster yang ada di DataFrame: {df['cluster'].unique().tolist()}

            Diketahui data penjualan (data target) adalah `delta_jumlah_sepeda_motor_kabkota` dalam satuan unit
            Sebagai tambahan, nilai kategorikal hanya ada di kolom `prov`, dan `kab`, selain kolom tersebut merupakan data numerik.
            Kolom cluster adalah nilai numerikal yang dihasilkan dari clustering dengan menggunakan KMeans

            Pertanyaan: "{text}"

            Pastikan hanya kembalikan satu baris kode Python yang akan memberikan jawaban berupa 
            numerik atau string atau list/list comprehension atau dictionary/dictionary comprehension atau DataFrame. tanpa penjelasan tambahan.
        """

        response = model.generate_content(
            contents=prompt
        ).text.replace("```python", "").replace("```", "").strip()

        answer_the_code = eval(response)

        prompt_2 = f"""
            Pertanyaan dari user adalah "{text}".
            Kode yang dihasilkan adalah: {response}

            Diketahui bahwa hasil jawaban aktualnya adalah {answer_the_code}.
            Analisislah diikuti dengan data dari jawaban aktualnya tanpa perlu memention baris kodenya sama sekali
        """

        answer = model.generate_content(
            contents=prompt_2
        ).text.replace("```python", "").replace("```", "").strip()

        return f"## Jawaban SPLASHBot: \n {answer_the_code} \n\n ## Penjelasan SPLASHBot: \n {answer}"
    
    except Exception as e:
        response = model.generate_content(
            contents=f"""
                Kamu tidak dapat memberikan jawaban spesifik dari:

                Pertanyaan: "{text}"
                Kolom DataFrame: {df.columns.tolist()}
                Nama Kota yang ada di DataFrame: {df['kab'].unique().tolist()}
                Nama Provinsi yang ada di DataFrame: {df['prov'].unique().tolist()}

                Namun, kamu bisa memberikan penjelasan umum tentang data tersebut.
            """
        ).text.replace("```python", "").replace("```", "").strip()

        answer = response
        return answer
    
def four_wheels_model(text):
    df = pd.read_csv('dataset/2w_dataset.csv')

    try:
        prompt = f"""
            Kamu adalah asisten data analyst. Tugasmu adalah membuat satu baris kode Python (menggunakan pandas) 
            untuk menjawab pertanyaan berikut dari DataFrame bernama `df`.

            Kolom DataFrame: {df.columns.tolist()}
            Nama Kota yang ada di DataFrame: {df['kab'].unique().tolist()}
            Nama Provinsi yang ada di DataFrame: {df['prov'].unique().tolist()}
            Distribusi Tahun yang ada di DataFrame: {df['year'].unique().tolist()}
            Distribusi Cluster yang ada di DataFrame: {df['cluster'].unique().tolist()}

            Diketahui data penjualan (data target) adalah `delta_jumlah_sepeda_motor_kabkota` dalam satuan unit
            Sebagai tambahan, nilai kategorikal hanya ada di kolom `prov`, dan `kab`, selain kolom tersebut merupakan data numerik.
            Kolom cluster adalah nilai numerikal yang dihasilkan dari clustering dengan menggunakan KMeans

            Pertanyaan: "{text}"

            Pastikan hanya kembalikan satu baris kode Python yang akan memberikan jawaban berupa 
            numerik atau string atau list/list comprehension atau dictionary/dictionary comprehension atau DataFrame. tanpa penjelasan tambahan.
        """

        response = model.generate_content(
            contents=prompt
        ).text.replace("```python", "").replace("```", "").strip()

        answer_the_code = eval(response)

        prompt_2 = f"""
            Pertanyaan dari user adalah "{text}".
            Kode yang dihasilkan adalah: {response}

            Diketahui bahwa hasil jawaban aktualnya adalah {answer_the_code}.
            Analisislah diikuti dengan data dari jawaban aktualnya tanpa perlu memention baris kodenya sama sekali
        """

        answer = model.generate_content(
            contents=prompt_2
        ).text.replace("```python", "").replace("```", "").strip()

        return f"# Jawaban SPLASHBot: {answer_the_code} \n\n # Penjelasan SPLASHBot: {answer}"
    
    except Exception as e:
        response = model.generate_content(
            contents=f"""
                Kamu tidak dapat memberikan jawaban spesifik dari:

                Pertanyaan: "{text}"
                Kolom DataFrame: {df.columns.tolist()}
                Nama Kota yang ada di DataFrame: {df['kab'].unique().tolist()}
                Nama Provinsi yang ada di DataFrame: {df['prov'].unique().tolist()}

                Namun, kamu bisa memberikan penjelasan umum tentang data tersebut.
            """
        ).text.replace("```python", "").replace("```", "").strip()

        answer = response
        return answer
    
def retail_general_model(text):
    df = pd.read_csv('dataset/2w_dataset.csv')

    try:
        prompt = f"""
            Kamu adalah asisten data analyst. Tugasmu adalah membuat satu baris kode Python (menggunakan pandas) 
            untuk menjawab pertanyaan berikut dari DataFrame bernama `df`.

            Kolom DataFrame: {df.columns.tolist()}
            Nama Kota yang ada di DataFrame: {df['kab'].unique().tolist()}
            Nama Provinsi yang ada di DataFrame: {df['prov'].unique().tolist()}
            Distribusi Tahun yang ada di DataFrame: {df['year'].unique().tolist()}
            Distribusi Cluster yang ada di DataFrame: {df['cluster'].unique().tolist()}

            Diketahui data penjualan (data target) adalah `delta_jumlah_sepeda_motor_kabkota` dalam satuan unit
            Sebagai tambahan, nilai kategorikal hanya ada di kolom `prov`, dan `kab`, selain kolom tersebut merupakan data numerik.
            Kolom cluster adalah nilai numerikal yang dihasilkan dari clustering dengan menggunakan KMeans

            Pertanyaan: "{text}"

            Pastikan hanya kembalikan satu baris kode Python yang akan memberikan jawaban berupa 
            numerik atau string atau list/list comprehension atau dictionary/dictionary comprehension atau DataFrame. tanpa penjelasan tambahan.
        """

        response = model.generate_content(
            contents=prompt
        ).text.replace("```python", "").replace("```", "").strip()

        answer_the_code = eval(response)

        prompt_2 = f"""
            Pertanyaan dari user adalah "{text}".
            Kode yang dihasilkan adalah: {response}

            Diketahui bahwa hasil jawaban aktualnya adalah {answer_the_code}.
            Analisislah diikuti dengan data dari jawaban aktualnya tanpa perlu memention baris kodenya sama sekali
        """

        answer = model.generate_content(
            contents=prompt_2
        ).text.replace("```python", "").replace("```", "").strip()

        return f"# Jawaban SPLASHBot: {answer_the_code} \n\n # Penjelasan SPLASHBot: {answer}"
    
    except Exception as e:
        response = model.generate_content(
            contents=f"""
                Kamu tidak dapat memberikan jawaban spesifik dari:

                Pertanyaan: "{text}"
                Kolom DataFrame: {df.columns.tolist()}
                Nama Kota yang ada di DataFrame: {df['kab'].unique().tolist()}
                Nama Provinsi yang ada di DataFrame: {df['prov'].unique().tolist()}

                Namun, kamu bisa memberikan penjelasan umum tentang data tersebut.
            """
        ).text.replace("```python", "").replace("```", "").strip()

        answer = response
        return answer
    
def retail_beauty_model(text):
    df = pd.read_csv('dataset/2w_dataset.csv')

    try:
        prompt = f"""
            Kamu adalah asisten data analyst. Tugasmu adalah membuat satu baris kode Python (menggunakan pandas) 
            untuk menjawab pertanyaan berikut dari DataFrame bernama `df`.

            Kolom DataFrame: {df.columns.tolist()}
            Nama Kota yang ada di DataFrame: {df['kab'].unique().tolist()}
            Nama Provinsi yang ada di DataFrame: {df['prov'].unique().tolist()}
            Distribusi Tahun yang ada di DataFrame: {df['year'].unique().tolist()}
            Distribusi Cluster yang ada di DataFrame: {df['cluster'].unique().tolist()}

            Diketahui data penjualan (data target) adalah `delta_jumlah_sepeda_motor_kabkota` dalam satuan unit
            Sebagai tambahan, nilai kategorikal hanya ada di kolom `prov`, dan `kab`, selain kolom tersebut merupakan data numerik.
            Kolom cluster adalah nilai numerikal yang dihasilkan dari clustering dengan menggunakan KMeans

            Pertanyaan: "{text}"

            Pastikan hanya kembalikan satu baris kode Python yang akan memberikan jawaban berupa 
            numerik atau string atau list/list comprehension atau dictionary/dictionary comprehension atau DataFrame. tanpa penjelasan tambahan.
        """

        response = model.generate_content(
            contents=prompt
        ).text.replace("```python", "").replace("```", "").strip()

        answer_the_code = eval(response)

        prompt_2 = f"""
            Pertanyaan dari user adalah "{text}".
            Kode yang dihasilkan adalah: {response}

            Diketahui bahwa hasil jawaban aktualnya adalah {answer_the_code}.
            Analisislah diikuti dengan data dari jawaban aktualnya tanpa perlu memention baris kodenya sama sekali
        """

        answer = model.generate_content(
            contents=prompt_2
        ).text.replace("```python", "").replace("```", "").strip()

        return f"# Jawaban SPLASHBot: {answer_the_code} \n\n # Penjelasan SPLASHBot: {answer}"
    
    except Exception as e:
        response = model.generate_content(
            contents=f"""
                Kamu tidak dapat memberikan jawaban spesifik dari:

                Pertanyaan: "{text}"
                Kolom DataFrame: {df.columns.tolist()}
                Nama Kota yang ada di DataFrame: {df['kab'].unique().tolist()}
                Nama Provinsi yang ada di DataFrame: {df['prov'].unique().tolist()}

                Namun, kamu bisa memberikan penjelasan umum tentang data tersebut.
            """
        ).text.replace("```python", "").replace("```", "").strip()

        answer = response
        return answer
    
def retail_fnb_model(text):
    df = pd.read_csv('dataset/2w_dataset.csv')

    try:
        prompt = f"""
            Kamu adalah asisten data analyst. Tugasmu adalah membuat satu baris kode Python (menggunakan pandas) 
            untuk menjawab pertanyaan berikut dari DataFrame bernama `df`.

            Kolom DataFrame: {df.columns.tolist()}
            Nama Kota yang ada di DataFrame: {df['kab'].unique().tolist()}
            Nama Provinsi yang ada di DataFrame: {df['prov'].unique().tolist()}
            Distribusi Tahun yang ada di DataFrame: {df['year'].unique().tolist()}
            Distribusi Cluster yang ada di DataFrame: {df['cluster'].unique().tolist()}

            Diketahui data penjualan (data target) adalah `delta_jumlah_sepeda_motor_kabkota` dalam satuan unit
            Sebagai tambahan, nilai kategorikal hanya ada di kolom `prov`, dan `kab`, selain kolom tersebut merupakan data numerik.
            Kolom cluster adalah nilai numerikal yang dihasilkan dari clustering dengan menggunakan KMeans

            Pertanyaan: "{text}"

            Pastikan hanya kembalikan satu baris kode Python yang akan memberikan jawaban berupa 
            numerik atau string atau list/list comprehension atau dictionary/dictionary comprehension atau DataFrame. tanpa penjelasan tambahan.
        """

        response = model.generate_content(
            contents=prompt
        ).text.replace("```python", "").replace("```", "").strip()

        answer_the_code = eval(response)

        prompt_2 = f"""
            Pertanyaan dari user adalah "{text}".
            Kode yang dihasilkan adalah: {response}

            Diketahui bahwa hasil jawaban aktualnya adalah {answer_the_code}.
            Analisislah diikuti dengan data dari jawaban aktualnya tanpa perlu memention baris kodenya sama sekali
        """

        answer = model.generate_content(
            contents=prompt_2
        ).text.replace("```python", "").replace("```", "").strip()

        return f"# Jawaban SPLASHBot: {answer_the_code} \n\n # Penjelasan SPLASHBot: {answer}"
    
    except Exception as e:
        response = model.generate_content(
            contents=f"""
                Kamu tidak dapat memberikan jawaban spesifik dari:

                Pertanyaan: "{text}"
                Kolom DataFrame: {df.columns.tolist()}
                Nama Kota yang ada di DataFrame: {df['kab'].unique().tolist()}
                Nama Provinsi yang ada di DataFrame: {df['prov'].unique().tolist()}

                Namun, kamu bisa memberikan penjelasan umum tentang data tersebut.
            """
        ).text.replace("```python", "").replace("```", "").strip()

        answer = response
        return answer
    
def retail_drugstore_model(text):
    df = pd.read_csv('dataset/2w_dataset.csv')

    try:
        prompt = f"""
            Kamu adalah asisten data analyst. Tugasmu adalah membuat satu baris kode Python (menggunakan pandas) 
            untuk menjawab pertanyaan berikut dari DataFrame bernama `df`.

            Kolom DataFrame: {df.columns.tolist()}
            Nama Kota yang ada di DataFrame: {df['kab'].unique().tolist()}
            Nama Provinsi yang ada di DataFrame: {df['prov'].unique().tolist()}
            Distribusi Tahun yang ada di DataFrame: {df['year'].unique().tolist()}
            Distribusi Cluster yang ada di DataFrame: {df['cluster'].unique().tolist()}

            Diketahui data penjualan (data target) adalah `delta_jumlah_sepeda_motor_kabkota` dalam satuan unit
            Sebagai tambahan, nilai kategorikal hanya ada di kolom `prov`, dan `kab`, selain kolom tersebut merupakan data numerik.
            Kolom cluster adalah nilai numerikal yang dihasilkan dari clustering dengan menggunakan KMeans

            Pertanyaan: "{text}"

            Pastikan hanya kembalikan satu baris kode Python yang akan memberikan jawaban berupa 
            numerik atau string atau list/list comprehension atau dictionary/dictionary comprehension atau DataFrame. tanpa penjelasan tambahan.
        """

        response = model.generate_content(
            contents=prompt
        ).text.replace("```python", "").replace("```", "").strip()

        answer_the_code = eval(response)

        prompt_2 = f"""
            Pertanyaan dari user adalah "{text}".
            Kode yang dihasilkan adalah: {response}

            Diketahui bahwa hasil jawaban aktualnya adalah {answer_the_code}.
            Analisislah diikuti dengan data dari jawaban aktualnya tanpa perlu memention baris kodenya sama sekali
        """

        answer = model.generate_content(
            contents=prompt_2
        ).text.replace("```python", "").replace("```", "").strip()

        return f"# Jawaban SPLASHBot: {answer_the_code} \n\n # Penjelasan SPLASHBot: {answer}"
    
    except Exception as e:
        response = model.generate_content(
            contents=f"""
                Kamu tidak dapat memberikan jawaban spesifik dari:

                Pertanyaan: "{text}"
                Kolom DataFrame: {df.columns.tolist()}
                Nama Kota yang ada di DataFrame: {df['kab'].unique().tolist()}
                Nama Provinsi yang ada di DataFrame: {df['prov'].unique().tolist()}

                Namun, kamu bisa memberikan penjelasan umum tentang data tersebut.
            """
        ).text.replace("```python", "").replace("```", "").strip()

        answer = response
        return answer
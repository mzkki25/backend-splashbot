from core.gemini import model
from utils.preprocessing import clean_python_list

import numpy as np
import pandas as pd

from core.logging_logger import setup_logger
logger = setup_logger(__name__)

def recommend_follow_up_questions_gm(prompt, response, file_id_input=None):
    try:
        if file_id_input:
            return []
        else:
            prompt = f"""
                Kamu adalah **SPLASHBot**, sebuah AI Agent yang ahli dalam menjawab pertanyaan seputar **ekonomi**, termasuk ekonomi makro, mikro, kebijakan fiskal/moneter, perdagangan, keuangan, dan indikator ekonomi.

                Diberikan sebuah pertanyaan awal dari pengguna berikut:

                "{prompt}"

                dan jawaban yang sudah diberikan oleh sistem:

                "{response}"

                Buatlah hingga 5 pertanyaan lanjutan yang singkat, relevan, profesional, dan bersifat eksploratif yang berkaitan dengan **ekonomi** untuk membantu pengguna memahami topik ini lebih lanjut. 
                Berikan hasil dalam format list Python (satu pertanyaan per elemen).
                Contoh format:
                [
                    "Pertanyaan lanjutan 1?",
                    "Pertanyaan lanjutan 2?",
                    ...
                ]
            """.strip()

            response = eval(model.generate_content(contents=prompt).text.replace("```python", "").replace("```", "").strip())

            num_questions = np.random.randint(1, 6)

            if len(response) > num_questions:
                response = np.random.choice(response, num_questions, replace=False).tolist()

            return response
        
    except Exception as e:
        logger.error(f"Error generating follow-up questions General Macroeconomics: {e}")
        return []
    
def recommend_follow_up_questions_ngm(prompt, response, chat_option):
    if chat_option == "2 Wheels":
        try:
            df = pd.read_csv('dataset/fix_2w.csv')

            prompt = f"""
                Kamu adalah **SPLASHBot**, sebuah AI Agent yang ahli dalam menjawab pertanyaan seputar **ekonomi**, termasuk ekonomi makro, mikro, kebijakan fiskal/moneter, perdagangan, keuangan, dan indikator ekonomi.

                ### Diketahui Data yang Disediakan (Kolom Kategorikal):
                - Kolom: {df.columns.tolist()} 

                - Kota (`kab`): {df['kab'].unique().tolist()}
                - Provinsi (`prov`): {df['prov'].unique().tolist()}
                - Tahun (`year`): {df['year'].unique().tolist()}
                - Target variabel (penjualan): `penjualan` (dalam satuan unit)
                - Target prediksi: `prediksi` (dalam satuan unit)

                Data diatas adalah data penjualan sepeda motor di Indonesia. Data ini berisi informasi tentang penjualan sepeda motor berdasarkan tahun, provinsi, dan kabupaten/kota.

                Diberikan sebuah pertanyaan awal dari pengguna berikut:

                "{prompt}"

                dan jawaban yang sudah diberikan oleh sistem:

                "{response}"

                ### Tugasmu adalah: 
                - Buatlah hingga 5 pertanyaan lanjutan yang singkat, relevan, profesional, dan bersifat eksploratif untuk membantu pengguna memahami topik ini lebih lanjut
                - Pertanyaan lanjutan harus **berkaitan dengan data yang tersedia**. 
                - Berikan hasil dalam format list Python (satu pertanyaan per elemen).

                Contoh format:
                [
                    "Pertanyaan lanjutan 1?",
                    "Pertanyaan lanjutan 2?",
                    ...
                ]
            """.strip()

            response = eval(model.generate_content(contents=prompt).text.replace("```python", "").replace("```", "").strip())
            logger.info(f"Response: {response}")
            response = clean_python_list(response)

            num_questions = np.random.randint(1, 6)

            if len(response) > num_questions:
                response = np.random.choice(response, num_questions, replace=False).tolist()

            return response
        
        except Exception as e:
            logger.error(f"Error generating follow-up questions for 2 Wheels: {e}")
            return []
    
    elif chat_option == "4 Wheels":
        return []
    elif chat_option == "Retail General":
        return []
    elif chat_option == "Retail Beauty":
        return []
    elif chat_option == "Retail FnB":
        return []
    elif chat_option == "Retail Drugstore":
        return []
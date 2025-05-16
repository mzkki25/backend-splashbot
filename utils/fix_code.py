import re
import ast

def clean_code_1(code: str) -> str:
    code = re.sub(r"(?s).*?```python(.*?)```", r"\1", code) if '```python' in code else code
    code = code.encode('utf-8', errors='ignore').decode('utf-8')  
    code = re.sub(r'[\u200b\u200e\u200f\ufeff\u00a0\u00ad]', '', code)  
    code = code.replace('\r\n', '\n').strip()  
    return code

def clean_code_2(code: str) -> str:
    if 'python' in code:
        code = re.sub(r"(?s).*?python(.*?)```", r"\1", code)
    
    invisible_chars = [
        '\u200b', # zero width space
        '\u200c', # zero width non-joiner
        '\u200d', # zero width joiner
        '\u200e', # left-to-right mark
        '\u200f', # right-to-left mark
        '\ufeff', # zero width no-break space (BOM)
        '\u00a0', # non-breaking space
        '\u00ad', # soft hyphen
        '\u202a', # left-to-right embedding
        '\u202b', # right-to-left embedding
        '\u202c', # pop directional formatting
        '\u202d', # left-to-right override
        '\u202e', # right-to-left override
    ]
    
    for ch in invisible_chars:
        code = code.replace(ch, '')
    
    code = ''.join(c for c in code if c.isprintable() or c in ['\n', '\t'])
    
    code = code.replace('\r\n', '\n').replace('\r', '\n')
    code = code.strip()
    
    return code

def clean_python_list(list_str) -> list:
    if isinstance(list_str, list):
        return list_str

    if '```python' in list_str:
        list_str = re.sub(r"(?s).*?```python(.*?)```", r"\1", list_str)
    elif 'python' in list_str:
        list_str = re.sub(r"(?s).*?python(.*?)```", r"\1", list_str)

    list_str = re.sub(r"[\u200b\u200e\u200f\ufeff\u00a0\u00ad]", '', list_str)
    list_str = list_str.encode('utf-8', errors='ignore').decode('utf-8').strip()

    try:
        parsed = ast.literal_eval(list_str)
        if not isinstance(parsed, list):
            raise ValueError("Hasil bukan list")
        return parsed

    except Exception as e:
        raise ValueError(f"List tidak valid: {e}")

def save_code(code: str, filename: str):
    with open(filename, 'w') as f:
        f.write(code)
    print(f"Code saved to {filename}")

def read_clean_python_file(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            code = f.read()

        code = code.replace('\r\n', '\n').strip()
        ast.parse(code)
        code = code.encode('utf-8', errors='ignore').decode('utf-8')

        return code

    except SyntaxError as e:
        raise SyntaxError(f"File Python tidak valid: {e}")

    except Exception as e:
        raise RuntimeError(f"Gagal membaca file: {e}")
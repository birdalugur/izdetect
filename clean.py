import re
import sys
import os

def extract_function_blocks(code):
    pattern = re.compile(r'(const\s+\w+\s*=\s*(?:async\s+)?\([^)]*\)\s*=>\s*)\{')
    result = []
    pos = 0

    while True:
        match = pattern.search(code, pos)
        if not match:
            break

        header_start = match.start(1)
        body_start = match.end(0)  # hemen { sonrası

        brace_count = 1
        i = body_start

        while i < len(code):
            if code[i] == '{':
                brace_count += 1
            elif code[i] == '}':
                brace_count -= 1
                if brace_count == 0:
                    break
            i += 1

        if brace_count == 0:
            full_block = code[match.start():i+1]
            cleaned_block = f"{match.group(1)}{{}}"
            result.append((full_block, cleaned_block))
            pos = i
        else:
            # Parantez dengesi bozulmuşsa, çık
            break

    return result

def clean_svelte_code(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        code = file.read()

    # 1. class="" temizle
    code = re.sub(r'class\s*=\s*"[^"]*"', '', code)

    # 2. Arrow fonksiyon bloklarını bulup temizle
    function_blocks = extract_function_blocks(code)
    for original, cleaned in function_blocks:
        code = code.replace(original, cleaned)

    # 3. Temiz kodu "clean" klasörüne kaydet
    clean_dir = "clean"
    os.makedirs(clean_dir, exist_ok=True)
    clean_file_path = os.path.join(clean_dir, os.path.basename(file_path))
    with open(clean_file_path, 'w', encoding='utf-8') as file:
        file.write(code)

    print(f"Temizlenmiş dosya: {clean_file_path}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Kullanım: python script.py <dosya_yolu>")
        sys.exit(1)

    svelte_file = sys.argv[1]
    clean_svelte_code(svelte_file)

import re
import sys

def remove_comments_from_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        code = f.read()

    # 删除 """ 多行注释 """
    code = re.sub(r'("""|\'\'\')[\s\S]*?\1', '', code)

    # 删除整行 # 注释
    code = re.sub(r'^\s*#.*$', '', code, flags=re.MULTILINE)

    # 删除行尾注释（保留代码）
    code = re.sub(r'([^\n#]*?)\s+#.*$', r'\1', code)

    # 删除多余空行（可选）
    code = re.sub(r'\n{3,}', '\n\n', code)

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(code)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python clean_comments.py <filename>")
    else:
        remove_comments_from_file(sys.argv[1])

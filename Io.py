import json

def load_file(file_name):
    with open(file_name, 'r', encoding="utf-8") as f:
        return json.load(f)
        
def write_file(file_name, content):
    with open(file_name, 'w', encoding="utf-8") as f:
        json.dump(content, f, ensure_ascii=False, indent=4)
import os
import json

def count_lines(path):
    categories = {
        'Python (后端业务逻辑)': 0,
        'Python (单元测试)': 0,
        'TypeScript/React (前端)': 0,
        '配置与样式 (JSON, CSS, HTML)': 0,
        'Markdown (文档)': 0
    }

    for root, dirs, files in os.walk(path):
        if any(ignored in root.replace(chr(92), '/') for ignored in ['/venv', '/node_modules', '/.git', '/__pycache__', '/dist', '/.pytest_cache']):
            continue
        for file in files:
            ext = os.path.splitext(file)[1]
            if ext not in ['.py', '.ts', '.tsx', '.md', '.json', '.css', '.html']:
                continue

            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    lines = len(f.readlines())

                # Classify
                if ext == '.py':
                    if 'tests' in root.replace(chr(92), '/'):
                        categories['Python (单元测试)'] += lines
                    else:
                        categories['Python (后端业务逻辑)'] += lines
                elif ext in ['.ts', '.tsx']:
                    categories['TypeScript/React (前端)'] += lines
                elif ext == '.md':
                    categories['Markdown (文档)'] += lines
                elif ext in ['.json', '.css', '.html']:
                    categories['配置与样式 (JSON, CSS, HTML)'] += lines
            except:
                pass

    with open('stats.json', 'w', encoding='utf-8') as f:
        json.dump(categories, f, indent=2, ensure_ascii=False)

count_lines('.')

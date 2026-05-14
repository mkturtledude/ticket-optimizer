import os
import json

def minimize_json(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if 'tour' in data and 'Cups' in data['tour']:
            minimized_data = {
                "tour": {
                    "Cups": data['tour']['Cups']
                }
            }
            with open(file_path, 'w', encoding='utf-8') as f:
                # Use separators to remove whitespace for maximum space saving
                json.dump(minimized_data, f, separators=(',', ':'))
            print(f"Minimized {file_path}")
        else:
            print(f"Skipped {file_path} (structure not recognized)")
    except Exception as e:
        print(f"Error processing {file_path}: {e}")

def main():
    base_dir = os.path.join('data', 'pastTours')
    if not os.path.exists(base_dir):
        print(f"Directory {base_dir} not found.")
        return

    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.json'):
                minimize_json(os.path.join(root, file))

if __name__ == "__main__":
    main()

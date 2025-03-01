import os
print(os.path)
file_path = os.path.join(os.getcwd(), 'crawler', 'tgdd_crawler', 'tgdd_crawler', 'metadata.json')
if os.path.exists(file_path):
    print(f"Tệp {file_path} tồn tại.")
else:
    print(f"Tệp {file_path} không tồn tại.")

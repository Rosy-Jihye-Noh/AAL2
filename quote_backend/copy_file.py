# -*- coding: utf-8 -*-
import shutil
import sys
sys.stdout.reconfigure(encoding='utf-8')

src = r"c:\Users\cjw09\OneDrive - 주식회사 아로아랩스\Desktop\Untitled-1.html"
dst = r"D:\Planning_data\AAL\AAL\frontend\pages\quotation.html"

try:
    shutil.copy2(src, dst)
    print(f"[OK] File copied successfully!")
    print(f"Source: {src}")
    print(f"Destination: {dst}")
except Exception as e:
    print(f"[ERROR] {e}")


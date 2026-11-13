STOCKWISE - FIXED BUILD

CARA MEMASANG:
1. Ekstrak ZIP ini ke folder baru, misalnya Downloads\STOCKWISE_FIXED.
2. Buka folder STOCKWISE_FIXED di VS Code (File > Open Folder).
3. Buka Terminal > New Terminal. Pastikan terminal berada di folder yang sama dengan app.py.
4. Jalankan: python -m pip install -r requirements.txt
5. Jalankan: python -m streamlit run app.py
6. Buka alamat yang muncul, biasanya http://localhost:8501

PENTING:
- Jangan campur app.py ini dengan file lama. Gunakan folder baru agar database lama tidak tertimpa.
- Database stockwise.db akan dibuat otomatis di folder ini dan menyimpan data aplikasi.
- Data awal merupakan data simulasi, bukan data usaha nyata.
- Batch yang sudah kedaluwarsa tidak dihitung sebagai stok layak pakai untuk rekomendasi dan pencatatan produksi.

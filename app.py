import os
import json
import requests
from datetime import datetime

# Menggunakan Groq API (Gratis & Super Cepat)
API_URL = "https://api.groq.com/openai/v1/chat/completions"
API_KEY = os.getenv("AI_API_KEY")

def minta_ai_buat_konten(prompt_permintaan):
    """Agen 1: Pembuat Konten Iklan / Produk"""
    payload = {
        "model": "llama3-8b-8192",
        "messages": [
            {
                "role": "system", 
                "content": "Kamu adalah copywriter profesional. Buat caption pendek maksimal 30 kata dan WAJIB sertakan minimal 3 hashtag."
            },
            {"role": "user", "content": prompt_permintaan}
        ]
    }
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    try:
        response = requests.post(API_URL, json=payload, headers=headers).json()
        return response['choices'][0]['message']['content']
    except Exception as e:
        return f"Error Agen 1: {str(e)}"

def minta_ai_periksa_konten(hasil_konten):
    """Agen 2: Pemeriksa Kesalahan & Koreksi Otomatis (Evaluator)"""
    payload = {
        "model": "llama3-8b-8192",
        "messages": [
            {
                "role": "system", 
                "content": "Kamu adalah QC Officer. Periksa teks berikut. Apakah panjangnya melebihi 30 kata? Apakah ada minimal 3 hashtag? Jawab HANYA dengan kata 'LOLOS' jika sempurna, atau berikan instruksi perbaikan spesifik jika salah."
            },
            {"role": "user", "content": hasil_konten}
        ]
    }
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    try:
        response = requests.post(API_URL, json=payload, headers=headers).json()
        return response['choices'][0]['message']['content']
    except Exception as e:
        return f"Error Agen 2: {str(e)}"

def jalankan_sistem_otonom(kata_kunci):
    print(f"🚀 Memulai pencarian produk otomatis untuk: {kata_kunci}")
    
    percobaan = 0
    maksimal_koreksi = 5
    konten_sekarang = minta_ai_buat_konten(kata_kunci)
    riwayat_koreksi = []

    while percobaan < maksimal_koreksi:
        hasil_pemeriksaan = minta_ai_periksa_konten(konten_sekarang)
        
        if "LOLOS" in hasil_pemeriksaan.upper():
            print(f"✨ SUKSES! Sistem berhasil lolos QC pada percobaan ke-{percobaan+1}")
            break
        else:
            print(f"⚠️ Koreksi Otomatis ke-{percobaan+1}: {hasil_pemeriksaan}")
            riwayat_koreksi.append({
                "percobaan_ke": percobaan + 1,
                "kesalahan": hasil_pemeriksaan,
                "konten_salah": konten_sekarang
            })
            
            # Memaksa AI memperbaiki dirinya sendiri berdasarkan feedback kesalahan
            prompt_revisi = f"Hasil kerjamu sebelumnya salah: '{konten_sekarang}'. Perbaiki total berdasarkan instruksi ini: {hasil_pemeriksaan}"
            konten_sekarang = minta_ai_buat_konten(prompt_revisi)
            percobaan += 1

    # Menyimpan hasil akhir kerja AI ke dalam file log agar tercatat di GitHub
    laporan_bisnis = {
        "tanggal_eksekusi": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "input_user": kata_kunci,
        "hasil_akhir_ai": konten_sekarang,
        "total_revisi": percobaan,
        "catatan_koreksi": riwayat_koreksi
    }

    # Menulis hasil ke file lokal (akan dicommit oleh robot GitHub)
    with open("laporan_bisnis_ai.json", "w", encoding="utf-8") as f:
        json.dump(laporan_bisnis, f, indent=4, ensure_ascii=False)
        
    print("📁 Laporan bisnis berhasil disimpan ke laporan_bisnis_ai.json")

if __name__ == "__main__":
    # Simulasi input otomatis produk jualan bisnis kamu hari ini
    jalankan_sistem_otonom("Rekomendasi Sepatu Sneakers Lokal Keren Murah")
    

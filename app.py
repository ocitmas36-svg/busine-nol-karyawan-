import os
import requests

# Menggunakan GitHub Models API atau Groq API (Pilih yang gratis & cepat)
API_URL = "https://api.groq.com/openai/v1/chat/completions"
API_KEY = os.getenv("AI_API_KEY") # Nanti kita setel kuncinya

def minta_ai_buat_konten(prompt_permintaan):
    """Agen 1: Bertugas sebagai pembuat konten"""
    payload = {
        "model": "llama3-8b-8192",
        "messages": [
            {"role": "system", "content": "Kamu adalah copywriter profesional. Buat caption pendek maksimal 30 kata dan WAJIB sertakan minimal 3 hashtag."},
            {"role": "user", "content": prompt_permintaan}
        ]
    }
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    response = requests.post(API_URL, json=payload, headers=headers).json()
    return response['choices'][0]['message']['content']

def minta_ai_periksa_konten(hasil_konten):
    """Agen 2: Bertugas mengecek kesalahan (Evaluator)"""
    payload = {
        "model": "llama3-8b-8192",
        "messages": [
            {"role": "system", "content": "Kamu adalah QC Officer. Periksa teks berikut. Apakah panjangnya melebihi 30 kata? Apakah ada minimal 3 hashtag? Jawab HANYA dengan kata 'LOLOS' jika sempurna, atau berikan instruksi perbaikan jika salah."},
            {"role": "user", "content": hasil_konten}
        ]
    }
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    response = requests.post(API_URL, json=payload, headers=headers).json()
    return response['choices'][0]['message']['content']

def sistem_otonom_rosit(kata_kunci_user):
    percobaan = 0
    maksimal_koreksi = 5
    konten_sekarang = minta_ai_buat_konten(kata_kunci_user)
    
    # 🔁 DI SINI LOGIKA AI MEMPERBAIKI DIRINYA SENDIRI SECARA OTOMATIS
    while percobaan < maksimal_koreksi:
        hasil_pemeriksaan = minta_ai_periksa_konten(konten_sekarang)
        
        if "LOLOS" in hasil_pemeriksaan:
            print(f"✨ Sukses dalam {percobaan+1} kali percobaan!")
            return konten_sekarang
        else:
            # Jika salah, AI Agen 2 akan memberikan feedback ke AI Agen 1 untuk direvisi
            print(f"⚠️ Koreksi Otomatis ke-{percobaan+1}: {hasil_pemeriksaan}")
            prompt_revisi = f"Hasil kerjamu sebelumnya salah: '{konten_sekarang}'. Perbaiki berdasarkan koreksi ini: {hasil_pemeriksaan}"
            konten_sekarang = minta_ai_buat_konten(prompt_revisi)
            percobaan += 1
            
    return "Sistem gagal mengoreksi otomatis setelah 5 kali mencoba."

# Contoh simulasi pemicu sistem
# hasil_akhir = sistem_otonom_rosit("Jual baju kemeja flanel pria")

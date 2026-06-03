import os
import json
import requests
from datetime import datetime, timedelta

# Konfigurasi API Groq
API_URL = "https://api.groq.com/openai/v1/chat/completions"
API_KEY = os.getenv("AI_API_KEY")

# =====================================================================
# SIMULASI DATABASE KLIEN UMKM (Nanti data ini diisi dari Web Pendaftaran)
# =====================================================================
DB_KLIEN = {
    "081234567890": {
        "nama_pemilik": "Andi Sepatu",
        "nomor_target_bot": "081234567890",
        "tanggal_daftar": "2026-06-01",  # Contoh daftar 3 hari lalu
        "durasi_trial_hari": 5,
        "status_pembayaran": "Trial",    # Pilihan: Trial / Aktif / Jatuh Tempo
        "sop_perusahaan": """
        Nama Toko: Rosit Sneakers Store.
        Produk: Sepatu sneakers lokal berkualitas, harga kisaran Rp150.000 - Rp300.000.
        SOP Balasan: Ramah, santun, gunakan panggilan 'Kakak'. 
        Aturan Penting: Jika stok ditanya, jawab 'Semua produk ready stock siap kirim hari ini!'. 
        Jangan berikan diskon tambahan kecuali pembeli mengambil minimal 3 pasang.
        """
    },
    "089999999999": {
        "nama_pemilik": "Budi Coffee",
        "nomor_target_bot": "089999999999",
        "tanggal_daftar": "2026-05-20",  # Contoh daftar 15 hari lalu (Sudah Lewat 5 Hari)
        "durasi_trial_hari": 5,
        "status_pembayaran": "Trial",    # Statusnya masih Trial, harusnya nanti ke-detek Jatuh Tempo
        "sop_perusahaan": "Toko Kopi Buka jam 08.00 - 22.00."
    }
}

def hitung_status_akses(data_klien):
    """Fungsi melacak sisa hari trial dan mendeteksi jatuh tempo secara otomatis"""
    tgl_daftar = datetime.strptime(data_klien["tanggal_daftar"], "%Y-%m-%d")
    tgl_kadaluwarsa_trial = tgl_daftar + timedelta(days=data_klien["durasi_trial_hari"])
    tgl_sekarang = datetime.now()

    # Jika pemilik sudah bayar, langsung loloskan jadi Aktif
    if data_klien["status_pembayaran"].lower() == "aktif":
        return "AKTIF", 0

    # Jika masih trial, cek apakah waktunya masih ada atau sudah habis
    if tgl_sekarang <= tgl_kadaluwarsa_trial:
        sisa_hari = (tgl_kadaluwarsa_trial - tgl_sekarang).days + 1
        return "TRIAL", sisa_hari
    else:
        return "JATUH TEMPO", 0

def ai_agen_cs_balas(pesan_pelanggan, sop_toko):
    """Agen 1: CS AI yang membalas chat berdasarkan SOP Toko Klien"""
    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {
                "role": "system", 
                "content": f"Kamu adalah Customer Service otomatis yang cerdas dan ramah. Kamu WAJIB menjawab pertanyaan pelanggan HANYA berdasarkan SOP Perusahaan berikut ini: {sop_toko}. Jangan mengada-ada informasi di luar SOP."
            },
            {"role": "user", "content": pesan_pelanggan}
        ]
    }
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    try:
        response = requests.post(API_URL, json=payload, headers=headers).json()
        return response['choices'][0]['message']['content']
    except Exception as e:
        return f"Error Agen CS: {str(e)}"

def ai_agen_qc_periksa(jawaban_cs, sop_toko):
    """Agen 2: QC Officer yang memastikan jawaban CS tidak melanggar SOP"""
    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {
                "role": "system", 
                "content": f"Kamu adalah Quality Control untuk chat CS. Periksa apakah jawaban CS ini sudah ramah, akurat, dan sesuai dengan SOP Toko ini: {sop_toko}. Jika sudah bagus dan layak kirim ke WhatsApp pelanggan, jawab HANYA dengan kata 'LOLOS'. Jika buruk atau melanggar SOP, berikan revisi teks perbaikannya."
            },
            {"role": "user", "content": jawaban_cs}
        ]
    }
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    try:
        response = requests.post(API_URL, json=payload, headers=headers).json()
        return response['choices'][0]['message']['content']
    except Exception as e:
        return f"Error Agen QC: {str(e)}"

def proses_chat_masuk(nomor_toko, chat_pelanggan):
    print(f"\n📥 Ada chat masuk ke nomor Bot: {nomor_toko}")
    
    # 1. Cek apakah nomor toko tersebut terdaftar di sistem kita
    if nomor_toko not in DB_KLIEN:
        return "Nomor Anda belum terdaftar di sistem SaaS Rosit AI."

    klien = DB_KLIEN[nomor_toko]
    
    # 2. Cek status uji coba / jatuh tempo pembayaran klien
    status_akses, sisa_waktu = hitung_status_akses(klien)
    
    if status_akses == "JATUH TEMPO":
        print(f"❌ SISTEM MOGOK: Nomor {nomor_toko} sudah Jatuh Tempo! Mengirim instruksi tagihan manual.")
        return f"[MOGOK SISTEM] Masa trial 5 hari sudah habis. Silakan hubungi WA Rosit Admin 1 untuk perpanjangan."

    print(f"🟢 Akses Valid: Status [{status_akses}] | Sisa Masa Trial: {sisa_waktu} Hari.")

    # 3. Jalankan Debat AI untuk membalas chat pelanggan secara otonom
    jawaban_sekarang = ai_agen_cs_balas(chat_pelanggan, klien["sop_perusahaan"])
    
    # Proses koreksi diri maksimal 3 kali jika QC menolak
    for i in range(3):
        hasil_qc = ai_agen_qc_periksa(jawaban_sekarang, klien["sop_perusahaan"])
        if "LOLOS" in hasil_qc.upper():
            print(f"✨ Jawaban lolos QC pada pengecekan ke-{i+1}")
            break
        else:
            print(f"⚠️ QC merevisi jawaban CS ke-{i+1}")
            jawaban_sekarang = hasil_qc # Menggunakan teks perbaikan dari QC

    return jawaban_sekarang

if __name__ == "__main__":
    print("=== SIMULASI TESTING SISTEM SAAS BOT WA ROSIT AI ===")
    
    # TEST CASE 1: Menguji Toko Andi Sepatu (Masih masa Trial hari ke-3 dari 5 hari)
    pertanyaan_1 = "Min, sepatu sneakers yang harga 200rb ready gak? Terus dapet diskon lagi gak kalau beli 1 pasang?"
    hasil_balasan_1 = proses_chat_masuk("081234567890", pertanyaan_1)
    print(f"🤖 Bot WA Mengirim ke Pelanggan:\n{hasil_balasan_1}")
    
    print("-" * 50)
    
    # TEST CASE 2: Menguji Toko Budi Coffee (Sudah lewat 5 hari dari masa pendaftaran)
    pertanyaan_2 = "Kopi susu gula arennya masih ada mas?"
    hasil_balasan_2 = proses_chat_masuk("089999999999", pertanyaan_2)
    print(f"🤖 Bot WA Mengirim ke Pelanggan:\n{hasil_balasan_2}")
        

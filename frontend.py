import streamlit as st
import requests
from fpdf import FPDF
import tempfile
import datetime
import time 

# Konfigurasi Halaman
st.set_page_config(page_title="Skrining Hipertensi", page_icon="🩺", layout="centered")

st.title("Sistem Deteksi Dini Hipertensi")
st.markdown("Masukkan data rekam medis pasien untuk melihat prediksi risiko.")
st.write("---")

# ----------------- FUNGSI GENERATE PDF (VERSI RESMI) -----------------
def generate_pdf(nama, gender, age, hasil, payload_indo):
    pdf = FPDF()
    pdf.add_page()
    
    # 1. KOP SURAT PUSKESMAS
    pdf.set_font("Arial", 'B', 16)
    pdf.set_text_color(0, 50, 100)
    pdf.cell(0, 8, txt="PUSKESMAS MELINTANG", ln=True, align='C')
    
    pdf.set_font("Arial", '', 10)
    pdf.set_text_color(50, 50, 50)
    pdf.cell(0, 5, txt="Kecamatan Rangkui, Kota Pangkalpinang, Kepulauan Bangka Belitung", ln=True, align='C')
    pdf.cell(0, 5, txt="Layanan Skrining Kesehatan Penyakit Tidak Menular (PTM)", ln=True, align='C')
    
    pdf.line(10, 30, 200, 30)
    pdf.line(10, 31, 200, 31)
    pdf.ln(8)
    
    # 2. JUDUL DOKUMEN DENGAN BACKGROUND
    pdf.set_font("Arial", 'B', 14)
    pdf.set_text_color(0, 0, 0)
    pdf.set_fill_color(220, 230, 240)
    pdf.cell(0, 10, txt="LAPORAN HASIL DETEKSI DINI HIPERTENSI", border=1, ln=True, align='C', fill=True)
    pdf.ln(5)
    
    # 3. IDENTITAS PASIEN
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 8, txt="A. IDENTITAS PASIEN", ln=True)
    pdf.set_font("Arial", '', 11)
    
    pdf.cell(50, 8, txt=" Nama Lengkap", border=1)
    pdf.cell(140, 8, txt=f" {nama}", border=1, ln=True)
    
    pdf.cell(50, 8, txt=" Jenis Kelamin", border=1)
    pdf.cell(140, 8, txt=f" {gender}", border=1, ln=True)
    
    pdf.cell(50, 8, txt=" Usia", border=1)
    pdf.cell(140, 8, txt=f" {age} Tahun", border=1, ln=True)
    
    pdf.cell(50, 8, txt=" Tanggal Periksa", border=1)
    pdf.cell(140, 8, txt=f" {datetime.date.today().strftime('%d %B %Y')}", border=1, ln=True)
    pdf.ln(5)
    
    # 4. DATA KLINIS
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 8, txt="B. PARAMETER MEDIS & GAYA HIDUP", ln=True)
    pdf.set_font("Arial", '', 11)
    
    for key, value in payload_indo.items():
        pdf.cell(70, 8, txt=f" {key}", border=1)
        pdf.cell(120, 8, txt=f" {value}", border=1, ln=True)
    pdf.ln(5)
    
    # 5. HASIL PREDIKSI SISTEM
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 8, txt="C. KESIMPULAN DETEKSI DINI", ln=True)
    
    if hasil == "Beresiko Hipertensi":
        pdf.set_text_color(220, 20, 60)
        hasil_teks = "BERESIKO HIPERTENSI"
        saran = "Segera jadwalkan konsultasi lanjutan dengan dokter umum."
    else:
        pdf.set_text_color(34, 139, 34)
        hasil_teks = "NORMAL (TIDAK BERESIKO)"
        saran = "Pertahankan pola hidup sehat dan lakukan pemeriksaan rutin."
        
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, txt=f"STATUS: {hasil_teks}", border=1, ln=True, align='C')
    
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", 'I', 11)
    pdf.cell(0, 8, txt=f"Rekomendasi: {saran}", ln=True)
    
    # 6. KOLOM TANDA TANGAN
    pdf.ln(10)
    pdf.set_font("Arial", '', 11)
    pdf.cell(120, 8, txt="")
    pdf.cell(70, 8, txt="Petugas Pemeriksa,", align='C', ln=True)
    pdf.ln(15)
    pdf.cell(120, 8, txt="")
    pdf.cell(70, 8, txt="(.......................................)", align='C', ln=True)
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        pdf.output(tmp.name)
        with open(tmp.name, "rb") as f:
            return f.read()

# ----------------- ANTARMUKA STREAMLIT (Tanpa st.form) -----------------

st.subheader("A. Data Diri Pasien")
nama = st.text_input("Nama Lengkap", placeholder="Contoh: Budi Santoso")

col_a, col_b = st.columns(2)
with col_a:
    gender = st.selectbox("Jenis Kelamin", ["Laki-laki", "Perempuan"])
with col_b:
    age = st.number_input("Usia (Tahun)", min_value=1, max_value=120, value=45)
    
st.write("---")
st.subheader("B. Data Antropometri (Fisik)")

col_tb, col_bb = st.columns(2)
with col_tb:
    tinggi_badan = st.number_input("Tinggi Badan (cm)", min_value=50.0, max_value=250.0, value=165.0, step=1.0)
with col_bb:
    berat_badan = st.number_input("Berat Badan (kg)", min_value=10.0, max_value=250.0, value=65.0, step=1.0)

bmi_calc = berat_badan / ((tinggi_badan / 100) ** 2)
st.info(f"📊 **Indeks Massa Tubuh (BMI) Pasien:** {bmi_calc:.1f}")

st.write("---")
st.subheader("C. Data Klinis & Gaya Hidup")

col1, col2 = st.columns(2)

with col1:
    bp_history_indo = st.selectbox("Riwayat Tekanan Darah", ["Normal", "Pra-hipertensi (Sedikit Tinggi)", "Hipertensi (Tinggi)"])
    
    # Logika dinamis sekarang akan berjalan instan!
    if bp_history_indo == "Normal":
        st.selectbox("Pengobatan Saat Ini", ["Tidak Ada"], disabled=True, help="Otomatis dinonaktifkan.")
        medication_indo = "Tidak Ada"
    else:
        medication_indo = st.selectbox("Pengobatan Saat Ini", ["Tidak Ada", "Beta Blocker (ex: Bisoprolol)", "ACE Inhibitor (ex: Captopril)", "Diuretik (Obat Pelancar Kencing)", "Lainnya"])
        
    family_history_indo = st.selectbox("Riwayat Darah Tinggi Keluarga", ["Tidak Ada", "Ada (Ya)"])

with col2:
    sleep_duration = st.number_input("Rata-rata Durasi Tidur (Jam/Hari)", min_value=1.0, max_value=24.0, value=7.0, step=0.5)
    stress_score = st.number_input("Skor Stres (0-10)", min_value=0, max_value=10, value=5, help="0 = Sangat Santai, 10 = Sangat Tertekan")
    exercise_level_indo = st.selectbox("Aktivitas Fisik / Olahraga", ["Rendah (Jarang)", "Sedang (Rutin Ringan)", "Tinggi (Sering/Atlet)"])
    smoking_status_indo = st.selectbox("Status Merokok", ["Bukan Perokok", "Perokok Aktif"])

st.write("---")
salt_intake = st.number_input("Estimasi Konsumsi Garam Harian (Gram/Hari)", min_value=0.0, max_value=50.0, value=5.0, step=0.5)
st.caption("**Panduan Estimasi:** 1 sendok teh peres garam dapur setara dengan ±5 gram. Perhatikan juga garam pada makanan kemasan/instan.")

st.write("")

# Menggunakan st.button biasa alih-alih form_submit_button
submitted = st.button("Analisis Risiko Pasien", use_container_width=True)

# ----------------- LOGIKA PENGIRIMAN DATA DENGAN ANIMASI -----------------
if submitted:
    if nama.strip() == "":
        st.error("Gagal! Mohon isi Nama Lengkap pasien terlebih dahulu.")
    else:
        progress_text = "Sistem sedang memuat data dan menganalisis pola medis..."
        my_bar = st.progress(0, text=progress_text)
        
        for percent_complete in range(100):
            time.sleep(0.015) 
            my_bar.progress(percent_complete + 1, text=progress_text)
            
        my_bar.empty()
        
        bp_map = {"Normal": "Normal", "Pra-hipertensi (Sedikit Tinggi)": "Prehypertension", "Hipertensi (Tinggi)": "Hypertension"}
        med_map = {"Tidak Ada (Otomatis)": "None", "Tidak Ada": "None", "Beta Blocker (ex: Bisoprolol)": "Beta Blocker", "ACE Inhibitor (ex: Captopril)": "ACE Inhibitor", "Diuretik (Obat Pelancar Kencing)": "Diuretic", "Lainnya": "Other"}
        fam_map = {"Tidak Ada": "No", "Ada (Ya)": "Yes"}
        exe_map = {"Rendah (Jarang)": "Low", "Sedang (Rutin Ringan)": "Moderate", "Tinggi (Sering/Atlet)": "High"}
        smk_map = {"Bukan Perokok": "Non-Smoker", "Perokok Aktif": "Smoker"}
        
        payload = {
            "Age": age,
            "Salt_Intake": salt_intake,
            "Stress_Score": stress_score,
            "BP_History": bp_map[bp_history_indo],
            "Sleep_Duration": sleep_duration,
            "BMI": round(bmi_calc, 1),
            "Medication": med_map[medication_indo],
            "Family_History": fam_map[family_history_indo],
            "Exercise_Level": exe_map[exercise_level_indo],
            "Smoking_Status": smk_map[smoking_status_indo]
        }
        
        payload_indo = {
            "Tinggi Badan": f"{tinggi_badan} cm",
            "Berat Badan": f"{berat_badan} kg",
            "BMI": round(bmi_calc, 1),
            "Riwayat Tekanan Darah": bp_history_indo,
            "Pengobatan": medication_indo,
            "Riwayat Keluarga": family_history_indo,
            "Durasi Tidur": f"{sleep_duration} Jam",
            "Tingkat Stres": f"Skor {stress_score}/10",
            "Olahraga": exercise_level_indo,
            "Status Merokok": smoking_status_indo,
            "Konsumsi Garam": f"{salt_intake} Gram/Hari"
        }
        
        try:
            response = requests.post("http://127.0.0.1:5000/predict", json=payload)
            
            if response.status_code == 200:
                res_data = response.json()
                hasil = res_data['prediction']
                
                st.write("---")
                st.subheader("📋 Kesimpulan Analisis")
                
                if hasil == "Beresiko Hipertensi":
                    st.error(f"⚠️ Berdasarkan algoritma Random Forest, pasien terdeteksi **{hasil.upper()}**.")
                else:
                    st.success(f"✅ Berdasarkan algoritma Random Forest, pasien terdeteksi **{hasil.upper()}**.")
                
                pdf_bytes = generate_pdf(nama, gender, age, hasil, payload_indo)
                
                st.download_button(
                    label="📄 Cetak Rekam Medis (PDF)",
                    data=pdf_bytes,
                    file_name=f"Laporan_Deteksi_{nama.replace(' ', '_')}.pdf",
                    mime="application/pdf"
                )
            else:
                st.warning("Server merespon dengan error.")
        except Exception as e:
            st.error("Gagal terhubung ke AI. Pastikan server Flask (app.py) sudah berjalan.")
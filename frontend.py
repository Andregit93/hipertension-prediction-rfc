import streamlit as st
import requests
from fpdf import FPDF
import tempfile
import datetime

st.set_page_config(page_title="Deteksi Hipertensi", layout="centered")

st.title("Sistem Deteksi Dini Hipertensi 🩺")
st.markdown("**Puskesmas Melintang** - Masukkan data rekam medis pasien untuk melihat prediksi risiko.")

# Fungsi untuk membuat file PDF Laporan
def generate_pdf(nama, gender, age, hasil, data_medis):
    pdf = FPDF()
    pdf.add_page()
    
    # Header Dokumen
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="HASIL DETEKSI DINI HIPERTENSI PASIEN", ln=True, align='C')
    pdf.set_font("Arial", 'I', 10)
    pdf.cell(200, 10, txt=f"Tanggal Cetak: {datetime.date.today().strftime('%d %B %Y')}", ln=True, align='C')
    pdf.line(10, 30, 200, 30)
    pdf.ln(10)
    
    # Identitas Pasien
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="1. Identitas Pasien", ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.cell(200, 8, txt=f"   Nama Lengkap   : {nama}", ln=True)
    pdf.cell(200, 8, txt=f"   Jenis Kelamin  : {gender}", ln=True)
    pdf.cell(200, 8, txt=f"   Usia           : {age} Tahun", ln=True)
    pdf.ln(5)
    
    # Data Klinis & Gaya Hidup
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="2. Parameter Medis & Gaya Hidup", ln=True)
    pdf.set_font("Arial", '', 11)
    for key, value in data_medis.items():
        pdf.cell(200, 8, txt=f"   - {key.replace('_', ' ')}: {value}", ln=True)
    pdf.ln(5)
    
    # Hasil Keputusan
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="3. Hasil Analisis Sistem (Random Forest)", ln=True)
    pdf.set_font("Arial", 'B', 14)
    if hasil == "Beresiko Hipertensi":
        pdf.set_text_color(200, 0, 0) # Warna Merah
    else:
        pdf.set_text_color(0, 150, 0) # Warna Hijau
    pdf.cell(200, 10, txt=f"   KESIMPULAN: {hasil.upper()}", ln=True)
    pdf.set_text_color(0, 0, 0) # Reset warna teks
    
    # Footer Medis
    pdf.ln(20)
    pdf.set_font("Arial", 'I', 10)
    pdf.cell(200, 10, txt="Catatan: Hasil ini merupakan deteksi dini (skrining awal) berbasis AI.", ln=True)
    pdf.cell(200, 5, txt="Diagnosis pasti tetap memerlukan konsultasi dan pemeriksaan fisik oleh dokter.", ln=True)
    
    # Menyimpan file ke temporary agar bisa di-download Streamlit
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        pdf.output(tmp.name)
        with open(tmp.name, "rb") as f:
            return f.read()

# ----------------- ANTARMUKA STREAMLIT -----------------
with st.form("prediction_form"):
    st.subheader("A. Data Diri Pasien")
    nama = st.text_input("Nama Lengkap", placeholder="Contoh: Siti Aminah")
    
    col_a, col_b = st.columns(2)
    with col_a:
        gender = st.selectbox("Jenis Kelamin", ["Laki-laki", "Perempuan"], help="Pilih jenis kelamin pasien.")
    with col_b:
        age = st.number_input("Usia (Tahun)", min_value=1, max_value=120, value=45, help="Angka bulat. Contoh: 45")
        
    st.write("---")
    st.subheader("B. Data Klinis & Gaya Hidup")
    
    col1, col2 = st.columns(2)
    with col1:
        bmi = st.number_input("BMI (Body Mass Index)", value=22.5, step=0.1, help="Ketik menggunakan titik. Contoh: 25.4 (Normal: 18.5 - 24.9)")
        salt_intake = st.number_input("Konsumsi Garam (Gram/Hari)", value=5.0, step=0.1, help="Rata-rata gram per hari. Contoh: 6.5")
        sleep_duration = st.number_input("Durasi Tidur (Jam/Hari)", value=7.0, step=0.1, help="Rata-rata tidur. Contoh: 6.5")
        stress_score = st.number_input("Skor Stres (0-10)", min_value=0, max_value=10, value=5, help="0 = Tidak stres, 10 = Sangat berat. Contoh: 7")
        
    with col2:
        bp_history = st.selectbox("Riwayat Tekanan Darah", ["Normal", "Prehypertension", "Hypertension"], help="Riwayat tensi masa lalu.")
        medication = st.selectbox("Pengobatan Saat Ini", ["None", "Beta Blocker", "ACE Inhibitor", "Diuretic", "Other"], help="Pilih 'None' jika tidak konsumsi obat rutin.")
        family_history = st.selectbox("Riwayat Keluarga", ["No", "Yes"], help="Adakah garis keturunan/keluarga inti yang hipertensi?")
        exercise_level = st.selectbox("Aktivitas Olahraga", ["Low", "Moderate", "High"], help="Low = Jarang, Moderate = Rutin ringan, High = Atlet/Sering")
        smoking_status = st.selectbox("Status Merokok", ["Non-Smoker", "Smoker"], help="Apakah pasien perokok aktif?")

    # Tombol Eksekusi
    submitted = st.form_submit_button("Analisis Risiko Pasien")

# ----------------- LOGIKA PENGIRIMAN DATA -----------------
if submitted:
    if nama.strip() == "":
        st.error("Gagal! Mohon isi Nama Lengkap pasien terlebih dahulu.")
    else:
        # Menyiapkan data untuk dikirim ke API Flask
        payload = {
            "Age": age,
            "Salt_Intake": salt_intake,
            "Stress_Score": stress_score,
            "BP_History": bp_history,
            "Sleep_Duration": sleep_duration,
            "BMI": bmi,
            "Medication": medication,
            "Family_History": family_history,
            "Exercise_Level": exercise_level,
            "Smoking_Status": smoking_status
        }
        
        with st.spinner("AI sedang memproses data medis..."):
            try:
                # Memanggil API Flask di background
                response = requests.post("http://127.0.0.1:5000/predict", json=payload)
                
                if response.status_code == 200:
                    res_data = response.json()
                    hasil = res_data['prediction']
                    
                    st.write("---")
                    st.subheader("📋 Laporan Singkat")
                    st.write(f"**Nama Pasien:** {nama} ({gender}, {age} Tahun)")
                    
                    if hasil == "Beresiko Hipertensi":
                        st.error(f"⚠️ Hasil Prediksi: **{hasil}**")
                        st.write("Tindakan: Disarankan untuk menjadwalkan konsultasi lanjutan dengan dokter umum.")
                    else:
                        st.success(f"✅ Hasil Prediksi: **{hasil}**")
                        st.write("Tindakan: Kondisi baik. Edukasi pasien untuk mempertahankan gaya hidup sehat.")
                    
                    # Mengeksekusi pembuatan file PDF
                    pdf_bytes = generate_pdf(nama, gender, age, hasil, payload)
                    
                    # Menampilkan Tombol Download
                    st.download_button(
                        label="📄 Cetak Dokumen Rekam Medis (PDF)",
                        data=pdf_bytes,
                        file_name=f"Laporan_Deteksi_{nama.replace(' ', '_')}.pdf",
                        mime="application/pdf"
                    )
                else:
                    st.warning("Server merespon dengan error.")
            except Exception as e:
                st.error("Koneksi terputus. Pastikan terminal Flask (app.py) sedang berjalan di belakang layar.")
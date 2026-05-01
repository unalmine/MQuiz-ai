# MQUIZ AI - LANSMAN SÜRÜMÜ (Özel Bordo Tema)
import streamlit as st
import PyPDF2
import google.generativeai as genai
import os
import json
import random
from dotenv import load_dotenv

# --- 1. SİSTEM AYARLARI ---
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("🚨 Kritik Hata: API Anahtarı bulunamadı. Lütfen .env dosyanızı kontrol edin.")
    st.stop()

genai.configure(api_key=api_key)

# Sayfa Yapılandırması
st.set_page_config(page_title="MQuiz AI | Profesyonel Eğitim Platformu", page_icon="🍷", layout="wide")

# --- 2. ÖZEL TASARIM (BORDO KONSEPT - CSS) ---
st.markdown("""
<style>
    /* Ana Arka Plan - Koyu Bordo Geçişi */
    [data-testid="stAppViewContainer"] {
        background-color: #140305;
        background-image: radial-gradient(circle at 50% 0%, #360a14 0%, #140305 80%);
        color: #f0f0f0;
    }
    
    /* Üst taraftaki boşluğu azaltma */
    .block-container {
        padding-top: 2rem;
    }
    
    /* Profesyonel Kart Yapısı */
    .dashboard-card {
        background: rgba(36, 8, 13, 0.7); /* Şeffaf koyu bordo */
        padding: 20px;
        border-radius: 12px;
        border-left: 5px solid #a3162e; /* Logoya uygun canlı bordo */
        border-top: 1px solid #360a14;
        border-right: 1px solid #360a14;
        border-bottom: 1px solid #360a14;
        margin-bottom: 20px;
        box-shadow: 0 8px 16px rgba(0,0,0,0.4);
    }
    
    /* Buton Tasarımı */
    .stButton>button {
        background-color: #8c1024; /* Bordo Buton */
        color: white;
        border-radius: 8px;
        height: 3em;
        font-weight: bold;
        border: 1px solid #a3162e;
        transition: all 0.3s ease;
        width: 100%;
        letter-spacing: 1px;
    }
    
    .stButton>button:hover {
        background-color: #b3142e; /* Hover durumunda parlayan bordo */
        border-color: #ff3b5c;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(163, 22, 46, 0.4);
        color: white;
    }
    
    /* Slider ve vurgu renkleri */
    div.stSlider > div[data-baseweb="slider"] > div > div > div {
        background-color: #a3162e !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. ÜST BİLGİ VE LOGO (HEADER) ---
col_logo, col_text = st.columns([1, 8])
with col_logo:
    # Logonuz (MQuiz AI) burada yüklenecek
    try:
        st.image("logo.png", width=120)
    except:
        st.error("Logo bulunamadı! 'logo.png' klasörde mi?")
        
with col_text:
    st.markdown("<h1 style='margin-bottom: 0;'>MQuiz AI</h1>", unsafe_allow_html=True)
    st.markdown("*Kişisel PDF dokümanlarından saniyeler içinde benzersiz testler oluşturun.*")

st.divider()

# --- 4. ANA KONTROL PANELİ (DASHBOARD) ---
st.markdown("<div class='dashboard-card'><h3>⚙️ Sınav Motoru Parametreleri</h3>", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
with c1:
    soru_sayisi = st.select_slider("Hedef Soru Sayısı", options=[5, 10, 15, 20, 30, 40, 50], value=10)
with c2:
    zorluk = st.selectbox("Akademik Zorluk", ["Başlangıç", "Orta Seviye", "İleri Seviye", "Uzman (Detay Odaklı)"])
with c3:
    odak = st.text_input("Özel Odak Noktası (Opsiyonel)", placeholder="Örn: Sadece kavramlar, tarihler...")

st.markdown("</div>", unsafe_allow_html=True)

# --- 5. VERİ GİRİŞİ VE İŞLEME ---
if "test_verisi" not in st.session_state:
    st.session_state.test_verisi = None
if "cevaplar" not in st.session_state:
    st.session_state.cevaplar = {}
if "sinav_bitti" not in st.session_state:
    st.session_state.sinav_bitti = False

st.markdown("<div class='dashboard-card' style='border-left-color: #d18a28;'><h3>📂 Kaynak Doküman Yükleme</h3>", unsafe_allow_html=True)
yuklenen_dosya = st.file_uploader("Analiz edilecek PDF dosyasını buraya sürükleyin veya seçin", type="pdf")
st.markdown("</div>", unsafe_allow_html=True)

if yuklenen_dosya:
    st.markdown("<br>", unsafe_allow_html=True)
    col_btn, _ = st.columns([1, 2])
    
    with col_btn:
        baslat_metni = "🚀 SINAVI OLUŞTUR" if st.session_state.test_verisi is None else "🔄 YENİ SORULARLA GÜNCELLE"
        if st.button(baslat_metni):
            st.session_state.test_verisi = None
            st.session_state.cevaplar = {}
            st.session_state.sinav_bitti = False
            
            with st.spinner(f"AI Dokümanı analiz ediyor... {soru_sayisi} özel soru hazırlanıyor..."):
                try:
                    pdf_okuyucu = PyPDF2.PdfReader(yuklenen_dosya)
                    metin = "".join([page.extract_text() for page in pdf_okuyucu.pages if page.extract_text()])
                    
                    seed = random.randint(1, 999999)
                    odak_talimati = f"Özellikle şu konuya odaklan: '{odak}'." if odak else "Metnin genelinden homojen sorular seç."
                    
                    prompt = f"""
                    Sen profesyonel bir eğitimcisin.
                    GÖREV: Aşağıdaki metinden {soru_sayisi} adet {zorluk} seviyesinde çoktan seçmeli soru üret.
                    1. {odak_talimati}
                    2. BENZERSİZLİK KODU: {seed}. Hep aynı yerlerden sorma, farklı detaylar bul.
                    3. Çıktıyı SADECE JSON formatında ver:
                    [
                        {{"soru": "Soru", "secenekler": ["A", "B", "C", "D"], "dogru_cevap": "Doğru şıkkın tam metni", "aciklama": "Açıklama"}}
                    ]
                    METİN: {metin[:250000]}
                    """
                    
                    models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                    target_model = next((m for m in models if "flash" in m.lower()), models[0])
                    
                    ai_engine = genai.GenerativeModel(target_model)
                    res = ai_engine.generate_content(prompt)
                    
                    cleaned_json = res.text.replace('```json', '').replace('```', '').strip()
                    st.session_state.test_verisi = json.loads(cleaned_json)
                    st.rerun()
                except Exception as e:
                    st.error(f"Sistem hatası oluştu. Lütfen tekrar deneyin. Detay: {e}")

# --- 6. SINAV EKRANI ---
if st.session_state.test_verisi:
    st.divider()
    st.success(f"✅ Sınav Hazır! Başarılar dileriz.")
    
    for i, p in enumerate(st.session_state.test_verisi):
        st.markdown(f"<div class='dashboard-card'><h4>Soru {i+1}: {p['soru']}</h4></div>", unsafe_allow_html=True)
        ans = st.radio("Seçenekler:", p['secenekler'], key=f"q_{i}", index=None, label_visibility="collapsed", disabled=st.session_state.sinav_bitti)
        st.session_state.cevaplar[f"q_{i}"] = ans
        st.markdown("<br>", unsafe_allow_html=True)

    if not st.session_state.sinav_bitti:
        col_b, _ = st.columns([1, 2])
        with col_b:
            if st.button("📝 SINAVI TAMAMLA VE SONUÇLARI GÖR"):
                st.session_state.sinav_bitti = True
                st.rerun()

# --- 7. ANALİZ VE SKOR ---
if st.session_state.sinav_bitti:
    st.header("📊 Performans Analizi")
    dogru = sum(1 for i, p in enumerate(st.session_state.test_verisi) if st.session_state.cevaplar.get(f"q_{i}") == p['dogru_cevap'])
    yanlis = len(st.session_state.test_verisi) - dogru
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Doğru Sayısı", f"✅ {dogru}")
    c2.metric("Yanlış/Boş Sayısı", f"❌ {yanlis}")
    c3.metric("Başarı Oranı", f"%{int((dogru/len(st.session_state.test_verisi))*100)}")

    for i, p in enumerate(st.session_state.test_verisi):
        durum = "✅ Doğru" if st.session_state.cevaplar.get(f"q_{i}") == p['dogru_cevap'] else "❌ Yanlış/Boş"
        with st.expander(f"{durum} | Soru {i+1} Analizi"):
            st.write(f"**Soru:** {p['soru']}")
            st.write(f"**Senin Cevabın:** {st.session_state.cevaplar.get(f'q_{i}')}")
            st.write(f"**Doğru Cevap:** {p['dogru_cevap']}")
            st.info(f"**Öğretmen Notu:** {p['aciklama']}")

    st.divider()
    if st.button("🔄 Tüm Verileri Sıfırla ve Başa Dön"):
        st.session_state.clear()
        st.rerun()
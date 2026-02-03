import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# Sayfa Ayarları
st.set_page_config(page_title="CMV Üveit Analiz Paneli", layout="wide")

# Başlık ve Giriş
st.title("🔬 CMV Ön Üveit İmmünolojik Analiz Paneli")
st.markdown("""
Bu panel, **Sağlıklı (CMV-/+)** ve **CMV Üveit (Vaka)** grupları arasındaki immünolojik farkları 
(özellikle **CTLA-4, PD-1 ve NKG2A** ekspresyonlarını) interaktif olarak incelemek için hazırlanmıştır.
""")

# Yan Menü (Sidebar)
st.sidebar.header("⚙️ Grafik Ayarları")
n_samples = st.sidebar.slider("Örneklem Sayısı (Simülasyon)", 5, 50, 11)
show_points = st.sidebar.checkbox("Bireysel Veri Noktalarını Göster (Jitter)", value=True)

# Veri Üretme Fonksiyonu (Senin tezindeki ortalamalarla)
def generate_data(mean, sd, n):
    np.random.seed(42) # Sabit sonuç için
    data = np.random.normal(mean, sd, n)
    return np.clip(data, 0, None) # Negatif değer olamaz

# --- VERİLERİN HAZIRLANMASI ---
# Gruplar: CMV (-), CMV (+), Vaka
groups = ['CMV (-)', 'CMV (+)', 'Vaka Grubu']

# 1. CD56dim CTLA-4
df1 = pd.DataFrame({
    'Grup': groups * n_samples,
    'Değer': np.concatenate([
        generate_data(0.63, 0.67, n_samples),
        generate_data(0.72, 0.58, n_samples),
        generate_data(2.05, 1.51, n_samples)
    ]),
    'Belirteç': 'CD56dim CTLA-4+'
})

# 2. CD56bright CTLA-4
df2 = pd.DataFrame({
    'Grup': groups * n_samples,
    'Değer': np.concatenate([
        generate_data(6.4, 4.0, n_samples),
        generate_data(3.8, 2.4, n_samples),
        generate_data(8.5, 4.4, n_samples)
    ]),
    'Belirteç': 'CD56bright CTLA-4+'
})

# 3. CD56dim NKG2A
df3 = pd.DataFrame({
    'Grup': groups * n_samples,
    'Değer': np.concatenate([
        generate_data(49.3, 10.2, n_samples),
        generate_data(36.1, 18.9, n_samples),
        generate_data(34.3, 16.7, n_samples)
    ]),
    'Belirteç': 'CD56dim NKG2A+'
})

# 4. Total NK Oranı
df4 = pd.DataFrame({
    'Grup': groups * n_samples,
    'Değer': np.concatenate([
        generate_data(9.9, 4.2, n_samples),
        generate_data(11.3, 5.0, n_samples),
        generate_data(11.2, 7.7, n_samples)
    ]),
    'Belirteç': 'Total NK Hücre Oranı'
})

datasets = [df1, df2, df3, df4]
titles = [
    "CD56dim CTLA-4+ (Vaka Grubunda Artış)", 
    "CD56bright CTLA-4+ (Vaka Grubunda Artış)", 
    "CD56dim NKG2A+ (Vaka Grubunda Azalış)", 
    "Total NK Hücre Oranı (Fark Yok)"
]
# P değerlerini manuel ekleyelim (Görsel üstüne)
p_infos = [
    "p=0.020 (vs CMV-)\np=0.045 (vs CMV+)",
    "p=0.005 (vs CMV+)",
    "p=0.028 (vs CMV-)",
    "Anlamlı Fark Yok"
]

# --- GRAFİKLERİN ÇİZİLMESİ ---
st.subheader("📊 Karşılaştırmalı Analiz Grafikleri")

row1_col1, row1_col2 = st.columns(2)
row2_col1, row2_col2 = st.columns(2)
cols = [row1_col1, row1_col2, row2_col1, row2_col2]

prism_palette = ["#E0E0E0", "#90CAF9", "#1565C0"]

for i, col in enumerate(cols):
    with col:
        fig, ax = plt.subplots(figsize=(6, 5))
        
        # Boxplot
        sns.boxplot(x="Grup", y="Değer", data=datasets[i], ax=ax, 
                    palette=prism_palette, width=0.5, linewidth=1.5, showfliers=False)
        
        # Jitter (Noktalar)
        if show_points:
            sns.stripplot(x="Grup", y="Değer", data=datasets[i], ax=ax, 
                          color="black", size=5, jitter=0.15, alpha=0.7)
        
        # Süslemeler
        ax.set_title(titles[i], fontweight='bold', fontsize=10)
        ax.set_ylabel("% Ekspresyon")
        ax.set_xlabel("")
        sns.despine()
        
        # P değeri notu
        y_max = datasets[i]['Değer'].max()
        ax.text(1, y_max*1.05, p_infos[i], ha='center', va='bottom', fontsize=9, color='red')
        
        st.pyplot(fig)

# Tablo Görünümü
st.subheader("📋 Özet İstatistik Tablosu")
st.info("Bu veriler tezinizdeki tablolardan alınmıştır.")

summary_data = {
    'Parametre': ['CD56dim CTLA-4', 'CD56bright CTLA-4', 'CD56dim NKG2A', 'Total NK Oranı'],
    'CMV (-) Ort.±SS': ['0.63 ± 0.67', '6.4 ± 4.0', '49.3 ± 10.2', '9.9 ± 4.2'],
    'CMV (+) Ort.±SS': ['0.72 ± 0.58', '3.8 ± 2.4', '36.1 ± 18.9', '11.3 ± 5.0'],
    'Vaka Grubu Ort.±SS': ['2.05 ± 1.51', '8.5 ± 4.4', '34.3 ± 16.7', '11.2 ± 7.7'],
    'P Değeri (Genel)': ['0.036*', '0.020*', '0.660', '0.821']
}
st.table(pd.DataFrame(summary_data))

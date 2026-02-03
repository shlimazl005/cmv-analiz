import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="CMV Üveit Analiz Paneli", layout="wide", page_icon="🔬")

# Başlık
st.title("🔬 CMV Ön Üveit İmmünolojik Analiz Paneli")
st.markdown("""
Bu interaktif panel, **Sağlıklı (CMV-/+)** ve **CMV Üveit (Vaka)** grupları arasındaki immünolojik farkları 
incelemek için **tez verileri simüle edilerek** oluşturulmuştur.
""")

# --- YAN MENÜ ---
with st.sidebar:
    st.header("⚙️ Görünüm Ayarları")
    n_samples = st.slider("Grup Başına Örneklem Sayısı (N)", 10, 50, 11)
    show_points = st.checkbox("Bireysel Veri Noktalarını Göster", value=True)
    st.info("Bu grafikler GraphPad Prism estetiğinde, Plotly altyapısı ile çizilmiştir.")

# --- VERİ ÜRETME FONKSİYONU ---
def generate_data(mean, sd, n):
    np.random.seed(42) # Veriler her seferinde değişmesin, sabit kalsın
    data = np.random.normal(mean, sd, n)
    return np.clip(data, 0, None) # Negatif değerleri sıfırla

# --- DATASETLERİN HAZIRLANMASI (Tez Verileri) ---
groups = ['CMV (-)', 'CMV (+)', 'Vaka Grubu']

# 1. CD56dim CTLA-4+ (Vaka grubunda Yüksek)
df_ctla4_dim = pd.DataFrame({
    'Grup': groups * n_samples,
    'Değer': np.concatenate([
        generate_data(0.63, 0.67, n_samples),
        generate_data(0.72, 0.58, n_samples),
        generate_data(2.05, 1.51, n_samples)
    ]),
    'Belirteç': 'CD56dim CTLA-4+'
})

# 2. CD56bright CTLA-4+ (Vaka grubunda Yüksek)
df_ctla4_bright = pd.DataFrame({
    'Grup': groups * n_samples,
    'Değer': np.concatenate([
        generate_data(6.4, 4.0, n_samples),
        generate_data(3.8, 2.4, n_samples),
        generate_data(8.5, 4.4, n_samples)
    ]),
    'Belirteç': 'CD56bright CTLA-4+'
})

# 3. CD56dim NKG2A (Vaka grubunda Düşük)
df_nkg2a = pd.DataFrame({
    'Grup': groups * n_samples,
    'Değer': np.concatenate([
        generate_data(49.3, 10.2, n_samples),
        generate_data(36.1, 18.9, n_samples),
        generate_data(34.3, 16.7, n_samples)
    ]),
    'Belirteç': 'CD56dim NKG2A+'
})

# 4. Total NK Hücre Oranı (Fark Yok)
df_nk = pd.DataFrame({
    'Grup': groups * n_samples,
    'Değer': np.concatenate([
        generate_data(9.9, 4.2, n_samples),
        generate_data(11.3, 5.0, n_samples),
        generate_data(11.2, 7.7, n_samples)
    ]),
    'Belirteç': 'Total NK Hücre Oranı (%)'
})

# --- GRAFİK ÇİZME FONKSİYONU (PLOTLY) ---
def create_prism_plot(df, y_label, title, p_val_text=None):
    # Renk Paleti (Gri -> Açık Mavi -> Koyu Lacivert)
    colors = {'CMV (-)': '#E0E0E0', 'CMV (+)': '#90CAF9', 'Vaka Grubu': '#0D47A1'}
    
    # Kutu Grafiği + Noktalar (points='all')
    fig = px.box(df, x="Grup", y="Değer", color="Grup", 
                 points="all" if show_points else False,
                 color_discrete_map=colors,
                 title=title)
    
    # GraphPad Prism Stili (Beyaz Arka Plan, Siyah Çerçeve)
    fig.update_layout(
        template="simple_white",
        showlegend=False,
        yaxis_title=y_label,
        xaxis_title="",
        title_font=dict(size=14, family="Arial Black"),
        margin=dict(l=40, r=40, t=60, b=40)
    )
    
    # P Değerini Grafiğe Ekleme (Annotation)
    if p_val_text:
        # En yüksek değeri bulup biraz üstüne yazalım
        y_max = df['Değer'].max()
        fig.add_annotation(
            x=2, # Vaka Grubu (Index 2)
            y=y_max,
            text=p_val_text,
            showarrow=True,
            arrowhead=2,
            arrowsize=1,
            arrowwidth=2,
            arrowcolor="black",
            yshift=10
        )
        
    return fig

# --- ARAYÜZ DÜZENİ (LAYOUT) ---
st.subheader("📊 İmmünolojik Karşılaştırma Grafikleri")

col1, col2 = st.columns(2)

with col1:
    st.plotly_chart(create_prism_plot(df_ctla4_dim, "% Ekspresyon", "CD56dim CTLA-4+ (Sitotoksik)", "p=0.036 (vs CMV-)"), use_container_width=True)
    st.plotly_chart(create_prism_plot(df_nkg2a, "% Ekspresyon", "CD56dim NKG2A (İnhibitör)", "p=0.028 (vs CMV-)"), use_container_width=True)

with col2:
    st.plotly_chart(create_prism_plot(df_ctla4_bright, "% Ekspresyon", "CD56bright CTLA-4+ (Sitokin)", "p=0.005 (vs CMV+)"), use_container_width=True)
    st.plotly_chart(create_prism_plot(df_nk, "% Oran", "Total NK Hücre Oranı", "Anlamlı Fark Yok"), use_container_width=True)

# --- VERİ TABLOSU ---
st.divider()
st.subheader("📋 Tez Veri Özeti")
st.markdown("Aşağıdaki veriler, tezdeki **Tablo 2, 3 ve 4**'ten alınmış orijinal ortalama değerlerdir.")

ozet_data = {
    'Parametre': ['CD56dim CTLA-4', 'CD56bright CTLA-4', 'CD56dim NKG2A', 'Total NK Oranı'],
    'CMV (-) Ort.±SS': ['0.63 ± 0.67', '6.4 ± 4.0', '49.3 ± 10.2', '9.9 ± 4.2'],
    'CMV (+) Ort.±SS': ['0.72 ± 0.58', '3.8 ± 2.4', '36.1 ± 18.9', '11.3 ± 5.0'],
    'Vaka Grubu Ort.±SS': ['2.05 ± 1.51', '8.5 ± 4.4', '34.3 ± 16.7', '11.2 ± 7.7'],
    'İstatistiksel Sonuç': ['Vaka Grubunda Artmış (p=0.036)', 'Vaka Grubunda Artmış (p=0.020)', 'Vaka Grubunda Azalmış (p<0.05)', 'Fark Yok']
}
st.dataframe(pd.DataFrame(ozet_data), use_container_width=True)

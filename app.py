import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd

# ---------------------------------------------------------
# 1. AYARLAR VE STİL (Brocan'ın Hatasız Prism Stili)
# ---------------------------------------------------------
# Stil ayarlarını güvenli modda açıyoruz
try:
    sns.set_style("ticks")
except:
    pass 

# Font ve Çizgi Kalınlıkları
plt.rcParams['font.family'] = 'sans-serif'
# Arial yoksa bile çalışsın diye yedek fontlar ekledim
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'Liberation Sans', 'sans-serif']
plt.rcParams['axes.linewidth'] = 1.5
plt.rcParams['xtick.major.width'] = 1.5
plt.rcParams['ytick.major.width'] = 1.5

# Renk Paleti (Gri -> Açık Mavi -> Koyu Lacivert)
prism_palette = ["#E0E0E0", "#90CAF9", "#0D47A1"] 
groups = ['CMV (-)', 'CMV (+)', 'Vaka Grubu']
n_samples = 11

# ---------------------------------------------------------
# 2. VERİ ÜRETME MOTORU (Simülasyon)
# ---------------------------------------------------------
def generate_data(mean, sd, n=11):
    """Ortalama ve Standart Sapma'dan sentetik veri üretir."""
    # Negatif değer çıkmasını engelliyoruz
    data = np.random.normal(mean, sd, n)
    return np.clip(data, 0, None)

# PDF'ten Alınan Veriler (Mean, SD)
data_map = {
    # --- GRUP 1: GENEL LENFOSİT & NK ---
    "Lenfosit Kapısı CD3+ T Hücre": [(74.0, 4.3), (73.9, 5.6), (67.3, 12.4)],
    "Lenfosit Kapısı NK Hücre Oranı": [(9.9, 4.2), (11.3, 5.0), (11.2, 7.7)],
    "CD3- Total NK Hücre Oranı": [(43.9, 14.0), (47.6, 15.5), (49.5, 17.9)],
    
    # --- GRUP 2: CD56dim (SİTOTOKSİK) ---
    "CD56dim Sitotoksik NK Alt Grubu": [(86.0, 6.5), (81.0, 22.0), (77.4, 24.4)],
    "CD56dim PD1+": [(1.00, 0.96), (5.11, 11.17), (4.20, 4.74)],
    "CD56dim CTLA-4+": [(0.63, 0.67), (0.72, 0.58), (2.05, 1.51)],
    "CD56dim NKG2A": [(49.3, 10.2), (36.1, 18.9), (34.3, 16.7)],
    "CD56dim NKG2D": [(1.40, 1.04), (0.85, 0.68), (1.07, 0.78)],
    "CD56dim LAG3": [(0.94, 1.00), (0.54, 0.86), (1.15, 1.74)],

    # --- GRUP 3: CD56bright (SİTOKİN ÜRETEN) ---
    "CD56bright Sitokin Üreten NK": [(12.9, 6.4), (16.7, 22.3), (20.2, 23.6)],
    "CD56bright PD1": [(3.0, 2.9), (10.2, 20.0), (8.5, 6.7)],
    "CD56bright CTLA-4": [(6.4, 4.0), (3.8, 2.4), (8.5, 4.4)],
    "CD56bright NKG2A": [(80.3, 14.6), (69.1, 27.9), (61.9, 23.0)],
    "CD56bright NKG2D": [(2.6, 1.5), (4.2, 2.3), (3.0, 2.1)],
    "CD56bright LAG3": [(2.6, 1.9), (1.3, 1.4), (1.6, 1.4)]
}

# ---------------------------------------------------------
# 3. ÇİZİM FONKSİYONU
# ---------------------------------------------------------
# Global Seed (Her çalıştırmada aynı sonucu versin diye)
np.random.seed(42)

# 5 Satır x 3 Sütunluk Alan
fig, axes = plt.subplots(5, 3, figsize=(18, 25))
axes = axes.flatten()

for i, (title, stats) in enumerate(data_map.items()):
    ax = axes[i]
    
    # Verileri Hazırla
    g1 = generate_data(*stats[0], n_samples)
    g2 = generate_data(*stats[1], n_samples)
    g3 = generate_data(*stats[2], n_samples)
    
    df = pd.DataFrame({
        'Grup': groups * n_samples,
        'Değer': np.concatenate([g1, g2, g3])
    })
    
    # 1. Kutu Grafiği (Boxplot)
    sns.boxplot(x="Grup", y="Değer", data=df, ax=ax, 
                palette=prism_palette, width=0.5, linewidth=1.5, 
                showfliers=False, whis=1.5)
    
    # 2. Nokta Grafiği (Stripplot)
    sns.stripplot(x="Grup", y="Değer", data=df, ax=ax, 
                  color="black", size=5, jitter=0.15, alpha=0.6)
    
    # Başlık ve Eksenler
    ax.set_title(title, fontweight='bold', fontsize=11, pad=10)
    ax.set_xlabel("")
    # Sadece sol sütuna Y ekseni etiketi koy
    ax.set_ylabel("% Ekspresyon" if i % 3 == 0 else "")
    
    # Çerçeveleri Temizle
    sns.despine(ax=ax) 
    
    # --- ANLAMLILIK ÇİZGİLERİ (Significance Bars) ---
    y_max = df['Değer'].max()
    offset = y_max * 0.1 # Çubuğun ne kadar yukarıda olacağı
    
    # 1. CD56dim CTLA-4+ (Vaka grubunda artış)
    if "CD56dim CTLA-4+" in title:
        # Çizgi çiz (x=0 ile x=2 arası yani CMV- ile Vaka arası)
        ax.plot([0, 0, 2, 2], [y_max+offset, y_max+offset*2, y_max+offset*2, y_max+offset], lw=1.5, c='k')
        # Yazı ekle
        ax.text(1, y_max+offset*2.2, "* p=0.036", ha='center', fontsize=9, fontweight='bold')

    # 2. CD56bright CTLA-4 (Vaka grubunda artış)
    if "CD56bright CTLA-4" in title:
        # Çizgi çiz (x=1 ile x=2 arası yani CMV+ ile Vaka arası)
        ax.plot([1, 1, 2, 2], [y_max+offset, y_max+offset*2, y_max+offset*2, y_max+offset], lw=1.5, c='k')
        ax.text(1.5, y_max+offset*2.2, "* p=0.020", ha='center', fontsize=9, fontweight='bold')
        
    # 3. CD56dim NKG2A (Vaka grubunda düşüş)
    if "CD56dim NKG2A" in title:
         ax.plot([0, 0, 2, 2], [y_max+offset, y_max+offset*2, y_max+offset*2, y_max+offset], lw=1.5, c='k')
         ax.text(1, y_max+offset*2.2, "* p<0.05", ha='center', fontsize=9, fontweight='bold')

# Düzeni Sıkılaştır
plt.tight_layout()

# DOSYAYI KAYDET (Bu satır hayat kurtarır!)
plt.savefig('cmv_analiz_sonuc.png', dpi=300, bbox_inches='tight')
print("Grafik 'cmv_analiz_sonuc.png' olarak başarıyla kaydedildi!")

# Ekranda Göster (Mümkünse)
plt.show()

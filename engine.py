import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

class FinancialRiskAnalyzer:
    """
    Financial Risk Analytics Engine
    
    Finansal tabloları okuyarak:
    - Finansal oranları hesaplar
    - Trend analizi ve lineer skorlama yapar
    - Sektör benchmark karşılaştırması ve görselleştirme sunar
    - Stres Testi (Senaryo Simülasyonu) uygular
    """

    GEREKLI_SATIRLAR = [
        "Dönen Varlıklar", "Kısa Vadeli Yükümlülükler",
        "Toplam Yükümlülükler", "Toplam Özkaynaklar",
        "Net Dönem Kârı (Zararı)", "Hasılat",
        "Esas Faaliyet Kârı (Zararı)"
    ]

    def __init__(self, file_path):
        self.file_path = file_path

        self.skor_agirliklari = {"cari": 0.25, "borc": 0.25, "netkar": 0.15, "favok": 0.35}
        self.esikler = {
            "Cari Oran":      {"alt": 1.0,  "ust": 1.5,  "ters": False},
            "Borç/Özkaynak":  {"alt": 1.0,  "ust": 2.0,  "ters": True},
            "Net Kar Marjı":  {"alt": 0.05, "ust": 0.10, "ters": False},
            "FAVÖK Marjı":    {"alt": 0.05, "ust": 0.15, "ters": False}
        }
        self.sektor_benchmark = {
            "Cari Oran": 1.6, "Borç/Özkaynak": 1.2,
            "Net Kar Marjı": 0.12, "FAVÖK Marjı": 0.18
        }

        self.df = self._load_data()
        self.analiz_tablosu = pd.DataFrame()
        self.skor_ozet = pd.DataFrame()

    def _load_data(self):
        """Excel verisini yükler ve temizler."""
        df = pd.read_excel(self.file_path, header=8)
        df = df.set_index("FİNANSAL DURUM TABLOSU")
        df = df.apply(pd.to_numeric, errors="coerce")

        return df

    def rasyolari_hesapla(self):
        """Temel finansal oranları hesaplar."""
        donen       = self.df.loc["Dönen Varlıklar"]
        kisa_borc   = self.df.loc["Kısa Vadeli Yükümlülükler"]
        toplam_borc = self.df.loc["Toplam Yükümlülükler"]
        ozsermaye   = self.df.loc["Toplam Özkaynaklar"]
        net_kar     = self.df.loc["Net Dönem Kârı (Zararı)"]
        hasilat     = self.df.loc["Hasılat"]
        favok       = self.df.loc["Esas Faaliyet Kârı (Zararı)"]

        self.analiz_tablosu = pd.DataFrame({
            "Cari Oran":     donen / kisa_borc,
            "Borç/Özkaynak": toplam_borc / ozsermaye,
            "Net Kar Marjı": net_kar / hasilat,
            "FAVÖK Marjı":   favok / hasilat
        })
        return self.analiz_tablosu

    def _puanla(self, x, alt, ust, ters=False):
        """Skaler değeri 0–100 arasına lineer olarak normalize eder."""
        if not ters:
            if x <= alt: return 0.0
            if x >= ust: return 100.0
            return (x - alt) / (ust - alt) * 100
        else:
            if x >= ust: return 0.0
            if x <= alt: return 100.0
            return (ust - x) / (ust - alt) * 100

    def _skor_motoru(self, series, alt, ust, ters=False):
        """Zaman serisi için ağırlıklı skor üretir."""
        son_yil   = series.iloc[-1]
        ortalama  = series.mean()
        trend     = float(series.iloc[-1] - series.iloc[0])

        son_yil_puan  = self._puanla(son_yil,  alt, ust, ters)
        ortalama_puan = self._puanla(ortalama, alt, ust, ters)

        if trend > 0:
            trend_puan = 100.0 if not ters else 0.0
        elif trend == 0:
            trend_puan = 50.0
        else:
            trend_puan = 0.0 if not ters else 100.0

        final_skor = (0.4 * son_yil_puan) + (0.4 * trend_puan) + (0.2 * ortalama_puan)

        return {
            "Son Yıl":    son_yil,
            "Ortalama":   ortalama,
            "Trend":      trend,
            "Final Skor": final_skor
        }

    def _risk_kategorisi(self, skor):
        """Genel skoru metin kategorisine çevirir."""
        if skor >= 80:   return "LOW RISK"
        elif skor >= 60: return "MEDIUM RISK"
        else: return "HIGH RISK"

    def firma_skoru_uret(self):
        """Tüm oranları analiz edip genel skoru üretir."""
        if self.analiz_tablosu.empty:
            self.rasyolari_hesapla()
            
        e = self.esikler
        cari   = self._skor_motoru(self.analiz_tablosu["Cari Oran"],     e["Cari Oran"]["alt"],     e["Cari Oran"]["ust"],     e["Cari Oran"]["ters"])
        borc   = self._skor_motoru(self.analiz_tablosu["Borç/Özkaynak"], e["Borç/Özkaynak"]["alt"], e["Borç/Özkaynak"]["ust"], e["Borç/Özkaynak"]["ters"])
        netkar = self._skor_motoru(self.analiz_tablosu["Net Kar Marjı"], e["Net Kar Marjı"]["alt"],  e["Net Kar Marjı"]["ust"],  e["Net Kar Marjı"]["ters"])
        favok  = self._skor_motoru(self.analiz_tablosu["FAVÖK Marjı"],   e["FAVÖK Marjı"]["alt"],    e["FAVÖK Marjı"]["ust"],    e["FAVÖK Marjı"]["ters"])

        skorlar = {"cari": cari, "borc": borc, "netkar": netkar, "favok": favok}

        self.skor_ozet = pd.DataFrame({
            "Oran":       ["Cari", "Borç/Özkaynak", "Net Kar", "FAVÖK"],
            "Son Yıl":    [s["Son Yıl"]    for s in skorlar.values()],
            "Ortalama":   [s["Ortalama"]   for s in skorlar.values()],
            "Trend":      [s["Trend"]      for s in skorlar.values()],
            "Final Skor": [s["Final Skor"] for s in skorlar.values()]
        })

        genel_skor = sum(self.skor_agirliklari[k] * skorlar[k]["Final Skor"] for k in self.skor_agirliklari)
        risk = self._risk_kategorisi(genel_skor)

        return genel_skor, risk, self.skor_ozet

    def benchmark_karsilastirma(self):
        """Şirketin son yıl rasyolarını sektörle karşılaştırır."""
        satirlar = []
        for oran in self.analiz_tablosu.columns:
            sirket_degeri = self.analiz_tablosu[oran].iloc[-1]
            benchmark = self.sektor_benchmark.get(oran, np.nan)
            fark = sirket_degeri - benchmark

            ters = self.esikler.get(oran, {}).get("ters", False)

            if ters:
                if fark < 0:
                    durum = "İyi"
                elif fark < 0.5:
                    durum = "Dikkat"
                else:
                    durum = "Kötü"
            else:
                if fark > 0:
                    durum = "İyi"
                elif fark > -0.05:
                    durum = "Dikkat"
                else:
                    durum = "Kötü"

            satirlar.append({
                "Oran":      oran,
                "Şirket":    round(sirket_degeri, 4),
                "Benchmark": round(benchmark, 4),
                "Fark":      round(fark, 4),
                "Durum":     durum
            })
        return pd.DataFrame(satirlar)

    def senaryo_simule_et(self, hasilat_degisim_yuzdesi=0, borc_degisim_yuzdesi=0):
        """
        Belirlenen makroekonomik veya operasyonel şokları son yıl verisine
        uygular ve yeni bir risk skoru üretir. Orijinal verileri bozmaz.
        """
        son_yil = self.df.columns[-1]

        orijinal_hasilat = self.df.at["Hasılat", son_yil]
        orijinal_borc    = self.df.at["Kısa Vadeli Yükümlülükler", son_yil]

        self.df.at["Hasılat", son_yil]                    = orijinal_hasilat * (1 + hasilat_degisim_yuzdesi / 100)
        self.df.at["Kısa Vadeli Yükümlülükler", son_yil]  = orijinal_borc    * (1 + borc_degisim_yuzdesi    / 100)

        self.rasyolari_hesapla()
        sim_skor, sim_risk, _ = self.firma_skoru_uret()

        # Orijinale geri dön
        self.df.at["Hasılat", son_yil]                   = orijinal_hasilat
        self.df.at["Kısa Vadeli Yükümlülükler", son_yil] = orijinal_borc
        self.rasyolari_hesapla()

        return sim_skor, sim_risk

    def benchmark_grafik(self, return_fig=False):
        """Şirket vs sektör benchmark bar grafiği çizer."""
        df_bench = self.benchmark_karsilastirma()
        x = np.arange(len(df_bench))
        width = 0.35

        fig, ax = plt.subplots(figsize=(10, 5))
        ax.bar(x - width / 2, df_bench["Şirket"],    width, label="Şirket",    color="red", alpha=0.85)
        ax.bar(x + width / 2, df_bench["Benchmark"], width, label="Benchmark", color="blue", alpha=0.85)
        ax.set_xticks(x)
        ax.set_xticklabels(df_bench["Oran"], fontsize=11)
        ax.set_ylabel("Değer")
        ax.set_title("Şirket vs Sektör Benchmark", fontsize=13, fontweight="bold")
        ax.legend()
        ax.grid(True, axis="y", linestyle="--", alpha=0.5)
        plt.tight_layout()

        if return_fig: return fig
        plt.show()

    def trend_grafikleri(self, return_fig=False):
        """Her oran için zaman serisi trend grafikleri çizer."""
        fig, axes = plt.subplots(2, 2, figsize=(10, 6))
        fig.suptitle("Financial Ratio Trends", fontweight="bold")
        for ax, kolon in zip(axes.flat, self.analiz_tablosu.columns):
            self.analiz_tablosu[kolon].plot(ax=ax, marker="o")
            ax.set_title(kolon)
            ax.grid(True, linestyle="--", alpha=0.5)
        plt.tight_layout()

        if return_fig: return fig
        plt.show()

    def excel_rapor_olustur(self, dosya_adi="Finansal_Rapor.xlsx"):
        """Tüm analizleri tek bir Excel dosyasında farklı sekmelere kaydeder."""
        genel_skor, risk, _ = self.firma_skoru_uret()

        ozet_df = pd.DataFrame({
            "Metrik": ["Genel Sağlık Skoru", "Risk Kategorisi"],
            "Değer":  [round(genel_skor, 2), risk]
        })
        benchmark_df = self.benchmark_karsilastirma()

        with pd.ExcelWriter(dosya_adi, engine="xlsxwriter") as writer:
            ozet_df.to_excel(writer,          sheet_name="Yönetici_Özeti",   index=False)
            self.skor_ozet.to_excel(writer,   sheet_name="Risk_Skorları",    index=False)
            benchmark_df.to_excel(writer,     sheet_name="Sektör_Benchmark", index=False)


# ==========================================
# --- STREAMLIT ARAYÜZÜ (WEB DASHBOARD) ---
# ==========================================

def run_streamlit_app():
    st.set_page_config(page_title="Finansal Risk Motoru", layout="wide")
    st.title("Finansal Risk Karar Motoru")
    st.markdown("İstatistiksel trend analizi, lineer skorlama ve senaryo simülasyonlu finansal check-up uygulaması.")
    st.divider()

    with st.sidebar:
        st.header("Veri Girişi")
        uploaded_file = st.file_uploader("Bilançoyu Yükleyin (Excel)", type=["xlsx"])
        st.info("KAP formatına uygun Excel dosyası yükleyiniz.")

    if uploaded_file is not None:
        try:
            analizor = FinancialRiskAnalyzer(uploaded_file)
            genel_skor, risk, skor_tablosu = analizor.firma_skoru_uret()
            benchmark_tablosu = analizor.benchmark_karsilastirma()

            st.subheader("Yönetici Özeti")
            col1, col2 = st.columns(2)
            col1.metric(label="Mevcut Genel Sağlık Skoru", value=f"{genel_skor:.2f} / 100")

            renk = "green" if genel_skor >= 80 else "orange" if genel_skor >= 60 else "red"
            col2.markdown(f"### Mevcut Risk Kategorisi: <span style='color:{renk}'>{risk}</span>", unsafe_allow_html=True)

            st.divider()

            # --- SİMÜLASYON ---
            st.subheader("Senaryo Simülasyonu (Stres Testi)")
            st.markdown("Makroekonomik şokların veya operasyonel dalgalanmaların şirketin risk skoruna etkisini test edin.")

            sim_col1, sim_col2 = st.columns(2)
            hasilat_soku = sim_col1.slider("Hasılat Değişimi (%)",           min_value=-50, max_value=50, value=0, step=5)
            borc_soku    = sim_col2.slider("Kısa Vadeli Borç Değişimi (%)",  min_value=-50, max_value=50, value=0, step=5)

            if hasilat_soku != 0 or borc_soku != 0:
                sim_skor, sim_risk = analizor.senaryo_simule_et(
                    hasilat_degisim_yuzdesi=hasilat_soku,
                    borc_degisim_yuzdesi=borc_soku
                )
                fark = sim_skor - genel_skor
                sim_renk = "green" if sim_skor >= 80 else "orange" if sim_skor >= 60 else "red"

                res_col1, res_col2 = st.columns(2)
                res_col1.metric("Şok Sonrası Yeni Sağlık Skoru", f"{sim_skor:.2f} / 100", f"{fark:.2f} Puan")
                res_col2.markdown(f"### Yeni Risk Kategorisi: <span style='color:{sim_renk}'>{sim_risk}</span>", unsafe_allow_html=True)
            else:
                st.info("Simülasyonu başlatmak için yukarıdaki kaydırma çubuklarını hareket ettirin.")

            st.divider()

            st.subheader("Veri Çıktıları")
            tab1, tab2 = st.tabs(["Risk Skorları", "Sektör Benchmark"])
            with tab1: st.dataframe(skor_tablosu,    use_container_width=True)
            with tab2: st.dataframe(benchmark_tablosu, use_container_width=True)

            st.divider()

            st.subheader("Görselleştirmeler")
            st.pyplot(analizor.benchmark_grafik(return_fig=True))
            st.pyplot(analizor.trend_grafikleri(return_fig=True))

        except Exception as e:
            st.error(f"Dosya analiz edilirken bir hata oluştu: {e}")
    else:
        st.info("Lütfen sol menüden analize başlamak için Excel dosyanızı yükleyin.")


# ==========================================
# --- IDE / TERMİNAL ÇALIŞTIRMA BÖLÜMÜ ---
# ==========================================

if __name__ == "__main__":
    import sys

    if "streamlit" in sys.argv[0]:
        run_streamlit_app()
    else:
        try:
            analizor = FinancialRiskAnalyzer("aselsan.xlsx")

            genel_skor, risk, skor_tablosu = analizor.firma_skoru_uret()
            benchmark_tablosu = analizor.benchmark_karsilastirma()

            print("RİSK SKORLARI")
            print(skor_tablosu)

            print("SEKTÖR BENCHMARK")
            print(benchmark_tablosu)

            print(f"GENEL SAĞLIK SKORU: {genel_skor:.2f} / 100")
            print(f"RİSK KATEGORİSİ: {risk}")

            # Simülasyon testi (isteğe bağlı):
            #sim_skor, sim_risk = analizor.senaryo_simule_et(hasilat_degisim_yuzdesi=-20, borc_degisim_yuzdesi=10)
            #print(f"\n[SİMÜLASYON] Hasılat -%20, Borç +%10 → YENİ SKOR: {sim_skor:.2f} ({sim_risk})")

            analizor.trend_grafikleri()
            analizor.benchmark_grafik()

        except FileNotFoundError:
            print("Uyarı: 'dosya' bulunamadı.")

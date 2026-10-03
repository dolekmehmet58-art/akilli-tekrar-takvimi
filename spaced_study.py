import streamlit as st
import datetime
import json
import os

# ==========================================
# 1. VERİTABANI / DOSYA YÖNETİMİ
# ==========================================
DB_FILE = "study_data.json"

def load_data():
    """Kayıtlı ders verilerini JSON dosyasından yükler."""
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_data(data):
    """Gözden geçirilen verileri JSON dosyasına kaydeder."""
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# ==========================================
# 2. SAYFA VE ARAYÜZ AYARLARI
# ==========================================
st.set_page_config(
    page_title="Akıllı Tekrar Takvimi",
    page_icon="📚",
    layout="wide"
)

st.title("📚 Aralıklı Tekrar (Spaced Repetition) Tabanlı Çalışma Takvimi")
st.caption("Ebbinghaus Unutma Eğrisi ve Algoritmik Ders Takip Sistemi")
st.markdown("**Geliştiren:** Mehmet İhsan | *TÜBİTAK Yazılım Projesi*")

st.divider()

# Veriyi Yükle
topics = load_data()
today_str = datetime.date.today().isoformat()

# ==========================================
# 3. YENİ KONU EKLENEN YAN PANEL
# ==========================================
st.sidebar.header("➕ Yeni Konu Çalışması Ekle")

with st.sidebar.form("add_topic_form"):
    course_name = st.selectbox("Ders Seçin:", ["Matematik", "Fizik", "Kimya", "Biyoloji", "Türkçe", "Tarih", "Coğrafya"])
    topic_title = st.text_input("Konu Adı:", placeholder="Örn: İkinci Dereceden Denklemler")
    difficulty = st.select_slider(
        "Konu Zorluk / Anlama Düzeyi:",
        options=["Zor (Çok Unutulabilir)", "Orta (Normal)", "Kolay (İyi Anlaşıldı)"]
    )
    
    submitted = st.form_submit_button("Çalışmayı Kaydet")

if submitted and topic_title:
    # Zorluk derecesine göre ilk tekrar aralığı (gün cinsinden)
    interval = 1 if "Zor" in difficulty else (3 if "Orta" in difficulty else 5)
    next_review = datetime.date.today() + datetime.timedelta(days=interval)
    
    new_entry = {
        "id": len(topics) + 1,
        "course": course_name,
        "topic": topic_title,
        "added_date": today_str,
        "last_review": today_str,
        "next_review": next_review.isoformat(),
        "interval_days": interval,
        "review_count": 0,
        "difficulty": difficulty
    }
    
    topics.append(new_entry)
    save_data(topics)
    st.sidebar.success(f"'{topic_title}' başarıyla eklendi! İlk tekrar: {next_review.strftime('%d.%m.%Y')}")
    st.rerun()

# ==========================================
# 4. BUGÜNÜN TEKRAR LİSTESİ VE METRİKLER
# ==========================================

# Bugün tekrar edilmesi gereken konuları filtrele
due_topics = [t for t in topics if t["next_review"] <= today_str]
upcoming_topics = [t for t in topics if t["next_review"] > today_str]

col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Toplam Takip Edilen Konu", value=len(topics))
with col2:
    st.metric(label="⚠️ Bugün Tekrar Edilecekler", value=len(due_topics), delta_color="inverse")
with col3:
    st.metric(label="✅ İleriki Tarihli Tekrarlar", value=len(upcoming_topics))

st.divider()

# ==========================================
# 5. SEKMELER (GÖREVLER VE TÜM LİSTE)
# ==========================================
tab1, tab2 = st.tabs(["🔔 Bugünün Tekrar Görevleri", "📋 Tüm Çalışma Geçmişi"])

with tab1:
    st.subheader("🔔 Bugün Tamamlanması Gereken Tekrarlar")
    
    if not due_topics:
        st.info("🎉 Harika! Bugün tekrar etmen gereken hiçbir konu kalmadı.")
    else:
        for idx, item in enumerate(due_topics):
            with st.expander(f"📌 [{item['course']}] - {item['topic']} (Son Tekrar: {item['last_review']})", expanded=True):
                st.write(f"**Ekleme Tarihi:** {item['added_date']} | **Tekrar Sayısı:** {item['review_count']}")
                st.write(f"**Son Değerlendirme:** {item['difficulty']}")
                
                col_btn1, col_btn2, col_btn3 = st.columns(3)
                
                # Tekrar sonrası bildirim durumları
                if col_btn1.button("🔴 Zorlandım (1 Gün Sonra Tekrar)", key=f"hard_{item['id']}"):
                    item['interval_days'] = 1
                    item['next_review'] = (datetime.date.today() + datetime.timedelta(days=1)).isoformat()
                    item['last_review'] = today_str
                    item['review_count'] += 1
                    item['difficulty'] = "Zor (Çok Unutulabilir)"
                    save_data(topics)
                    st.success("Tekrar kaydedildi! Yarın tekrar hatırlatılacak.")
                    st.rerun()
                    
                if col_btn2.button("🟡 Normaldi (3 Gün Sonra Tekrar)", key=f"mid_{item['id']}"):
                    item['interval_days'] = int(item['interval_days'] * 1.8) + 2
                    item['next_review'] = (datetime.date.today() + datetime.timedelta(days=item['interval_days'])).isoformat()
                    item['last_review'] = today_str
                    item['review_count'] += 1
                    item['difficulty'] = "Orta (Normal)"
                    save_data(topics)
                    st.success(f"Tekrar kaydedildi! Sonraki tekrar {item['interval_days']} gün sonra.")
                    st.rerun()

                if col_btn3.button("🟢 Çok Kolaydı (7 Gün Sonra Tekrar)", key=f"easy_{item['id']}"):
                    item['interval_days'] = int(item['interval_days'] * 2.5) + 5
                    item['next_review'] = (datetime.date.today() + datetime.timedelta(days=item['interval_days'])).isoformat()
                    item['last_review'] = today_str
                    item['review_count'] += 1
                    item['difficulty'] = "Kolay (İyi Anlaşıldı)"
                    save_data(topics)
                    st.success(f"Tekrar kaydedildi! Sonraki tekrar {item['interval_days']} gün sonra.")
                    st.rerun()

with tab2:
    st.subheader("📋 Tüm Konular ve Gelecek Tekrar Tarihleri")
    
    if topics:
        # Tablo halinde gösterim
        table_data = []
        for t in topics:
            table_data.append({
                "Ders": t["course"],
                "Konu": t["topic"],
                "Son Tekrar": t["last_review"],
                "Gelecek Tekrar": t["next_review"],
                "Tekrar Sayısı": t["review_count"],
                "Durum": "⚠️ BUGÜN!" if t["next_review"] <= today_str else "⏳ Beklemede"
            })
        st.dataframe(table_data, use_container_width=True)
        
        if st.button("🗑️ Tüm Verileri Temizle"):
            save_data([])
            st.success("Veritabanı sıfırlandı.")
            st.rerun()
    else:
        st.write("Henüz eklenmiş bir konu bulunmuyor.")
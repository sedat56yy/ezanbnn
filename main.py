

# -*- coding: utf-8 -*-
# ╔══════════════════════════════════════════════╗
# ║      🕌  EZAN VAKTİ TELEGRAM BOTU  🕌        ║
# ║  Kurucu : @NikeCheatYeniden                  ║
# ║  Kanal  : @nikestoretr                       ║
# ╚══════════════════════════════════════════════╝
# Kurulum: pip install requests pytz

import json
import os
import threading
import time
import re
from datetime import datetime, timedelta
import requests

BOT_TOKEN   = os.environ.get("BOT_TOKEN", "8566312208:AAEFaLcdKsTnxe2zIqvQggS9riRcoIyeaAc")
ADMIN_IDS   = [583994825]
DATA_FILE   = "ezan_data.json"
LOG_FILE    = "ezan_log.json"
KANAL_URL   = "https://t.me/nikestoretr"
KANAL_LABEL = "📢 Kanal"
KURUCU_URL  = "https://t.me/NikeCheatYeniden"
KURUCU_LABEL= "👤 Kurucu"
BOT_LOGO    = "https://i.hizliresim.com/ojtpq9s.jpg"
SPAM_SURE   = 5
SPAM_CACHE  = {}
GNDR        = {}
_VAKIT_CACHE= {}

# ─── SPAM KORUMASI ───────────────────────────────
SPAM_SURE    = 5          # saniye — komutlar arası minimum süre
SPAM_CACHE   = {}         # uid → son_komut_timestamp

# ╔══════════════════════════════════════════════╗
# ║  FOTOĞRAF LİNKLERİ — konuma göre foto gönder ║
# ╚══════════════════════════════════════════════╝
FOTO = {
    "TR": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b3/Sultan_Ahmed_mosque.jpg/800px-Sultan_Ahmed_mosque.jpg",
    "SA": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b9/Masjid_Al_Haram%2C_Mecca.jpg/800px-Masjid_Al_Haram%2C_Mecca.jpg",
    "EG": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/af/All_Gizah_Pyramids.jpg/800px-All_Gizah_Pyramids.jpg",
    "ID": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4d/Istiqlal_mosque%2C_Jakarta%2C_December_2020.jpg/800px-Istiqlal_mosque%2C_Jakarta%2C_December_2020.jpg",
    "MY": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/67/Masjid_Putra%2C_Putrajaya.jpg/800px-Masjid_Putra%2C_Putrajaya.jpg",
    "PK": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Badshahi_Mosque_front_picture.jpg/800px-Badshahi_Mosque_front_picture.jpg",
    "IR": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0d/Imam_Mosque_Isfahan.jpg/800px-Imam_Mosque_Isfahan.jpg",
    "DE": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1e/DITIB-Zentralmoschee-K%C3%B6ln.jpg/800px-DITIB-Zentralmoschee-K%C3%B6ln.jpg",
    "DEFAULT": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/89/Hagia_Sophia_Mars_2013.jpg/800px-Hagia_Sophia_Mars_2013.jpg",
}

# ╔══════════════════════════════════════════════╗
# ║  YASAK / MUTE VERİSİ                         ║
# ╚══════════════════════════════════════════════╝
BAN_DATA  = {}   # uid -> {"banned": True/False, "mute_until": timestamp or None}

# ═══════════════════════════════════════════════
#  LOG
# ═══════════════════════════════════════════════
def log_yukle():
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE,"r",encoding="utf-8") as f:
                return json.load(f)
        except: pass
    return {"events":[]}

def log_kaydet(lg):
    with open(LOG_FILE,"w",encoding="utf-8") as f:
        json.dump(lg, f, ensure_ascii=False, indent=2)

def log_ekle(olay, uid, isim, detay=""):
    global LOG_KANAL
    try:
        lg = log_yukle()
        lg["events"].append({
            "zaman": datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
            "olay": olay, "uid": uid, "isim": isim, "detay": detay
        })
        if len(lg["events"]) > 500:
            lg["events"] = lg["events"][-500:]
        log_kaydet(lg)
        # Kanala log gönder — tüm komutlar ve olaylar
        if LOG_KANAL:
            olay_emoji = {
                "START": "🚀", "VAKITLER": "🕌", "YARIN": "📅", "HAFTALIK": "📆",
                "KONUM": "📍", "UYARI": "⏰", "API": "🔧", "DİL": "🌐",
                "AYARLAR": "⚙️", "DURDUR": "🔕", "DEVAM": "🔔",
                "BAN": "🚫", "UBAN": "✅", "MUTE": "🔇", "UMUTE": "🔊",
                "DUYURU": "📢", "ADMIN": "🔐", "BOT_BASLADI": "✅",
                "LOG_AYARLA": "📋", "SPAM": "⚠️", "SEHIR": "🏙️",
                "ILCE": "📍", "LOG_TEMIZLENDI": "🗑️", "GRUBA_EKLENDI": "👥",
            }.get(olay, "📝")
            isim_str = str(isim) if isim else "—"
            uid_str = str(uid) if uid else "—"
            detay_str = str(detay)[:200] if detay else "—"
            msg = (
                f"{olay_emoji} *LOG — {olay}*\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"👤 Kim   : {isim_str} (`{uid_str}`)\n"
                f"📝 Detay : {detay_str}\n"
                f"🕐 Zaman : `{datetime.now().strftime('%d.%m.%Y %H:%M:%S')}`\n"
                f"━━━━━━━━━━━━━━━━━━"
            )
            tg_post("sendMessage", {"chat_id": LOG_KANAL, "text": msg, "parse_mode": "Markdown"})
    except: pass

# ═══════════════════════════════════════════════
#  VERİ
# ═══════════════════════════════════════════════
def veri_yukle():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE,"r",encoding="utf-8") as f:
                return json.load(f)
        except: pass
    return {"k":{},"bugun":0,"tarih":"","toplam":0,"log_kanal":None,"ban":{}}

def veri_kaydet(v):
    with open(DATA_FILE,"w",encoding="utf-8") as f:
        json.dump(v, f, ensure_ascii=False, indent=2)

def kul_al(v, uid):
    k = str(uid)
    if k not in v["k"]:
        v["k"][k] = {
            "lang": None,
            "ulke_label": None, "ulke_kod": None,
            "sehir": None, "sehir_en": None,
            "ilce": None, "ilce_en": None,
            "lat": None, "lon": None,
            "dk": 15, "api": "auto", "aktif": True,
            "isim": "", "username": "",
            "kayit": datetime.now().strftime("%d.%m.%Y %H:%M"),
            "setup_step": "lang"   # lang → ulke → done
        }
    return v["k"][k]

def is_banned(uid):
    b = VERI.get("ban", {}).get(str(uid), {})
    if b.get("banned"): return True
    mu = b.get("mute_until")
    if mu and datetime.now().timestamp() < mu: return True
    return False

VERI = veri_yukle()
# Grup ayarları: VERI["gruplar"][chat_id_str] = {sehir, ilce, lat, lon, aktif_vakitler, aktif}
if "gruplar" not in VERI:
    VERI["gruplar"] = {}
GNDR = {}
_VAKIT_CACHE = {}   # uid_str → {"tarih": ..., "tm": ..., "tz": "Europe/Istanbul"}
# LOG_KANAL değerini veri dosyasından yükle
LOG_KANAL = VERI.get("log_kanal", None)

# ═══════════════════════════════════════════════
#  ÇOK DİLLİ METİNLER
# ═══════════════════════════════════════════════
DILLER = {
    "tr": "🇹🇷 Türkçe",
    "ar": "🇸🇦 العربية",
    "de": "🇩🇪 Deutsch",
    "fr": "🇫🇷 Français",
    "nl": "🇳🇱 Nederlands",
    "en": "🇬🇧 English",
    "ur": "🇵🇰 اردو",
    "id": "🇮🇩 Indonesia",
    "ms": "🇲🇾 Melayu",
    "ru": "🇷🇺 Русский",
    "az": "🇦🇿 Azərbaycanca",
    "bs": "🇧🇦 Bosanski",
    "sq": "🇦🇱 Shqip",
}

# Çok dilli /start hoşgeldin mesajı
HOSGELDIN_MULTI = (
    "🕌 *EZAN VAKTİ BOTU*\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    "🇹🇷 Lütfen dilinizi seçin\n"
    "🇸🇦 الرجاء اختيار لغتك\n"
    "🇩🇪 Bitte wähle deine Sprache\n"
    "🇫🇷 Choisissez votre langue\n"
    "🇳🇱 Kies uw taal\n"
    "🇬🇧 Please select your language\n"
    "🇵🇰 براہ کرم اپنی زبان منتخب کریں\n"
    "🇮🇩 Silakan pilih bahasa Anda\n"
    "🇲🇾 Sila pilih bahasa anda\n"
    "🇷🇺 Пожалуйста, выберите язык\n"
    "🇦🇿 Zəhmət olmasa dilinizi seçin\n"
    "🇧🇦 Molimo odaberite jezik\n"
    "🇦🇱 Ju lutem zgjidhni gjuhën\n\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "👤 @NikeCheatYeniden | 📢 @nikestoretr"
)

M = {
    "tr": {
        "hosgeldin":  "🌙 *Ezan Vakti Botuna Hoş Geldiniz!*\n\n✦ Lütfen dilinizi seçin:",
        "dil_ok":     "✅ Dil Türkçe olarak ayarlandı.",
        "ulke":       "🌍 *Ülkenizi seçin:*",
        "il":         "🏙️ *İl / Şehir seçin:*",
        "ilce":       "📍 *{s}* — İlçe seçin:",
        "yok":        "❌ Konum henüz ayarlanmamış!\n\n• /konum — Konum ayarla",
        "usor":       "⏰ *Kaç dakika öncesinde uyarı almak istersiniz?*",
        "uok":        "✅ Uyarı *{m} dakika* öncesi için ayarlandı.",
        "apisor":     "🔧 *API Seçin:*\n\n• 🕌 Diyanet — Türkiye için\n• 🌍 Aladhan — Tüm dünya\n• 🤖 Otomatik — Önerilen",
        "apiok":      "✅ API *{a}* olarak ayarlandı.",
        "dur":        "🔕 Uyarılar durduruldu.\n\n• /devam — Tekrar aç",
        "dev":        "🔔 Uyarılar tekrar açıldı!",
        "umsg":       "🔔 *EZAN UYARISI!*\n━━━━━━━━━━━━━━━━━━\n📍 {s} / {i}\n🕌 Vakit  : *{v}*\n⏱️ Kalan  : *{m} dakika*\n🕐 Saat   : `{t}`\n━━━━━━━━━━━━━━━━━━\n🤲 Hayırlı namazlar!\n👤 @NikeCheatYeniden | 📢 @nikestoretr",
        "bas":        "🕌 *NAMAZ VAKİTLERİ*\n━━━━━━━━━━━━━━━━━━\n📍 {s} / {i}\n📅 {d}\n━━━━━━━━━━━━━━━━━━\n\n",
        "im":  "🌙 İmsak  : `{t}`",
        "gu":  "☀️  Güneş  : `{t}`",
        "og":  "🌤️ Öğle   : `{t}`",
        "ik":  "🌇 İkindi : `{t}`",
        "ak":  "🌆 Akşam  : `{t}`",
        "ya":  "🌃 Yatsı  : `{t}`",
        "son": "\n\n⏭️ Sıradaki: *{v}* — `{t}`",
        "ayar": "⚙️ *AYARLARINIZ*\n━━━━━━━━━━━━━━━━━━\n🌍 Ülke   : {u}\n🏙️ Şehir  : {s}\n📍 İlçe   : {i}\n⏰ Uyarı  : {m} dk önce\n🔧 API    : {a}\n🌐 Dil    : Türkçe\n━━━━━━━━━━━━━━━━━━",
        "yard": (
            "📖 *KOMUT LİSTESİ*\n"
            "━━━━━━━━━━━━━━━━━━\n"
            "• /start — Botu başlat\n"
            "• /vakitler — Bugünün vakitleri\n"
            "• /yarin — Yarının vakitleri\n"
            "• /haftalik — Haftalık vakitler\n"
            "• /konum — Ülke / İl / İlçe seç\n"
            "• /uyari — Uyarı süresini ayarla\n"
            "• /api — API değiştir\n"
            "• /dil — Dil değiştir\n"
            "• /ayarlar — Mevcut ayarlar\n"
            "• /durdur — Uyarıları durdur\n"
            "• /devam — Uyarıları aç\n"
            "• /ozelgunler — Kandil & bayram\n"
            "• /istatistik — İstatistikler\n"
            "• /hakkinda — Bot hakkında\n"
            "━━━━━━━━━━━━━━━━━━\n"
            "🔧 *GRUP KOMUTU (Admin):*\n"
            "• /grubayarla — Gruba otomatik ezan bildirimi ekle\n"
            "  (Şehir seç, vakit seç, kaç dk önce uyarsın)\n"
            "━━━━━━━━━━━━━━━━━━\n"
            "👤 @NikeCheatYeniden | 📢 @nikestoretr"
        ),
        "hak": "🕌 *EZAN VAKTİ BOTU*\n━━━━━━━━━━━━━━━━━━\n👤 Kurucu : @NikeCheatYeniden\n📢 Kanal  : @nikestoretr\n\n🌍 Tüm ülkeler desteklenir\n🕌 Aladhan API (koordinat bazlı)\n🔔 Otomatik ezan uyarısı\n━━━━━━━━━━━━━━━━━━\n🤲 Hayırlı namazlar!",
        "grup": (
            "🕌 *EZAN VAKTİ BOTU GRUBA KATILDI!*\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Selam! Ben *Ezan Vakti Botu* 🤖\n"
            "Size günlük namaz vakitlerini bildiririm.\n\n"
            "🚀 *HIZLI BAŞLANGIÇ:*\n"
            "1️⃣ `/konum` — Şehir/İlçe seçin\n"
            "2️⃣ `/uyari` — Kaç dk önce uyarılayım?\n"
            "3️⃣ `/vakitler` — Bugünün vakitleri\n\n"
            "📋 *TÜM KOMUTLAR:*\n"
            "• `/vakitler` — Bugünün namaz vakitleri\n"
            "• `/yarin` — Yarının vakitleri\n"
            "• `/haftalik` — 7 günlük vakitler\n"
            "• `/konum` — Şehir/İlçe ayarla\n"
            "• `/uyari` — Ezan uyarı süresi (5-60 dk)\n"
            "• `/durdur` — Uyarıları durdur\n"
            "• `/devam` — Uyarıları aç\n"
            "• `/ayarlar` — Mevcut ayarları gör\n"
            "• `/ozelgunler` — İslami özel günler\n"
            "• `/grubayarla` — Grup ezan bildirimi (Admin)\n"
            "• `/hakkinda` — Bot hakkında\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "🌍 40+ ülke • 🕌 Koordinat bazlı doğru vakitler\n"
            "👤 @NikeCheatYeniden | 📢 @nikestoretr"
        ),
        "stat": "📊 *İSTATİSTİKLER*\n━━━━━━━━━━━━━━━━━━\n👥 Toplam kullanıcı : {t}\n✅ Aktif uyarı      : {a}\n🔔 Bugün gönderilen : {b}\n📨 Toplam uyarı     : {top}\n━━━━━━━━━━━━━━━━━━",
        "ad": {"Fajr":"İmsak","Sunrise":"Güneş","Dhuhr":"Öğle","Asr":"İkindi","Maghrib":"Akşam","Isha":"Yatsı"},
        "menu_bilgi": "🕌 *EZAN VAKTİ BOTU*\n━━━━━━━━━━━━━━━━━━\n📍 {s} / {i}\n━━━━━━━━━━━━━━━━━━",
        "konum_ok": "✅ *KONUM AYARLANDI!*\n━━━━━━━━━━━━━━━━━━\n🌍 Ülke  : {u}\n🏙️ Şehir : {s}\n📍 İlçe  : {i}\n━━━━━━━━━━━━━━━━━━\n• /vakitler ile vakitleri görün.",
        "hata_api": "❌ *Vakitler alınamadı!*\n\nLütfen birkaç saniye bekleyip tekrar deneyin.\n• /konum — Konumu yeniden ayarla",
        "spam":     "⏳ *Çok hızlı komut gönderiyorsun!*\n━━━━━━━━━━━━━━━━━━\n{emoji} *{sn} saniye* daha bekle.\n━━━━━━━━━━━━━━━━━━\n💡 Komutlar arası en az *5 saniye* beklemelisin.",
        "ban":      "🚫 Erişiminiz kısıtlanmış.",
        "bilinmeyen": "❌ *`{cmd}`* — böyle bir komut yok!\n━━━━━━━━━━━━━━━━━━\n📖 Tüm komutlar için: /yardim\n🏠 Ana menü için: /start\n━━━━━━━━━━━━━━━━━━\n💡 _Komutlar `/` ile başlar_",    },
    "ar": {
        "hosgeldin":  "🌙 *مرحباً بك في بوت أوقات الصلاة!*\n\n✦ اختر لغتك:",
        "dil_ok":     "✅ تم ضبط اللغة العربية.",
        "ulke":       "🌍 *اختر دولتك:*",
        "il":         "🏙️ *اختر المدينة:*",
        "ilce":       "📍 *{s}* — اختر المنطقة:",
        "yok":        "❌ لم يتم تحديد الموقع!\n\n• /konum — تحديد الموقع",
        "usor":       "⏰ *كم دقيقة قبل الصلاة للتنبيه؟*",
        "uok":        "✅ سيتم التنبيه قبل *{m} دقيقة*.",
        "apisor":     "🔧 *اختر API:*\n\n• 🌍 Aladhan — عالمي\n• 🤖 تلقائي — موصى به",
        "apiok":      "✅ تم اختيار *{a}*.",
        "dur":        "🔕 تم إيقاف التنبيهات.\n\n• /devam — استئناف",
        "dev":        "🔔 تم استئناف التنبيهات!",
        "umsg":       "🔔 *تنبيه الصلاة!*\n━━━━━━━━━━━━━━━━━━\n📍 {s} / {i}\n🕌 الصلاة : *{v}*\n⏱️ المتبقي: *{m} دقيقة*\n🕐 الوقت  : `{t}`\n━━━━━━━━━━━━━━━━━━\n🤲 صلاة مقبولة!\n👤 @NikeCheatYeniden | 📢 @nikestoretr",
        "bas":        "🕌 *أوقات الصلاة*\n━━━━━━━━━━━━━━━━━━\n📍 {s} / {i}\n📅 {d}\n━━━━━━━━━━━━━━━━━━\n\n",
        "im":  "🌙 الفجر   : `{t}`",
        "gu":  "☀️  الشروق : `{t}`",
        "og":  "🌤️ الظهر   : `{t}`",
        "ik":  "🌇 العصر   : `{t}`",
        "ak":  "🌆 المغرب  : `{t}`",
        "ya":  "🌃 العشاء  : `{t}`",
        "son": "\n\n⏭️ القادمة: *{v}* — `{t}`",
        "ayar": "⚙️ *الإعدادات*\n━━━━━━━━━━━━━━━━━━\n🌍 الدولة  : {u}\n🏙️ المدينة : {s}\n📍 المنطقة : {i}\n⏰ التنبيه : {m} دقيقة\n🔧 API     : {a}\n━━━━━━━━━━━━━━━━━━",
        "yard": "📖 *الأوامر*\n━━━━━━━━━━━━━━━━━━\n• /start — تشغيل البوت\n• /vakitler — أوقات اليوم\n• /yarin — أوقات الغد\n• /haftalik — الأسبوع\n• /konum — تحديد الموقع\n• /uyari — ضبط التنبيه\n• /dil — تغيير اللغة\n• /ayarlar — الإعدادات\n• /durdur — إيقاف\n• /devam — استئناف\n• /ozelgunler — المناسبات\n• /hakkinda — حول البوت\n━━━━━━━━━━━━━━━━━━\n🔧 *أمر المجموعة (مشرف):*\n• /grubayarla — إعداد الإشعارات التلقائية\n━━━━━━━━━━━━━━━━━━\n👤 @NikeCheatYeniden | 📢 @nikestoretr",
        "hak": "🕌 *بوت أوقات الصلاة*\n━━━━━━━━━━━━━━━━━━\n👤 @NikeCheatYeniden\n📢 @nikestoretr\n🌍 يدعم جميع الدول\n🔔 تنبيه تلقائي دقيق\n━━━━━━━━━━━━━━━━━━\n🤲 صلاة مقبولة!",
        "grup": "🕌 *تم إضافة بوت الصلاة!*\n━━━━━━━━━━━━━━━━━━\n• /konum — تحديد الموقع\n• /vakitler — عرض الأوقات\n━━━━━━━━━━━━━━━━━━\n👤 @NikeCheatYeniden | 📢 @nikestoretr",
        "stat": "📊 *الإحصائيات*\n━━━━━━━━━━━━━━━━━━\n👥 المستخدمون  : {t}\n✅ النشطون     : {a}\n🔔 اليوم       : {b}\n📨 الإجمالي    : {top}\n━━━━━━━━━━━━━━━━━━",
        "ad": {"Fajr":"الفجر","Sunrise":"الشروق","Dhuhr":"الظهر","Asr":"العصر","Maghrib":"المغرب","Isha":"العشاء"},
        "menu_bilgi": "🕌 *بوت الصلاة*\n━━━━━━━━━━━━━━━━━━\n📍 {s} / {i}\n━━━━━━━━━━━━━━━━━━",
        "konum_ok": "✅ *تم تحديد الموقع!*\n━━━━━━━━━━━━━━━━━━\n🌍 الدولة  : {u}\n🏙️ المدينة : {s}\n📍 المنطقة : {i}\n━━━━━━━━━━━━━━━━━━\n• /vakitler لعرض الأوقات.",
        "hata_api": "❌ *تعذر جلب الأوقات!*\n\nالرجاء المحاولة مجدداً.\n• /konum — إعادة تحديد الموقع",
        "spam":     "⏳ *أنت سريع جداً!*\n━━━━━━━━━━━━━━━━━━\n{emoji} انتظر *{sn} ثانية*.\n━━━━━━━━━━━━━━━━━━\n💡 يجب الانتظار *5 ثواني* بين الأوامر.",
        "ban":      "🚫 تم تقييد وصولك.",
        "bilinmeyen": "❌ *`{cmd}`* — هذا الأمر غير موجود!\n━━━━━━━━━━━━━━━━━━\n📖 /yardim لجميع الأوامر\n🏠 /start للقائمة الرئيسية",    },
    "de": {
        "hosgeldin":  "🌙 *Willkommen beim Gebetszeiten-Bot!*\n\n✦ Bitte wähle deine Sprache:",
        "dil_ok":     "✅ Sprache auf Deutsch eingestellt.",
        "ulke":       "🌍 *Wähle dein Land:*",
        "il":         "🏙️ *Stadt wählen:*",
        "ilce":       "📍 *{s}* — Bezirk wählen:",
        "yok":        "❌ Standort nicht eingestellt!\n\n• /konum — Standort einstellen",
        "usor":       "⏰ *Wie viele Minuten vor dem Gebet?*",
        "uok":        "✅ Benachrichtigung *{m} Minuten* vorher.",
        "apisor":     "🔧 *API wählen:*\n\n• 🌍 Aladhan — Weltweit\n• 🤖 Automatisch — Empfohlen",
        "apiok":      "✅ API *{a}* eingestellt.",
        "dur":        "🔕 Benachrichtigungen gestoppt.\n\n• /devam — Fortfahren",
        "dev":        "🔔 Benachrichtigungen wieder aktiv!",
        "umsg":       "🔔 *GEBETSZEIT-ERINNERUNG!*\n━━━━━━━━━━━━━━━━━━\n📍 {s} / {i}\n🕌 Gebet  : *{v}*\n⏱️ In     : *{m} Minuten*\n🕐 Uhrzeit: `{t}`\n━━━━━━━━━━━━━━━━━━\n🤲 Allah möge es annehmen!\n👤 @NikeCheatYeniden | 📢 @nikestoretr",
        "bas":        "🕌 *GEBETSZEITEN*\n━━━━━━━━━━━━━━━━━━\n📍 {s} / {i}\n📅 {d}\n━━━━━━━━━━━━━━━━━━\n\n",
        "im":  "🌙 Fajr    : `{t}`",
        "gu":  "☀️  Sunrise : `{t}`",
        "og":  "🌤️ Dhuhr   : `{t}`",
        "ik":  "🌇 Asr     : `{t}`",
        "ak":  "🌆 Maghrib : `{t}`",
        "ya":  "🌃 Isha    : `{t}`",
        "son": "\n\n⏭️ Nächstes: *{v}* — `{t}`",
        "ayar": "⚙️ *EINSTELLUNGEN*\n━━━━━━━━━━━━━━━━━━\n🌍 Land   : {u}\n🏙️ Stadt  : {s}\n📍 Bezirk : {i}\n⏰ Alarm  : {m} Min\n🔧 API    : {a}\n━━━━━━━━━━━━━━━━━━",
        "yard": "📖 *BEFEHLE*\n━━━━━━━━━━━━━━━━━━\n• /start — Bot starten\n• /vakitler — Heutige Zeiten\n• /yarin — Morgen\n• /haftalik — Wöchentlich\n• /konum — Standort\n• /uyari — Alarm\n• /dil — Sprache\n• /ayarlar — Einstellungen\n• /durdur — Stoppen\n• /devam — Fortfahren\n• /ozelgunler — Islamische Tage\n• /hakkinda — Über den Bot\n━━━━━━━━━━━━━━━━━━\n🔧 *Gruppenbefehl (Admin):*\n• /grubayarla — Automatische Gebetszeiten\n━━━━━━━━━━━━━━━━━━\n👤 @NikeCheatYeniden | 📢 @nikestoretr",
        "hak": "🕌 *GEBETSZEITEN BOT*\n━━━━━━━━━━━━━━━━━━\n👤 @NikeCheatYeniden\n📢 @nikestoretr\n🌍 Alle Länder\n🔔 Automatische Erinnerungen\n━━━━━━━━━━━━━━━━━━\n🤲 Allah möge es annehmen!",
        "grup": "🕌 *Gebetszeiten-Bot hinzugefügt!*\n━━━━━━━━━━━━━━━━━━\n• /konum — Standort\n• /vakitler — Zeiten\n━━━━━━━━━━━━━━━━━━\n👤 @NikeCheatYeniden | 📢 @nikestoretr",
        "stat": "📊 *STATISTIK*\n━━━━━━━━━━━━━━━━━━\n👥 Benutzer : {t}\n✅ Aktiv    : {a}\n🔔 Heute    : {b}\n📨 Gesamt   : {top}\n━━━━━━━━━━━━━━━━━━",
        "ad": {"Fajr":"Fajr","Sunrise":"Sonnenaufgang","Dhuhr":"Dhuhr","Asr":"Asr","Maghrib":"Maghrib","Isha":"Isha"},
        "menu_bilgi": "🕌 *GEBETSZEITEN BOT*\n━━━━━━━━━━━━━━━━━━\n📍 {s} / {i}\n━━━━━━━━━━━━━━━━━━",
        "konum_ok": "✅ *STANDORT EINGESTELLT!*\n━━━━━━━━━━━━━━━━━━\n🌍 Land   : {u}\n🏙️ Stadt  : {s}\n📍 Bezirk : {i}\n━━━━━━━━━━━━━━━━━━\n• /vakitler für Gebetszeiten.",
        "hata_api": "❌ *Zeiten konnten nicht abgerufen werden!*\n\nBitte erneut versuchen.\n• /konum — Standort neu setzen",
        "spam":     "⏳ *Zu schnell!*\n━━━━━━━━━━━━━━━━━━\n{emoji} Warte noch *{sn} Sekunden*.\n━━━━━━━━━━━━━━━━━━\n💡 Mindestens *5 Sekunden* zwischen Befehlen.",
        "ban":      "🚫 Ihr Zugriff wurde eingeschränkt.",
        "bilinmeyen": "❌ *`{cmd}`* — Unbekannter Befehl!\n━━━━━━━━━━━━━━━━━━\n📖 Alle Befehle: /yardim\n🏠 Hauptmenü: /start",    },
    "fr": {
        "hosgeldin":  "🌙 *Bienvenue sur le Bot des Heures de Prière!*\n\n✦ Choisissez votre langue:",
        "dil_ok":     "✅ Langue réglée en Français.",
        "ulke":       "🌍 *Choisissez votre pays:*",
        "il":         "🏙️ *Choisissez votre ville:*",
        "ilce":       "📍 *{s}* — Choisissez le quartier:",
        "yok":        "❌ Localisation non définie!\n\n• /konum — Définir la localisation",
        "usor":       "⏰ *Combien de minutes avant la prière?*",
        "uok":        "✅ Alerte réglée *{m} minutes* avant.",
        "apisor":     "🔧 *Choisir API:*\n\n• 🌍 Aladhan — Mondial\n• 🤖 Automatique — Recommandé",
        "apiok":      "✅ API *{a}* sélectionné.",
        "dur":        "🔕 Alertes suspendues.\n\n• /devam — Reprendre",
        "dev":        "🔔 Alertes reprises!",
        "umsg":       "🔔 *RAPPEL DE PRIÈRE!*\n━━━━━━━━━━━━━━━━━━\n📍 {s} / {i}\n🕌 Prière : *{v}*\n⏱️ Dans   : *{m} minutes*\n🕐 Heure  : `{t}`\n━━━━━━━━━━━━━━━━━━\n🤲 Bonne prière!\n👤 @NikeCheatYeniden | 📢 @nikestoretr",
        "bas":        "🕌 *HEURES DE PRIÈRE*\n━━━━━━━━━━━━━━━━━━\n📍 {s} / {i}\n📅 {d}\n━━━━━━━━━━━━━━━━━━\n\n",
        "im":  "🌙 Fajr    : `{t}`",
        "gu":  "☀️  Lever   : `{t}`",
        "og":  "🌤️ Dhuhr   : `{t}`",
        "ik":  "🌇 Asr     : `{t}`",
        "ak":  "🌆 Maghrib : `{t}`",
        "ya":  "🌃 Isha    : `{t}`",
        "son": "\n\n⏭️ Prochain: *{v}* — `{t}`",
        "ayar": "⚙️ *PARAMÈTRES*\n━━━━━━━━━━━━━━━━━━\n🌍 Pays    : {u}\n🏙️ Ville   : {s}\n📍 Quartier: {i}\n⏰ Alerte  : {m} min\n🔧 API     : {a}\n━━━━━━━━━━━━━━━━━━",
        "yard": "📖 *COMMANDES*\n━━━━━━━━━━━━━━━━━━\n• /start — Démarrer\n• /vakitler — Prières d'aujourd'hui\n• /yarin — Demain\n• /haftalik — Semaine\n• /konum — Localisation\n• /uyari — Alerte\n• /dil — Langue\n• /ayarlar — Paramètres\n• /durdur — Suspendre\n• /devam — Reprendre\n• /ozelgunler — Jours islamiques\n• /hakkinda — À propos\n━━━━━━━━━━━━━━━━━━\n🔧 *Commande groupe (Admin):*\n• /grubayarla — Notifications automatiques\n━━━━━━━━━━━━━━━━━━\n👤 @NikeCheatYeniden | 📢 @nikestoretr",
        "hak": "🕌 *BOT HEURES DE PRIÈRE*\n━━━━━━━━━━━━━━━━━━\n👤 @NikeCheatYeniden\n📢 @nikestoretr\n🌍 Tous pays\n🔔 Rappels automatiques\n━━━━━━━━━━━━━━━━━━\n🤲 Qu'Allah accepte!",
        "grup": "🕌 *Bot de prière ajouté!*\n━━━━━━━━━━━━━━━━━━\n• /konum — Localisation\n• /vakitler — Voir prières\n━━━━━━━━━━━━━━━━━━\n👤 @NikeCheatYeniden | 📢 @nikestoretr",
        "stat": "📊 *STATISTIQUES*\n━━━━━━━━━━━━━━━━━━\n👥 Utilisateurs : {t}\n✅ Actifs       : {a}\n🔔 Aujourd'hui  : {b}\n📨 Total        : {top}\n━━━━━━━━━━━━━━━━━━",
        "ad": {"Fajr":"Fajr","Sunrise":"Lever","Dhuhr":"Dhuhr","Asr":"Asr","Maghrib":"Maghrib","Isha":"Isha"},
        "menu_bilgi": "🕌 *BOT DE PRIÈRE*\n━━━━━━━━━━━━━━━━━━\n📍 {s} / {i}\n━━━━━━━━━━━━━━━━━━",
        "konum_ok": "✅ *LOCALISATION RÉGLÉE!*\n━━━━━━━━━━━━━━━━━━\n🌍 Pays    : {u}\n🏙️ Ville   : {s}\n📍 Quartier: {i}\n━━━━━━━━━━━━━━━━━━\n• /vakitler pour les prières.",
        "hata_api": "❌ *Impossible d'obtenir les horaires!*\n\nRéessayez dans quelques secondes.\n• /konum — Redéfinir la localisation",
        "spam":     "⏳ *Trop rapide!*\n━━━━━━━━━━━━━━━━━━\n{emoji} Attendez *{sn} secondes*.\n━━━━━━━━━━━━━━━━━━\n💡 Minimum *5 secondes* entre les commandes.",
        "ban":      "🚫 Votre accès est restreint.",
        "bilinmeyen": "❌ *`{cmd}`* — Commande inconnue!\n━━━━━━━━━━━━━━━━━━\n📖 Toutes les commandes: /yardim\n🏠 Menu principal: /start",    },
    "nl": {
        "hosgeldin":  "🌙 *Welkom bij de Gebedstijden Bot!*\n\n✦ Selecteer uw taal:",
        "dil_ok":     "✅ Taal ingesteld op Nederlands.",
        "ulke":       "🌍 *Selecteer uw land:*",
        "il":         "🏙️ *Selecteer uw stad:*",
        "ilce":       "📍 *{s}* — Selecteer wijk:",
        "yok":        "❌ Locatie niet ingesteld!\n\n• /konum — Locatie instellen",
        "usor":       "⏰ *Hoeveel minuten voor het gebed?*",
        "uok":        "✅ Melding *{m} minuten* van tevoren.",
        "apisor":     "🔧 *API kiezen:*\n\n• 🌍 Aladhan — Wereldwijd\n• 🤖 Automatisch — Aanbevolen",
        "apiok":      "✅ API *{a}* ingesteld.",
        "dur":        "🔕 Meldingen gestopt.\n\n• /devam — Hervatten",
        "dev":        "🔔 Meldingen hervat!",
        "umsg":       "🔔 *GEBED HERINNERING!*\n━━━━━━━━━━━━━━━━━━\n📍 {s} / {i}\n🕌 Gebed  : *{v}*\n⏱️ Over   : *{m} minuten*\n🕐 Tijd   : `{t}`\n━━━━━━━━━━━━━━━━━━\n🤲 Moge Allah accepteren!\n👤 @NikeCheatYeniden | 📢 @nikestoretr",
        "bas":        "🕌 *GEBEDSTIJDEN*\n━━━━━━━━━━━━━━━━━━\n📍 {s} / {i}\n📅 {d}\n━━━━━━━━━━━━━━━━━━\n\n",
        "im":  "🌙 Fajr    : `{t}`",
        "gu":  "☀️  Sunrise : `{t}`",
        "og":  "🌤️ Dhuhr   : `{t}`",
        "ik":  "🌇 Asr     : `{t}`",
        "ak":  "🌆 Maghrib : `{t}`",
        "ya":  "🌃 Isha    : `{t}`",
        "son": "\n\n⏭️ Volgende: *{v}* — `{t}`",
        "ayar": "⚙️ *INSTELLINGEN*\n━━━━━━━━━━━━━━━━━━\n🌍 Land   : {u}\n🏙️ Stad   : {s}\n📍 Wijk   : {i}\n⏰ Alarm  : {m} min\n🔧 API    : {a}\n━━━━━━━━━━━━━━━━━━",
        "yard": "📖 *COMMANDO'S*\n━━━━━━━━━━━━━━━━━━\n• /start — Start\n• /vakitler — Tijden vandaag\n• /yarin — Morgen\n• /haftalik — Wekelijks\n• /konum — Locatie\n• /uyari — Alarm\n• /dil — Taal\n• /ayarlar — Instellingen\n• /durdur — Stoppen\n• /devam — Hervatten\n• /ozelgunler — Islamitische dagen\n• /hakkinda — Over\n━━━━━━━━━━━━━━━━━━\n🔧 *Groepscommando (Admin):*\n• /grubayarla — Automatische gebedsmeldingen\n━━━━━━━━━━━━━━━━━━\n👤 @NikeCheatYeniden | 📢 @nikestoretr",
        "hak": "🕌 *GEBEDSTIJDEN BOT*\n━━━━━━━━━━━━━━━━━━\n👤 @NikeCheatYeniden\n📢 @nikestoretr\n🌍 Alle landen\n🔔 Automatische herinneringen\n━━━━━━━━━━━━━━━━━━\n🤲 Moge Allah accepteren!",
        "grup": "🕌 *Gebedstijden Bot toegevoegd!*\n━━━━━━━━━━━━━━━━━━\n• /konum — Locatie\n• /vakitler — Tijden\n━━━━━━━━━━━━━━━━━━\n👤 @NikeCheatYeniden | 📢 @nikestoretr",
        "stat": "📊 *STATISTIEKEN*\n━━━━━━━━━━━━━━━━━━\n👥 Gebruikers : {t}\n✅ Actief     : {a}\n🔔 Vandaag    : {b}\n📨 Totaal     : {top}\n━━━━━━━━━━━━━━━━━━",
        "ad": {"Fajr":"Fajr","Sunrise":"Zonsopgang","Dhuhr":"Dhuhr","Asr":"Asr","Maghrib":"Maghrib","Isha":"Isha"},
        "menu_bilgi": "🕌 *GEBEDSTIJDEN BOT*\n━━━━━━━━━━━━━━━━━━\n📍 {s} / {i}\n━━━━━━━━━━━━━━━━━━",
        "konum_ok": "✅ *LOCATIE INGESTELD!*\n━━━━━━━━━━━━━━━━━━\n🌍 Land   : {u}\n🏙️ Stad   : {s}\n📍 Wijk   : {i}\n━━━━━━━━━━━━━━━━━━\n• /vakitler voor gebedstijden.",
        "hata_api": "❌ *Tijden konden niet worden opgehaald!*\n\nProbeer het opnieuw.\n• /konum — Locatie opnieuw instellen",
        "spam":     "⏳ *Te snel!*\n━━━━━━━━━━━━━━━━━━\n{emoji} Wacht *{sn} seconden*.\n━━━━━━━━━━━━━━━━━━\n💡 Minimaal *5 seconden* tussen commando's.",
        "ban":      "🚫 Uw toegang is beperkt.",
        "bilinmeyen": "❌ *`{cmd}`* — Onbekend commando!\n━━━━━━━━━━━━━━━━━━\n📖 Alle commando's: /yardim\n🏠 Hoofdmenu: /start",    },
    "en": {
        "hosgeldin":  "🌙 *Welcome to the Prayer Times Bot!*\n\n✦ Please select your language:",
        "dil_ok":     "✅ Language set to English.",
        "ulke":       "🌍 *Select your country:*",
        "il":         "🏙️ *Select your city:*",
        "ilce":       "📍 *{s}* — Select district:",
        "yok":        "❌ Location not set!\n\n• /konum — Set location",
        "usor":       "⏰ *How many minutes before prayer to notify?*",
        "uok":        "✅ Alert set *{m} minutes* before.",
        "apisor":     "🔧 *Select API:*\n\n• 🌍 Aladhan — Worldwide\n• 🤖 Auto — Recommended",
        "apiok":      "✅ API set to *{a}*.",
        "dur":        "🔕 Alerts paused.\n\n• /devam — Resume",
        "dev":        "🔔 Alerts resumed!",
        "umsg":       "🔔 *PRAYER ALERT!*\n━━━━━━━━━━━━━━━━━━\n📍 {s} / {i}\n🕌 Prayer : *{v}*\n⏱️ In     : *{m} minutes*\n🕐 Time   : `{t}`\n━━━━━━━━━━━━━━━━━━\n🤲 May Allah accept!\n👤 @NikeCheatYeniden | 📢 @nikestoretr",
        "bas":        "🕌 *PRAYER TIMES*\n━━━━━━━━━━━━━━━━━━\n📍 {s} / {i}\n📅 {d}\n━━━━━━━━━━━━━━━━━━\n\n",
        "im":  "🌙 Fajr    : `{t}`",
        "gu":  "☀️  Sunrise : `{t}`",
        "og":  "🌤️ Dhuhr   : `{t}`",
        "ik":  "🌇 Asr     : `{t}`",
        "ak":  "🌆 Maghrib : `{t}`",
        "ya":  "🌃 Isha    : `{t}`",
        "son": "\n\n⏭️ Next: *{v}* — `{t}`",
        "ayar": "⚙️ *YOUR SETTINGS*\n━━━━━━━━━━━━━━━━━━\n🌍 Country : {u}\n🏙️ City    : {s}\n📍 District: {i}\n⏰ Alert   : {m} min\n🔧 API     : {a}\n━━━━━━━━━━━━━━━━━━",
        "yard": "📖 *COMMANDS*\n━━━━━━━━━━━━━━━━━━\n• /start — Start bot\n• /vakitler — Today's times\n• /yarin — Tomorrow\n• /haftalik — Weekly\n• /konum — Set location\n• /uyari — Set alert\n• /dil — Change language\n• /ayarlar — Settings\n• /durdur — Pause alerts\n• /devam — Resume alerts\n• /ozelgunler — Islamic days\n• /hakkinda — About\n━━━━━━━━━━━━━━━━━━\n🔧 *Group command (Admin):*\n• /grubayarla — Auto prayer notifications\n━━━━━━━━━━━━━━━━━━\n👤 @NikeCheatYeniden | 📢 @nikestoretr",
        "hak": "🕌 *PRAYER TIMES BOT*\n━━━━━━━━━━━━━━━━━━\n👤 @NikeCheatYeniden\n📢 @nikestoretr\n🌍 All countries supported\n🔔 Automatic prayer alerts\n━━━━━━━━━━━━━━━━━━\n🤲 May Allah accept!",
        "grup": "🕌 *Prayer Times Bot added!*\n━━━━━━━━━━━━━━━━━━\n• /konum — Set location\n• /vakitler — View times\n━━━━━━━━━━━━━━━━━━\n👤 @NikeCheatYeniden | 📢 @nikestoretr",
        "stat": "📊 *STATISTICS*\n━━━━━━━━━━━━━━━━━━\n👥 Total users   : {t}\n✅ Active alerts : {a}\n🔔 Sent today    : {b}\n📨 Total sent    : {top}\n━━━━━━━━━━━━━━━━━━",
        "ad": {"Fajr":"Fajr","Sunrise":"Sunrise","Dhuhr":"Dhuhr","Asr":"Asr","Maghrib":"Maghrib","Isha":"Isha"},
        "menu_bilgi": "🕌 *PRAYER TIMES BOT*\n━━━━━━━━━━━━━━━━━━\n📍 {s} / {i}\n━━━━━━━━━━━━━━━━━━",
        "konum_ok": "✅ *LOCATION SET!*\n━━━━━━━━━━━━━━━━━━\n🌍 Country : {u}\n🏙️ City    : {s}\n📍 District: {i}\n━━━━━━━━━━━━━━━━━━\n• /vakitler to see prayer times.",
        "hata_api": "❌ *Could not fetch prayer times!*\n\nPlease try again.\n• /konum — Reset location",
        "spam":     "⏳ *Too fast!*\n━━━━━━━━━━━━━━━━━━\n{emoji} Wait *{sn} seconds*.\n━━━━━━━━━━━━━━━━━━\n💡 Minimum *5 seconds* between commands.",
        "ban":      "🚫 Your access has been restricted.",
        "bilinmeyen": "❌ *`{cmd}`* — Unknown command!\n━━━━━━━━━━━━━━━━━━\n📖 All commands: /yardim\n🏠 Main menu: /start",    },
    "ur": {
        "hosgeldin":  "🌙 *نماز کے اوقات بوٹ میں خوش آمدید!*\n\n✦ اپنی زبان منتخب کریں:",
        "dil_ok":     "✅ زبان اردو میں سیٹ ہوگئی۔",
        "ulke":       "🌍 *اپنا ملک منتخب کریں:*",
        "il":         "🏙️ *شہر منتخب کریں:*",
        "ilce":       "📍 *{s}* — علاقہ منتخب کریں:",
        "yok":        "❌ مقام سیٹ نہیں!\n\n• /konum — مقام سیٹ کریں",
        "usor":       "⏰ *نماز سے کتنے منٹ پہلے اطلاع؟*",
        "uok":        "✅ *{m} منٹ* پہلے اطلاع سیٹ ہوگئی۔",
        "apisor":     "🔧 *API منتخب کریں:*\n\n• 🌍 Aladhan — دنیا بھر\n• 🤖 خودکار — تجویز",
        "apiok":      "✅ API *{a}* سیٹ ہوگیا۔",
        "dur":        "🔕 اطلاعات روک دی گئیں۔\n\n• /devam — جاری رکھیں",
        "dev":        "🔔 اطلاعات دوبارہ شروع!",
        "umsg":       "🔔 *نماز کی یاددہانی!*\n━━━━━━━━━━━━━━━━━━\n📍 {s} / {i}\n🕌 نماز  : *{v}*\n⏱️ وقت   : *{m} منٹ*\n🕐 بجے   : `{t}`\n━━━━━━━━━━━━━━━━━━\n🤲 اللہ قبول فرمائے!\n👤 @NikeCheatYeniden | 📢 @nikestoretr",
        "bas":        "🕌 *نماز کے اوقات*\n━━━━━━━━━━━━━━━━━━\n📍 {s} / {i}\n📅 {d}\n━━━━━━━━━━━━━━━━━━\n\n",
        "im":  "🌙 فجر    : `{t}`",
        "gu":  "☀️  طلوع   : `{t}`",
        "og":  "🌤️ ظہر    : `{t}`",
        "ik":  "🌇 عصر    : `{t}`",
        "ak":  "🌆 مغرب   : `{t}`",
        "ya":  "🌃 عشاء   : `{t}`",
        "son": "\n\n⏭️ اگلی: *{v}* — `{t}`",
        "ayar": "⚙️ *آپ کی ترتیبات*\n━━━━━━━━━━━━━━━━━━\n🌍 ملک   : {u}\n🏙️ شہر   : {s}\n📍 علاقہ : {i}\n⏰ اطلاع : {m} منٹ\n🔧 API   : {a}\n━━━━━━━━━━━━━━━━━━",
        "yard": "📖 *کمانڈز*\n━━━━━━━━━━━━━━━━━━\n• /start — شروع\n• /vakitler — آج کے اوقات\n• /yarin — کل\n• /haftalik — ہفتہ\n• /konum — مقام\n• /uyari — اطلاع\n• /dil — زبان\n• /ayarlar — ترتیبات\n• /durdur — روکیں\n• /devam — جاری\n• /ozelgunler — اسلامی ایام\n━━━━━━━━━━━━━━━━━━\n🔧 *گروپ کمانڈ (ایڈمن):*\n• /grubayarla — خودکار اذان اطلاعات\n━━━━━━━━━━━━━━━━━━\n👤 @NikeCheatYeniden | 📢 @nikestoretr",
        "hak": "🕌 *نماز بوٹ*\n━━━━━━━━━━━━━━━━━━\n👤 @NikeCheatYeniden\n📢 @nikestoretr\n🌍 تمام ممالک\n🔔 خودکار اطلاع\n━━━━━━━━━━━━━━━━━━\n🤲 اللہ قبول فرمائے!",
        "grup": "🕌 *نماز بوٹ شامل!*\n━━━━━━━━━━━━━━━━━━\n• /konum — مقام\n• /vakitler — اوقات\n━━━━━━━━━━━━━━━━━━\n👤 @NikeCheatYeniden | 📢 @nikestoretr",
        "stat": "📊 *اعداد و شمار*\n━━━━━━━━━━━━━━━━━━\n👥 کل صارفین : {t}\n✅ فعال اطلاع : {a}\n🔔 آج بھیجی  : {b}\n📨 کل بھیجی  : {top}\n━━━━━━━━━━━━━━━━━━",
        "ad": {"Fajr":"فجر","Sunrise":"طلوع","Dhuhr":"ظہر","Asr":"عصر","Maghrib":"مغرب","Isha":"عشاء"},
        "menu_bilgi": "🕌 *نماز بوٹ*\n━━━━━━━━━━━━━━━━━━\n📍 {s} / {i}\n━━━━━━━━━━━━━━━━━━",
        "konum_ok": "✅ *مقام سیٹ!*\n━━━━━━━━━━━━━━━━━━\n🌍 ملک   : {u}\n🏙️ شہر   : {s}\n📍 علاقہ : {i}\n━━━━━━━━━━━━━━━━━━\n• /vakitler اوقات دیکھیں۔",
        "hata_api": "❌ *اوقات نہیں مل سکے!*\n\nدوبارہ کوشش کریں۔\n• /konum — مقام دوبارہ سیٹ کریں",
        "spam":     "⏳ *بہت تیز!*\n━━━━━━━━━━━━━━━━━━\n{emoji} *{sn} سیکنڈ* انتظار کریں۔\n━━━━━━━━━━━━━━━━━━\n💡 کمانڈز کے درمیان *5 سیکنڈ* ضروری ہیں۔",
        "ban":      "🚫 آپ کی رسائی محدود ہے۔",
        "bilinmeyen": "❌ *`{cmd}`* — نامعلوم کمانڈ!\n━━━━━━━━━━━━━━━━━━\n📖 تمام کمانڈز: /yardim\n🏠 مین مینو: /start",    },
    "id": {
        "hosgeldin":  "🌙 *Selamat Datang di Bot Waktu Sholat!*\n\n✦ Pilih bahasa Anda:",
        "dil_ok":     "✅ Bahasa Indonesia diatur.",
        "ulke":       "🌍 *Pilih negara Anda:*",
        "il":         "🏙️ *Pilih kota Anda:*",
        "ilce":       "📍 *{s}* — Pilih kecamatan:",
        "yok":        "❌ Lokasi belum diatur!\n\n• /konum — Atur lokasi",
        "usor":       "⏰ *Berapa menit sebelum sholat?*",
        "uok":        "✅ Pengingat *{m} menit* sebelumnya.",
        "apisor":     "🔧 *Pilih API:*\n\n• 🌍 Aladhan — Seluruh dunia\n• 🤖 Otomatis — Disarankan",
        "apiok":      "✅ API *{a}* dipilih.",
        "dur":        "🔕 Pengingat dihentikan.\n\n• /devam — Lanjutkan",
        "dev":        "🔔 Pengingat dilanjutkan!",
        "umsg":       "🔔 *PENGINGAT SHOLAT!*\n━━━━━━━━━━━━━━━━━━\n📍 {s} / {i}\n🕌 Sholat  : *{v}*\n⏱️ Dalam   : *{m} menit*\n🕐 Pukul   : `{t}`\n━━━━━━━━━━━━━━━━━━\n🤲 Semoga Allah menerima!\n👤 @NikeCheatYeniden | 📢 @nikestoretr",
        "bas":        "🕌 *WAKTU SHOLAT*\n━━━━━━━━━━━━━━━━━━\n📍 {s} / {i}\n📅 {d}\n━━━━━━━━━━━━━━━━━━\n\n",
        "im":  "🌙 Subuh   : `{t}`",
        "gu":  "☀️  Terbit  : `{t}`",
        "og":  "🌤️ Dzuhur  : `{t}`",
        "ik":  "🌇 Ashar   : `{t}`",
        "ak":  "🌆 Maghrib : `{t}`",
        "ya":  "🌃 Isya    : `{t}`",
        "son": "\n\n⏭️ Berikutnya: *{v}* — `{t}`",
        "ayar": "⚙️ *PENGATURAN*\n━━━━━━━━━━━━━━━━━━\n🌍 Negara : {u}\n🏙️ Kota   : {s}\n📍 Kec.   : {i}\n⏰ Alarm  : {m} menit\n🔧 API    : {a}\n━━━━━━━━━━━━━━━━━━",
        "yard": "📖 *PERINTAH*\n━━━━━━━━━━━━━━━━━━\n• /start — Mulai\n• /vakitler — Waktu hari ini\n• /yarin — Besok\n• /haftalik — Mingguan\n• /konum — Lokasi\n• /uyari — Alarm\n• /dil — Bahasa\n• /ayarlar — Pengaturan\n• /durdur — Hentikan\n• /devam — Lanjutkan\n• /ozelgunler — Hari Islam\n━━━━━━━━━━━━━━━━━━\n🔧 *Perintah grup (Admin):*\n• /grubayarla — Notifikasi otomatis\n━━━━━━━━━━━━━━━━━━\n👤 @NikeCheatYeniden | 📢 @nikestoretr",
        "hak": "🕌 *BOT WAKTU SHOLAT*\n━━━━━━━━━━━━━━━━━━\n👤 @NikeCheatYeniden\n📢 @nikestoretr\n🌍 Semua negara\n🔔 Pengingat otomatis\n━━━━━━━━━━━━━━━━━━\n🤲 Semoga diterima Allah!",
        "grup": "🕌 *Bot Sholat ditambahkan!*\n━━━━━━━━━━━━━━━━━━\n• /konum — Lokasi\n• /vakitler — Waktu\n━━━━━━━━━━━━━━━━━━\n👤 @NikeCheatYeniden | 📢 @nikestoretr",
        "stat": "📊 *STATISTIK*\n━━━━━━━━━━━━━━━━━━\n👥 Pengguna : {t}\n✅ Aktif    : {a}\n🔔 Hari ini : {b}\n📨 Total    : {top}\n━━━━━━━━━━━━━━━━━━",
        "ad": {"Fajr":"Subuh","Sunrise":"Terbit","Dhuhr":"Dzuhur","Asr":"Ashar","Maghrib":"Maghrib","Isha":"Isya"},
        "menu_bilgi": "🕌 *BOT SHOLAT*\n━━━━━━━━━━━━━━━━━━\n📍 {s} / {i}\n━━━━━━━━━━━━━━━━━━",
        "konum_ok": "✅ *LOKASI DIATUR!*\n━━━━━━━━━━━━━━━━━━\n🌍 Negara : {u}\n🏙️ Kota   : {s}\n📍 Kec.   : {i}\n━━━━━━━━━━━━━━━━━━\n• /vakitler untuk waktu sholat.",
        "hata_api": "❌ *Waktu sholat tidak dapat diambil!*\n\nCoba lagi.\n• /konum — Atur ulang lokasi",
        "spam":     "⏳ *Terlalu cepat!*\n━━━━━━━━━━━━━━━━━━\n{emoji} Tunggu *{sn} detik*.\n━━━━━━━━━━━━━━━━━━\n💡 Minimum *5 detik* antara perintah.",
        "ban":      "🚫 Akses Anda dibatasi.",
        "bilinmeyen": "❌ *`{cmd}`* — Perintah tidak dikenal!\n━━━━━━━━━━━━━━━━━━\n📖 Semua perintah: /yardim\n🏠 Menu utama: /start",    },
    "ms": {
        "hosgeldin":  "🌙 *Selamat Datang ke Bot Waktu Solat!*\n\n✦ Pilih bahasa anda:",
        "dil_ok":     "✅ Bahasa Melayu ditetapkan.",
        "ulke":       "🌍 *Pilih negara anda:*",
        "il":         "🏙️ *Pilih bandar anda:*",
        "ilce":       "📍 *{s}* — Pilih daerah:",
        "yok":        "❌ Lokasi belum ditetapkan!\n\n• /konum — Tetapkan lokasi",
        "usor":       "⏰ *Berapa minit sebelum solat?*",
        "uok":        "✅ Peringatan *{m} minit* lebih awal.",
        "apisor":     "🔧 *Pilih API:*\n\n• 🌍 Aladhan — Seluruh dunia\n• 🤖 Auto — Disyorkan",
        "apiok":      "✅ API *{a}* ditetapkan.",
        "dur":        "🔕 Peringatan dihentikan.\n\n• /devam — Teruskan",
        "dev":        "🔔 Peringatan diteruskan!",
        "umsg":       "🔔 *PERINGATAN SOLAT!*\n━━━━━━━━━━━━━━━━━━\n📍 {s} / {i}\n🕌 Solat  : *{v}*\n⏱️ Dalam  : *{m} minit*\n🕐 Masa   : `{t}`\n━━━━━━━━━━━━━━━━━━\n🤲 Semoga Allah menerima!\n👤 @NikeCheatYeniden | 📢 @nikestoretr",
        "bas":        "🕌 *WAKTU SOLAT*\n━━━━━━━━━━━━━━━━━━\n📍 {s} / {i}\n📅 {d}\n━━━━━━━━━━━━━━━━━━\n\n",
        "im":  "🌙 Subuh   : `{t}`",
        "gu":  "☀️  Syuruk  : `{t}`",
        "og":  "🌤️ Zohor   : `{t}`",
        "ik":  "🌇 Asar    : `{t}`",
        "ak":  "🌆 Maghrib : `{t}`",
        "ya":  "🌃 Isyak   : `{t}`",
        "son": "\n\n⏭️ Seterusnya: *{v}* — `{t}`",
        "ayar": "⚙️ *TETAPAN*\n━━━━━━━━━━━━━━━━━━\n🌍 Negara : {u}\n🏙️ Bandar : {s}\n📍 Daerah : {i}\n⏰ Amaran : {m} minit\n🔧 API    : {a}\n━━━━━━━━━━━━━━━━━━",
        "yard": "📖 *ARAHAN*\n━━━━━━━━━━━━━━━━━━\n• /start — Mula\n• /vakitler — Waktu hari ini\n• /yarin — Esok\n• /haftalik — Mingguan\n• /konum — Lokasi\n• /uyari — Amaran\n• /dil — Bahasa\n• /ayarlar — Tetapan\n• /durdur — Henti\n• /devam — Teruskan\n• /ozelgunler — Hari Islam\n━━━━━━━━━━━━━━━━━━\n🔧 *Arahan kumpulan (Admin):*\n• /grubayarla — Pemberitahuan automatik\n━━━━━━━━━━━━━━━━━━\n👤 @NikeCheatYeniden | 📢 @nikestoretr",
        "hak": "🕌 *BOT WAKTU SOLAT*\n━━━━━━━━━━━━━━━━━━\n👤 @NikeCheatYeniden\n📢 @nikestoretr\n🌍 Semua negara\n🔔 Peringatan automatik\n━━━━━━━━━━━━━━━━━━\n🤲 Semoga Allah menerima!",
        "grup": "🕌 *Bot Solat ditambah!*\n━━━━━━━━━━━━━━━━━━\n• /konum — Lokasi\n• /vakitler — Waktu\n━━━━━━━━━━━━━━━━━━\n👤 @NikeCheatYeniden | 📢 @nikestoretr",
        "stat": "📊 *STATISTIK*\n━━━━━━━━━━━━━━━━━━\n👥 Pengguna : {t}\n✅ Aktif    : {a}\n🔔 Hari ini : {b}\n📨 Jumlah   : {top}\n━━━━━━━━━━━━━━━━━━",
        "ad": {"Fajr":"Subuh","Sunrise":"Syuruk","Dhuhr":"Zohor","Asr":"Asar","Maghrib":"Maghrib","Isha":"Isyak"},
        "menu_bilgi": "🕌 *BOT SOLAT*\n━━━━━━━━━━━━━━━━━━\n📍 {s} / {i}\n━━━━━━━━━━━━━━━━━━",
        "konum_ok": "✅ *LOKASI DITETAPKAN!*\n━━━━━━━━━━━━━━━━━━\n🌍 Negara : {u}\n🏙️ Bandar : {s}\n📍 Daerah : {i}\n━━━━━━━━━━━━━━━━━━\n• /vakitler untuk waktu solat.",
        "hata_api": "❌ *Waktu solat tidak dapat diambil!*\n\nCuba lagi.\n• /konum — Semak semula lokasi",
        "spam":     "⏳ *Terlalu pantas!*\n━━━━━━━━━━━━━━━━━━\n{emoji} Tunggu *{sn} saat*.\n━━━━━━━━━━━━━━━━━━\n💡 Minimum *5 saat* antara arahan.",
        "ban":      "🚫 Akses anda telah disekat.",
        "bilinmeyen": "❌ *`{cmd}`* — Arahan tidak diketahui!\n━━━━━━━━━━━━━━━━━━\n📖 Semua arahan: /yardim\n🏠 Menu utama: /start",    },
    "ru": {
        "hosgeldin":  "🌙 *Добро пожаловать в бот времени намаза!*\n\n✦ Выберите язык:",
        "dil_ok":     "✅ Язык установлен на Русский.",
        "ulke":       "🌍 *Выберите страну:*",
        "il":         "🏙️ *Выберите город:*",
        "ilce":       "📍 *{s}* — Выберите район:",
        "yok":        "❌ Местоположение не указано!\n\n• /konum — Указать местоположение",
        "usor":       "⏰ *За сколько минут до намаза уведомить?*",
        "uok":        "✅ Уведомление за *{m} минут*.",
        "apisor":     "🔧 *Выберите API:*\n\n• 🌍 Aladhan — Весь мир\n• 🤖 Авто — Рекомендуется",
        "apiok":      "✅ API *{a}* выбран.",
        "dur":        "🔕 Уведомления остановлены.\n\n• /devam — Возобновить",
        "dev":        "🔔 Уведомления возобновлены!",
        "umsg":       "🔔 *НАПОМИНАНИЕ О НАМАЗЕ!*\n━━━━━━━━━━━━━━━━━━\n📍 {s} / {i}\n🕌 Намаз  : *{v}*\n⏱️ Через  : *{m} минут*\n🕐 Время  : `{t}`\n━━━━━━━━━━━━━━━━━━\n🤲 Да примет Аллах!\n👤 @NikeCheatYeniden | 📢 @nikestoretr",
        "bas":        "🕌 *ВРЕМЕНА НАМАЗА*\n━━━━━━━━━━━━━━━━━━\n📍 {s} / {i}\n📅 {d}\n━━━━━━━━━━━━━━━━━━\n\n",
        "im":  "🌙 Фаджр   : `{t}`",
        "gu":  "☀️  Восход  : `{t}`",
        "og":  "🌤️ Зухр    : `{t}`",
        "ik":  "🌇 Аср     : `{t}`",
        "ak":  "🌆 Магриб  : `{t}`",
        "ya":  "🌃 Иша     : `{t}`",
        "son": "\n\n⏭️ Следующий: *{v}* — `{t}`",
        "ayar": "⚙️ *НАСТРОЙКИ*\n━━━━━━━━━━━━━━━━━━\n🌍 Страна : {u}\n🏙️ Город  : {s}\n📍 Район  : {i}\n⏰ Аларм  : за {m} мин\n🔧 API    : {a}\n━━━━━━━━━━━━━━━━━━",
        "yard": "📖 *КОМАНДЫ*\n━━━━━━━━━━━━━━━━━━\n• /start — Запуск\n• /vakitler — Намазы сегодня\n• /yarin — Завтра\n• /haftalik — Неделя\n• /konum — Местоположение\n• /uyari — Аларм\n• /dil — Язык\n• /ayarlar — Настройки\n• /durdur — Остановить\n• /devam — Возобновить\n• /ozelgunler — Исламские дни\n━━━━━━━━━━━━━━━━━━\n🔧 *Команда для группы (Админ):*\n• /grubayarla — Авто уведомления\n━━━━━━━━━━━━━━━━━━\n👤 @NikeCheatYeniden | 📢 @nikestoretr",
        "hak": "🕌 *БОТ НАМАЗА*\n━━━━━━━━━━━━━━━━━━\n👤 @NikeCheatYeniden\n📢 @nikestoretr\n🌍 Все страны\n🔔 Автоматические напоминания\n━━━━━━━━━━━━━━━━━━\n🤲 Да примет Аллах!",
        "grup": "🕌 *Бот добавлен!*\n━━━━━━━━━━━━━━━━━━\n• /konum — Местоположение\n• /vakitler — Времена намаза\n━━━━━━━━━━━━━━━━━━\n👤 @NikeCheatYeniden | 📢 @nikestoretr",
        "stat": "📊 *СТАТИСТИКА*\n━━━━━━━━━━━━━━━━━━\n👥 Пользователи : {t}\n✅ Активные     : {a}\n🔔 Сегодня      : {b}\n📨 Всего        : {top}\n━━━━━━━━━━━━━━━━━━",
        "ad": {"Fajr":"Фаджр","Sunrise":"Восход","Dhuhr":"Зухр","Asr":"Аср","Maghrib":"Магриб","Isha":"Иша"},
        "menu_bilgi": "🕌 *БОТ НАМАЗА*\n━━━━━━━━━━━━━━━━━━\n📍 {s} / {i}\n━━━━━━━━━━━━━━━━━━",
        "konum_ok": "✅ *МЕСТОПОЛОЖЕНИЕ УСТАНОВЛЕНО!*\n━━━━━━━━━━━━━━━━━━\n🌍 Страна : {u}\n🏙️ Город  : {s}\n📍 Район  : {i}\n━━━━━━━━━━━━━━━━━━\n• /vakitler для времён намаза.",
        "hata_api": "❌ *Не удалось получить времена намаза!*\n\nПовторите попытку.\n• /konum — Переустановить местоположение",
        "spam":     "⏳ *Слишком быстро!*\n━━━━━━━━━━━━━━━━━━\n{emoji} Подождите *{sn} секунд*.\n━━━━━━━━━━━━━━━━━━\n💡 Минимум *5 секунд* между командами.",
        "ban":      "🚫 Ваш доступ ограничен.",
        "bilinmeyen": "❌ *`{cmd}`* — Неизвестная команда!\n━━━━━━━━━━━━━━━━━━\n📖 Все команды: /yardim\n🏠 Главное меню: /start",    },
    "az": {
        "hosgeldin":  "🌙 *Namaz Vaxtları Botuna Xoş Gəldiniz!*\n\n✦ Dilinizi seçin:",
        "dil_ok":     "✅ Dil Azərbaycanca olaraq quruldu.",
        "ulke":       "🌍 *Ölkənizi seçin:*",
        "il":         "🏙️ *Şəhərinizi seçin:*",
        "ilce":       "📍 *{s}* — Rayonu seçin:",
        "yok":        "❌ Məkan qurulmayıb!\n\n• /konum — Məkan qur",
        "usor":       "⏰ *Namazdan neçə dəqiqə əvvəl?*",
        "uok":        "✅ *{m} dəqiqə* əvvəl xəbərdarlıq.",
        "apisor":     "🔧 *API seçin:*\n\n• 🌍 Aladhan — Dünya\n• 🤖 Avtomatik — Tövsiyə",
        "apiok":      "✅ API *{a}* seçildi.",
        "dur":        "🔕 Xəbərdarlıqlar dayandırıldı.\n\n• /devam — Davam et",
        "dev":        "🔔 Xəbərdarlıqlar bərpa edildi!",
        "umsg":       "🔔 *NAMAZ XƏBƏRDARLIĞı!*\n━━━━━━━━━━━━━━━━━━\n📍 {s} / {i}\n🕌 Namaz  : *{v}*\n⏱️ Qalan  : *{m} dəqiqə*\n🕐 Saat   : `{t}`\n━━━━━━━━━━━━━━━━━━\n🤲 Namazın qəbul olsun!\n👤 @NikeCheatYeniden | 📢 @nikestoretr",
        "bas":        "🕌 *NAMAZ VAXTLARI*\n━━━━━━━━━━━━━━━━━━\n📍 {s} / {i}\n📅 {d}\n━━━━━━━━━━━━━━━━━━\n\n",
        "im":  "🌙 Sübh    : `{t}`",
        "gu":  "☀️  Gündoğma: `{t}`",
        "og":  "🌤️ Zöhr    : `{t}`",
        "ik":  "🌇 Əsr     : `{t}`",
        "ak":  "🌆 Axşam   : `{t}`",
        "ya":  "🌃 Gecə    : `{t}`",
        "son": "\n\n⏭️ Növbəti: *{v}* — `{t}`",
        "ayar": "⚙️ *AYARLAR*\n━━━━━━━━━━━━━━━━━━\n🌍 Ölkə   : {u}\n🏙️ Şəhər  : {s}\n📍 Rayon  : {i}\n⏰ Alarm  : {m} dəq\n🔧 API    : {a}\n━━━━━━━━━━━━━━━━━━",
        "yard": "📖 *ƏMRLƏR (güncəllənmiş)*\n━━━━━━━━━━━━━━━━━━\n• /start — Başlat\n• /vakitler — Vaxtlar\n• /yarin — Sabah\n• /haftalik — Həftəlik\n• /konum — Məkan\n• /uyari — Alarm\n• /dil — Dil\n• /ayarlar — Ayarlar\n• /durdur — Dayandır\n• /devam — Davam et\n━━━━━━━━━━━━━━━━━━\n👤 @NikeCheatYeniden | 📢 @nikestoretr",
        "hak": "🕌 *NAMAZ VAXTLARI BOTU*\n━━━━━━━━━━━━━━━━━━\n👤 @NikeCheatYeniden\n📢 @nikestoretr\n🌍 Bütün ölkələr\n🔔 Avtomatik xəbərdarlıq\n━━━━━━━━━━━━━━━━━━\n🤲 Namazın qəbul olsun!",
        "grup": "🕌 *Namaz Botu əlavə edildi!*\n━━━━━━━━━━━━━━━━━━\n• /konum — Məkan\n• /vakitler — Vaxtlar\n━━━━━━━━━━━━━━━━━━\n👤 @NikeCheatYeniden | 📢 @nikestoretr",
        "stat": "📊 *STATİSTİKA*\n━━━━━━━━━━━━━━━━━━\n👥 İstifadəçi : {t}\n✅ Aktiv      : {a}\n🔔 Bu gün     : {b}\n📨 Ümumi      : {top}\n━━━━━━━━━━━━━━━━━━",
        "ad": {"Fajr":"Sübh","Sunrise":"Gündoğma","Dhuhr":"Zöhr","Asr":"Əsr","Maghrib":"Axşam","Isha":"Gecə"},
        "menu_bilgi": "🕌 *NAMAZ BOTU*\n━━━━━━━━━━━━━━━━━━\n📍 {s} / {i}\n━━━━━━━━━━━━━━━━━━",
        "konum_ok": "✅ *MƏKAN QURULDU!*\n━━━━━━━━━━━━━━━━━━\n🌍 Ölkə   : {u}\n🏙️ Şəhər  : {s}\n📍 Rayon  : {i}\n━━━━━━━━━━━━━━━━━━\n• /vakitler vaxtlar üçün.",
        "hata_api": "❌ *Vaxtlar alına bilmədi!*\n\nTekrar cəhd edin.\n• /konum — Məkanı yenidən qurun",
        "spam":     "⏳ *Çox sürətlisiniz!*\n━━━━━━━━━━━━━━━━━━\n{emoji} *{sn} saniyə* gözləyin.\n━━━━━━━━━━━━━━━━━━\n💡 Əmrlər arasında min. *5 saniyə* lazımdır.",
        "ban":      "🚫 Girişiniz məhdudlaşdırılıb.",
        "bilinmeyen": "❌ *`{cmd}`* — Naməlum əmr!\n━━━━━━━━━━━━━━━━━━\n📖 Bütün əmrlər: /yardim\n🏠 Əsas menyu: /start",    },
    "bs": {
        "hosgeldin":  "🌙 *Dobrodošli u Bot za Namaz!*\n\n✦ Odaberite jezik:",
        "dil_ok":     "✅ Jezik postavljen na Bosanski.",
        "ulke":       "🌍 *Odaberite državu:*",
        "il":         "🏙️ *Odaberite grad:*",
        "ilce":       "📍 *{s}* — Odaberite općinu:",
        "yok":        "❌ Lokacija nije postavljena!\n\n• /konum — Postavi lokaciju",
        "usor":       "⏰ *Koliko minuta prije namaza podsjetnik?*",
        "uok":        "✅ Podsjetnik *{m} minuta* ranije.",
        "apisor":     "🔧 *Odaberite API:*\n\n• 🌍 Aladhan — Cijeli svijet\n• 🤖 Automatski — Preporučeno",
        "apiok":      "✅ API *{a}* odabran.",
        "dur":        "🔕 Podsjetnici zaustavljeni.\n\n• /devam — Nastavak",
        "dev":        "🔔 Podsjetnici nastavljeni!",
        "umsg":       "🔔 *PODSJETNIK ZA NAMAZ!*\n━━━━━━━━━━━━━━━━━━\n📍 {s} / {i}\n🕌 Namaz  : *{v}*\n⏱️ Za     : *{m} minuta*\n🕐 Saat   : `{t}`\n━━━━━━━━━━━━━━━━━━\n🤲 Allah kabul etsin!\n👤 @NikeCheatYeniden | 📢 @nikestoretr",
        "bas":        "🕌 *NAMASKA VREMENA*\n━━━━━━━━━━━━━━━━━━\n📍 {s} / {i}\n📅 {d}\n━━━━━━━━━━━━━━━━━━\n\n",
        "im":  "🌙 Sabah   : `{t}`",
        "gu":  "☀️  Izlazak : `{t}`",
        "og":  "🌤️ Podne   : `{t}`",
        "ik":  "🌇 Ikindija: `{t}`",
        "ak":  "🌆 Akšam   : `{t}`",
        "ya":  "🌃 Jacija  : `{t}`",
        "son": "\n\n⏭️ Sljedeće: *{v}* — `{t}`",
        "ayar": "⚙️ *POSTAVKE*\n━━━━━━━━━━━━━━━━━━\n🌍 Država : {u}\n🏙️ Grad   : {s}\n📍 Općina : {i}\n⏰ Alarm  : {m} min\n🔧 API    : {a}\n━━━━━━━━━━━━━━━━━━",
        "yard": "📖 *KOMANDE*\n━━━━━━━━━━━━━━━━━━\n• /start — Pokreni\n• /vakitler — Namazi danas\n• /yarin — Sutra\n• /haftalik — Sedmica\n• /konum — Lokacija\n• /uyari — Alarm\n• /dil — Jezik\n• /ayarlar — Postavke\n• /durdur — Zaustavi\n• /devam — Nastavi\n• /ozelgunler — Islamski dani\n━━━━━━━━━━━━━━━━━━\n🔧 *Grupna komanda (Admin):*\n• /grubayarla — Auto obavještenja\n━━━━━━━━━━━━━━━━━━\n👤 @NikeCheatYeniden | 📢 @nikestoretr",
        "hak": "🕌 *BOT ZA NAMAZ*\n━━━━━━━━━━━━━━━━━━\n👤 @NikeCheatYeniden\n📢 @nikestoretr\n🌍 Sve države\n🔔 Automatski podsjetnici\n━━━━━━━━━━━━━━━━━━\n🤲 Allah kabul etsin!",
        "grup": "🕌 *Bot za Namaz dodan!*\n━━━━━━━━━━━━━━━━━━\n• /konum — Lokacija\n• /vakitler — Namaska vremena\n━━━━━━━━━━━━━━━━━━\n👤 @NikeCheatYeniden | 📢 @nikestoretr",
        "stat": "📊 *STATISTIKA*\n━━━━━━━━━━━━━━━━━━\n👥 Korisnici : {t}\n✅ Aktivnih  : {a}\n🔔 Danas     : {b}\n📨 Ukupno    : {top}\n━━━━━━━━━━━━━━━━━━",
        "ad": {"Fajr":"Sabah","Sunrise":"Izlazak","Dhuhr":"Podne","Asr":"Ikindija","Maghrib":"Akšam","Isha":"Jacija"},
        "menu_bilgi": "🕌 *BOT ZA NAMAZ*\n━━━━━━━━━━━━━━━━━━\n📍 {s} / {i}\n━━━━━━━━━━━━━━━━━━",
        "konum_ok": "✅ *LOKACIJA POSTAVLJENA!*\n━━━━━━━━━━━━━━━━━━\n🌍 Država : {u}\n🏙️ Grad   : {s}\n📍 Općina : {i}\n━━━━━━━━━━━━━━━━━━\n• /vakitler za namaska vremena.",
        "hata_api": "❌ *Namaska vremena nisu dostupna!*\n\nPokušajte ponovo.\n• /konum — Ponovo postavi lokaciju",
        "spam":     "⏳ *Previše brzo!*\n━━━━━━━━━━━━━━━━━━\n{emoji} Čekajte *{sn} sekundi*.\n━━━━━━━━━━━━━━━━━━\n💡 Minimum *5 sekundi* između komandi.",
        "ban":      "🚫 Vaš pristup je ograničen.",
        "bilinmeyen": "❌ *`{cmd}`* — Nepoznata komanda!\n━━━━━━━━━━━━━━━━━━\n📖 Sve komande: /yardim\n🏠 Glavni meni: /start",    },
    "sq": {
        "hosgeldin":  "🌙 *Mirë se vini te Boti i Kohës së Namazit!*\n\n✦ Zgjidhni gjuhën tuaj:",
        "dil_ok":     "✅ Gjuha është caktuar në Shqip.",
        "ulke":       "🌍 *Zgjidhni vendin tuaj:*",
        "il":         "🏙️ *Zgjidhni qytetin:*",
        "ilce":       "📍 *{s}* — Zgjidhni lagjen:",
        "yok":        "❌ Vendndodhja nuk është caktuar!\n\n• /konum — Cakto vendndodhjen",
        "usor":       "⏰ *Sa minuta para namazit?*",
        "uok":        "✅ Njoftimi *{m} minuta* para namazit.",
        "apisor":     "🔧 *Zgjidhni API:*\n\n• 🌍 Aladhan — Gjithë bota\n• 🤖 Automatik — Rekomanduar",
        "apiok":      "✅ API *{a}* zgjedhur.",
        "dur":        "🔕 Njoftimet ndaluar.\n\n• /devam — Vazhdo",
        "dev":        "🔔 Njoftimet rifilluan!",
        "umsg":       "🔔 *KUJTUES NAMAZI!*\n━━━━━━━━━━━━━━━━━━\n📍 {s} / {i}\n🕌 Namazi : *{v}*\n⏱️ Pas    : *{m} minutash*\n🕐 Ora    : `{t}`\n━━━━━━━━━━━━━━━━━━\n🤲 Allahu pranoftë!\n👤 @NikeCheatYeniden | 📢 @nikestoretr",
        "bas":        "🕌 *KOHËT E NAMAZIT*\n━━━━━━━━━━━━━━━━━━\n📍 {s} / {i}\n📅 {d}\n━━━━━━━━━━━━━━━━━━\n\n",
        "im":  "🌙 Sabahu  : `{t}`",
        "gu":  "☀️  Lindja  : `{t}`",
        "og":  "🌤️ Dreka   : `{t}`",
        "ik":  "🌇 Ikindia : `{t}`",
        "ak":  "🌆 Akshami : `{t}`",
        "ya":  "🌃 Jacia   : `{t}`",
        "son": "\n\n⏭️ I radhës: *{v}* — `{t}`",
        "ayar": "⚙️ *CILËSIMET*\n━━━━━━━━━━━━━━━━━━\n🌍 Vendi  : {u}\n🏙️ Qyteti : {s}\n📍 Lagjja : {i}\n⏰ Alarm  : {m} min\n🔧 API    : {a}\n━━━━━━━━━━━━━━━━━━",
        "yard": "📖 *KOMANDAT*\n━━━━━━━━━━━━━━━━━━\n• /start — Nis\n• /vakitler — Kohët sot\n• /yarin — Nesër\n• /haftalik — Java\n• /konum — Vendndodhja\n• /uyari — Alarm\n• /dil — Gjuha\n• /ayarlar — Cilësime\n• /durdur — Ndalo\n• /devam — Vazhdo\n• /ozelgunler — Ditë islame\n━━━━━━━━━━━━━━━━━━\n🔧 *Komanda grupit (Admin):*\n• /grubayarla — Njoftime automatike\n━━━━━━━━━━━━━━━━━━\n👤 @NikeCheatYeniden | 📢 @nikestoretr",
        "hak": "🕌 *BOTI I NAMAZIT*\n━━━━━━━━━━━━━━━━━━\n👤 @NikeCheatYeniden\n📢 @nikestoretr\n🌍 Të gjitha vendet\n🔔 Kujtues automatik\n━━━━━━━━━━━━━━━━━━\n🤲 Allahu pranoftë!",
        "grup": "🕌 *Boti shtuar në grup!*\n━━━━━━━━━━━━━━━━━━\n• /konum — Vendndodhja\n• /vakitler — Kohët\n━━━━━━━━━━━━━━━━━━\n👤 @NikeCheatYeniden | 📢 @nikestoretr",
        "stat": "📊 *STATISTIKA*\n━━━━━━━━━━━━━━━━━━\n👥 Përdorues : {t}\n✅ Aktiv     : {a}\n🔔 Sot       : {b}\n📨 Gjithsej  : {top}\n━━━━━━━━━━━━━━━━━━",
        "ad": {"Fajr":"Sabahu","Sunrise":"Lindja","Dhuhr":"Dreka","Asr":"Ikindia","Maghrib":"Akshami","Isha":"Jacia"},
        "menu_bilgi": "🕌 *BOTI I NAMAZIT*\n━━━━━━━━━━━━━━━━━━\n📍 {s} / {i}\n━━━━━━━━━━━━━━━━━━",
        "konum_ok": "✅ *VENDNDODHJA U CAKTUA!*\n━━━━━━━━━━━━━━━━━━\n🌍 Vendi  : {u}\n🏙️ Qyteti : {s}\n📍 Lagjja : {i}\n━━━━━━━━━━━━━━━━━━\n• /vakitler për kohët.",
        "hata_api": "❌ *Kohët e namazit nuk mund të merren!*\n\nProvo përsëri.\n• /konum — Ricakto vendndodhjen",
        "spam":     "⏳ *Shumë shpejt!*\n━━━━━━━━━━━━━━━━━━\n{emoji} Prisni *{sn} sekonda*.\n━━━━━━━━━━━━━━━━━━\n💡 Minimum *5 sekonda* ndërmjet komandave.",
        "ban":      "🚫 Aksesi juaj është i kufizuar.",
        "bilinmeyen": "❌ *`{cmd}`* — Komandë e panjohur!\n━━━━━━━━━━━━━━━━━━\n📖 Të gjitha komandat: /yardim\n🏠 Menyja kryesore: /start",    },
}

def T(lang):
    return M.get(lang) or M["tr"]

# ═══════════════════════════════════════════════
#  ÜLKE / ŞEHİR / İLÇE VERİSİ
# ═══════════════════════════════════════════════
ULKELER = {
    "🇹🇷 Türkiye":      ("TR", "tr"),
    "🇩🇪 Almanya":      ("DE", "de"),
    "🇫🇷 Fransa":       ("FR", "fr"),
    "🇳🇱 Hollanda":     ("NL", "nl"),
    "🇧🇪 Belçika":      ("BE", "nl"),
    "🇬🇧 İngiltere":    ("GB", "en"),
    "🇨🇭 İsviçre":      ("CH", "de"),
    "🇦🇹 Avusturya":    ("AT", "de"),
    "🇸🇪 İsveç":        ("SE", "en"),
    "🇳🇴 Norveç":       ("NO", "en"),
    "🇩🇰 Danimarka":    ("DK", "en"),
    "🇺🇸 Amerika":      ("US", "en"),
    "🇨🇦 Kanada":       ("CA", "en"),
    "🇸🇦 S.Arabistan":  ("SA", "ar"),
    "🇪🇬 Mısır":        ("EG", "ar"),
    "🇲🇦 Fas":          ("MA", "ar"),
    "🇵🇰 Pakistan":     ("PK", "ur"),
    "🇮🇩 Endonezya":    ("ID", "id"),
    "🇲🇾 Malezya":      ("MY", "ms"),
    "🇦🇪 BAE":          ("AE", "ar"),
    "🇶🇦 Katar":        ("QA", "ar"),
    "🇰🇼 Kuveyt":       ("KW", "ar"),
    "🇦🇿 Azerbaycan":   ("AZ", "az"),
    "🇷🇺 Rusya":        ("RU", "ru"),
    "🇧🇦 Bosna":        ("BA", "bs"),
    "🇦🇱 Arnavutluk":   ("AL", "sq"),
    "🇸🇬 Singapur":     ("SG", "ms"),
    "🇽🇰 Kosova":       ("XK", "sq"),
    "🇩🇿 Cezayir":      ("DZ", "ar"),
    "🇹🇳 Tunus":        ("TN", "ar"),
    "🇱🇾 Libya":        ("LY", "ar"),
    "🇸🇩 Sudan":        ("SD", "ar"),
    "🇮🇶 Irak":         ("IQ", "ar"),
    "🇸🇾 Suriye":       ("SY", "ar"),
    "🇯🇴 Ürdün":        ("JO", "ar"),
    "🇱🇧 Lübnan":       ("LB", "ar"),
    "🇾🇪 Yemen":        ("YE", "ar"),
    "🇦🇫 Afganistan":   ("AF", "ur"),
    "🇧🇩 Bangladeş":    ("BD", "en"),
    "🇰🇿 Kazakistan":   ("KZ", "ru"),
    "🇺🇿 Özbekistan":   ("UZ", "ru"),
    "🇮🇷 İran":         ("IR", "ar"),
    "🇴🇲 Umman":        ("OM", "ar"),
    "🇧🇭 Bahreyn":      ("BH", "ar"),
    "🇳🇬 Nijerya":      ("NG", "en"),
    "🇸🇳 Senegal":      ("SN", "fr"),
    "🇵🇸 Filistin":     ("PS", "ar"),
    "🇲🇻 Maldivler":    ("MV", "en"),
    "🇲🇰 K.Makedonya":  ("MK", "sq"),
    "🇰🇬 Kırgızistan":  ("KG", "ru"),
    "🇹🇯 Tacikistan":   ("TJ", "ru"),
}


# ═══════════════════════════════════════════════
#  ÜLKE İSİMLERİ ÇEVİRİLERİ
# ═══════════════════════════════════════════════
ULKE_CEVIRI = {
    "tr": {k: k for k in [
        "🇹🇷 Türkiye","🇩🇪 Almanya","🇫🇷 Fransa","🇳🇱 Hollanda","🇧🇪 Belçika","🇬🇧 İngiltere",
        "🇨🇭 İsviçre","🇦🇹 Avusturya","🇸🇪 İsveç","🇳🇴 Norveç","🇩🇰 Danimarka","🇺🇸 Amerika",
        "🇨🇦 Kanada","🇸🇦 S.Arabistan","🇪🇬 Mısır","🇲🇦 Fas","🇵🇰 Pakistan","🇮🇩 Endonezya",
        "🇲🇾 Malezya","🇦🇪 BAE","🇶🇦 Katar","🇰🇼 Kuveyt","🇦🇿 Azerbaycan","🇷🇺 Rusya",
        "🇧🇦 Bosna","🇦🇱 Arnavutluk","🇸🇬 Singapur","🇽🇰 Kosova","🇩🇿 Cezayir","🇹🇳 Tunus",
        "🇱🇾 Libya","🇸🇩 Sudan","🇮🇶 Irak","🇸🇾 Suriye","🇯🇴 Ürdün","🇱🇧 Lübnan",
        "🇾🇪 Yemen","🇦🇫 Afganistan","🇧🇩 Bangladeş","🇰🇿 Kazakistan","🇺🇿 Özbekistan",
        "🇮🇷 İran","🇴🇲 Umman","🇧🇭 Bahreyn","🇳🇬 Nijerya","🇸🇳 Senegal","🇵🇸 Filistin",
        "🇲🇻 Maldivler","🇲🇰 K.Makedonya","🇰🇬 Kırgızistan","🇹🇯 Tacikistan"
    ]},
    "ar": {
        "🇹🇷 Türkiye":"🇹🇷 تركيا","🇩🇪 Almanya":"🇩🇪 ألمانيا","🇫🇷 Fransa":"🇫🇷 فرنسا",
        "🇳🇱 Hollanda":"🇳🇱 هولندا","🇧🇪 Belçika":"🇧🇪 بلجيكا","🇬🇧 İngiltere":"🇬🇧 بريطانيا",
        "🇨🇭 İsviçre":"🇨🇭 سويسرا","🇦🇹 Avusturya":"🇦🇹 النمسا","🇸🇪 İsveç":"🇸🇪 السويد",
        "🇳🇴 Norveç":"🇳🇴 النرويج","🇩🇰 Danimarka":"🇩🇰 الدنمارك","🇺🇸 Amerika":"🇺🇸 أمريكا",
        "🇨🇦 Kanada":"🇨🇦 كندا","🇸🇦 S.Arabistan":"🇸🇦 السعودية","🇪🇬 Mısır":"🇪🇬 مصر",
        "🇲🇦 Fas":"🇲🇦 المغرب","🇵🇰 Pakistan":"🇵🇰 باكستان","🇮🇩 Endonezya":"🇮🇩 إندونيسيا",
        "🇲🇾 Malezya":"🇲🇾 ماليزيا","🇦🇪 BAE":"🇦🇪 الإمارات","🇶🇦 Katar":"🇶🇦 قطر",
        "🇰🇼 Kuveyt":"🇰🇼 الكويت","🇦🇿 Azerbaycan":"🇦🇿 أذربيجان","🇷🇺 Rusya":"🇷🇺 روسيا",
        "🇧🇦 Bosna":"🇧🇦 البوسنة","🇦🇱 Arnavutluk":"🇦🇱 ألبانيا","🇸🇬 Singapur":"🇸🇬 سنغافورة",
        "🇽🇰 Kosova":"🇽🇰 كوسوفو","🇩🇿 Cezayir":"🇩🇿 الجزائر","🇹🇳 Tunus":"🇹🇳 تونس",
        "🇱🇾 Libya":"🇱🇾 ليبيا","🇸🇩 Sudan":"🇸🇩 السودان","🇮🇶 Irak":"🇮🇶 العراق",
        "🇸🇾 Suriye":"🇸🇾 سوريا","🇯🇴 Ürdün":"🇯🇴 الأردن","🇱🇧 Lübnan":"🇱🇧 لبنان",
        "🇾🇪 Yemen":"🇾🇪 اليمن","🇦🇫 Afganistan":"🇦🇫 أفغانستان","🇧🇩 Bangladeş":"🇧🇩 بنغلاديش",
        "🇰🇿 Kazakistan":"🇰🇿 كازاخستان","🇺🇿 Özbekistan":"🇺🇿 أوزبكستان","🇮🇷 İran":"🇮🇷 إيران",
        "🇴🇲 Umman":"🇴🇲 عُمان","🇧🇭 Bahreyn":"🇧🇭 البحرين","🇳🇬 Nijerya":"🇳🇬 نيجيريا",
        "🇸🇳 Senegal":"🇸🇳 السنغال","🇵🇸 Filistin":"🇵🇸 فلسطين","🇲🇻 Maldivler":"🇲🇻 المالديف",
        "🇲🇰 K.Makedonya":"🇲🇰 مقدونيا","🇰🇬 Kırgızistan":"🇰🇬 قيرغيزستان","🇹🇯 Tacikistan":"🇹🇯 طاجيكستان",
    "ilce_yok": "ℹ️ Nuk ka lagje për *{s}*.\n✅ Vendndodhja *{s}* u caktua.",
    "ilce_yok": "ℹ️ Nema okruga za *{s}*.\n✅ Lokacija *{s}* postavljena.",
    "ilce_yok": "ℹ️ *{s}* üçün rayon yoxdur.\n✅ Məkan *{s}* ayarlandı.",
    "ilce_yok": "ℹ️ Нет районов для *{s}*.\n✅ Местоположение *{s}* установлено.",
    "ilce_yok": "ℹ️ Tiada daerah untuk *{s}*.\n✅ Lokasi *{s}* ditetapkan.",
    "ilce_yok": "ℹ️ Tidak ada kecamatan untuk *{s}*.\n✅ Lokasi *{s}* telah diatur.",
    "ilce_yok": "ℹ️ *{s}* کے لیے کوئی ضلع نہیں۔\n✅ مقام *{s}* مقرر ہو گیا۔",
    "ilce_yok": "ℹ️ No districts available for *{s}*.\n✅ Location set to *{s}*.",
    "ilce_yok": "ℹ️ Geen wijken voor *{s}*.\n✅ Locatie *{s}* ingesteld.",
    "ilce_yok": "ℹ️ Aucun quartier pour *{s}*.\n✅ Localisation *{s}* définie.",
    "ilce_yok": "ℹ️ Für *{s}* gibt es keine Bezirke.\n✅ Standort *{s}* eingestellt.",
    "ilce_yok": "ℹ️ لا توجد أحياء لـ *{s}*.\n✅ تم تحديد الموقع *{s}*.",
    "ilce_yok": "ℹ️ *{s}* ili için ilçe listesi mevcut değil.\n✅ Konum *{s}* olarak ayarlandı.",
    },
    "de": {
        "🇹🇷 Türkiye":"🇹🇷 Türkei","🇩🇪 Almanya":"🇩🇪 Deutschland","🇫🇷 Fransa":"🇫🇷 Frankreich",
        "🇳🇱 Hollanda":"🇳🇱 Niederlande","🇧🇪 Belçika":"🇧🇪 Belgien","🇬🇧 İngiltere":"🇬🇧 Großbritannien",
        "🇨🇭 İsviçre":"🇨🇭 Schweiz","🇦🇹 Avusturya":"🇦🇹 Österreich","🇸🇪 İsveç":"🇸🇪 Schweden",
        "🇳🇴 Norveç":"🇳🇴 Norwegen","🇩🇰 Danimarka":"🇩🇰 Dänemark","🇺🇸 Amerika":"🇺🇸 Amerika",
        "🇨🇦 Kanada":"🇨🇦 Kanada","🇸🇦 S.Arabistan":"🇸🇦 Saudi-Arabien","🇪🇬 Mısır":"🇪🇬 Ägypten",
        "🇲🇦 Fas":"🇲🇦 Marokko","🇵🇰 Pakistan":"🇵🇰 Pakistan","🇮🇩 Endonezya":"🇮🇩 Indonesien",
        "🇲🇾 Malezya":"🇲🇾 Malaysia","🇦🇪 BAE":"🇦🇪 VAE","🇶🇦 Katar":"🇶🇦 Katar",
        "🇰🇼 Kuveyt":"🇰🇼 Kuwait","🇦🇿 Azerbaycan":"🇦🇿 Aserbaidschan","🇷🇺 Rusya":"🇷🇺 Russland",
        "🇧🇦 Bosna":"🇧🇦 Bosnien","🇦🇱 Arnavutluk":"🇦🇱 Albanien","🇸🇬 Singapur":"🇸🇬 Singapur",
        "🇽🇰 Kosova":"🇽🇰 Kosovo","🇩🇿 Cezayir":"🇩🇿 Algerien","🇹🇳 Tunus":"🇹🇳 Tunesien",
        "🇱🇾 Libya":"🇱🇾 Libyen","🇸🇩 Sudan":"🇸🇩 Sudan","🇮🇶 Irak":"🇮🇶 Irak",
        "🇸🇾 Suriye":"🇸🇾 Syrien","🇯🇴 Ürdün":"🇯🇴 Jordanien","🇱🇧 Lübnan":"🇱🇧 Libanon",
        "🇾🇪 Yemen":"🇾🇪 Jemen","🇦🇫 Afganistan":"🇦🇫 Afghanistan","🇧🇩 Bangladeş":"🇧🇩 Bangladesch",
        "🇰🇿 Kazakistan":"🇰🇿 Kasachstan","🇺🇿 Özbekistan":"🇺🇿 Usbekistan","🇮🇷 İran":"🇮🇷 Iran",
        "🇴🇲 Umman":"🇴🇲 Oman","🇧🇭 Bahreyn":"🇧🇭 Bahrain","🇳🇬 Nijerya":"🇳🇬 Nigeria",
        "🇸🇳 Senegal":"🇸🇳 Senegal","🇵🇸 Filistin":"🇵🇸 Palästina","🇲🇻 Maldivler":"🇲🇻 Malediven",
        "🇲🇰 K.Makedonya":"🇲🇰 N.Mazedonien","🇰🇬 Kırgızistan":"🇰🇬 Kirgisistan","🇹🇯 Tacikistan":"🇹🇯 Tadschikistan",
    },
    "fr": {
        "🇹🇷 Türkiye":"🇹🇷 Turquie","🇩🇪 Almanya":"🇩🇪 Allemagne","🇫🇷 Fransa":"🇫🇷 France",
        "🇳🇱 Hollanda":"🇳🇱 Pays-Bas","🇧🇪 Belçika":"🇧🇪 Belgique","🇬🇧 İngiltere":"🇬🇧 Royaume-Uni",
        "🇨🇭 İsviçre":"🇨🇭 Suisse","🇦🇹 Avusturya":"🇦🇹 Autriche","🇸🇪 İsveç":"🇸🇪 Suède",
        "🇳🇴 Norveç":"🇳🇴 Norvège","🇩🇰 Danimarka":"🇩🇰 Danemark","🇺🇸 Amerika":"🇺🇸 États-Unis",
        "🇨🇦 Kanada":"🇨🇦 Canada","🇸🇦 S.Arabistan":"🇸🇦 Arabie S.","🇪🇬 Mısır":"🇪🇬 Égypte",
        "🇲🇦 Fas":"🇲🇦 Maroc","🇵🇰 Pakistan":"🇵🇰 Pakistan","🇮🇩 Endonezya":"🇮🇩 Indonésie",
        "🇲🇾 Malezya":"🇲🇾 Malaisie","🇦🇪 BAE":"🇦🇪 Émirats","🇶🇦 Katar":"🇶🇦 Qatar",
        "🇰🇼 Kuveyt":"🇰🇼 Koweït","🇦🇿 Azerbaycan":"🇦🇿 Azerbaïdjan","🇷🇺 Rusya":"🇷🇺 Russie",
        "🇧🇦 Bosna":"🇧🇦 Bosnie","🇦🇱 Arnavutluk":"🇦🇱 Albanie","🇸🇬 Singapur":"🇸🇬 Singapour",
        "🇽🇰 Kosova":"🇽🇰 Kosovo","🇩🇿 Cezayir":"🇩🇿 Algérie","🇹🇳 Tunus":"🇹🇳 Tunisie",
        "🇱🇾 Libya":"🇱🇾 Libye","🇸🇩 Sudan":"🇸🇩 Soudan","🇮🇶 Irak":"🇮🇶 Irak",
        "🇸🇾 Suriye":"🇸🇾 Syrie","🇯🇴 Ürdün":"🇯🇴 Jordanie","🇱🇧 Lübnan":"🇱🇧 Liban",
        "🇾🇪 Yemen":"🇾🇪 Yémen","🇦🇫 Afganistan":"🇦🇫 Afghanistan","🇧🇩 Bangladeş":"🇧🇩 Bangladesh",
        "🇰🇿 Kazakistan":"🇰🇿 Kazakhstan","🇺🇿 Özbekistan":"🇺🇿 Ouzbékistan","🇮🇷 İran":"🇮🇷 Iran",
        "🇴🇲 Umman":"🇴🇲 Oman","🇧🇭 Bahreyn":"🇧🇭 Bahreïn","🇳🇬 Nijerya":"🇳🇬 Nigéria",
        "🇸🇳 Senegal":"🇸🇳 Sénégal","🇵🇸 Filistin":"🇵🇸 Palestine","🇲🇻 Maldivler":"🇲🇻 Maldives",
        "🇲🇰 K.Makedonya":"🇲🇰 Macédoine","🇰🇬 Kırgızistan":"🇰🇬 Kirghizistan","🇹🇯 Tacikistan":"🇹🇯 Tadjikistan",
    },
    "en": {
        "🇹🇷 Türkiye":"🇹🇷 Turkey","🇩🇪 Almanya":"🇩🇪 Germany","🇫🇷 Fransa":"🇫🇷 France",
        "🇳🇱 Hollanda":"🇳🇱 Netherlands","🇧🇪 Belçika":"🇧🇪 Belgium","🇬🇧 İngiltere":"🇬🇧 UK",
        "🇨🇭 İsviçre":"🇨🇭 Switzerland","🇦🇹 Avusturya":"🇦🇹 Austria","🇸🇪 İsveç":"🇸🇪 Sweden",
        "🇳🇴 Norveç":"🇳🇴 Norway","🇩🇰 Danimarka":"🇩🇰 Denmark","🇺🇸 Amerika":"🇺🇸 USA",
        "🇨🇦 Kanada":"🇨🇦 Canada","🇸🇦 S.Arabistan":"🇸🇦 Saudi Arabia","🇪🇬 Mısır":"🇪🇬 Egypt",
        "🇲🇦 Fas":"🇲🇦 Morocco","🇵🇰 Pakistan":"🇵🇰 Pakistan","🇮🇩 Endonezya":"🇮🇩 Indonesia",
        "🇲🇾 Malezya":"🇲🇾 Malaysia","🇦🇪 BAE":"🇦🇪 UAE","🇶🇦 Katar":"🇶🇦 Qatar",
        "🇰🇼 Kuveyt":"🇰🇼 Kuwait","🇦🇿 Azerbaycan":"🇦🇿 Azerbaijan","🇷🇺 Rusya":"🇷🇺 Russia",
        "🇧🇦 Bosna":"🇧🇦 Bosnia","🇦🇱 Arnavutluk":"🇦🇱 Albania","🇸🇬 Singapur":"🇸🇬 Singapore",
        "🇽🇰 Kosova":"🇽🇰 Kosovo","🇩🇿 Cezayir":"🇩🇿 Algeria","🇹🇳 Tunus":"🇹🇳 Tunisia",
        "🇱🇾 Libya":"🇱🇾 Libya","🇸🇩 Sudan":"🇸🇩 Sudan","🇮🇶 Irak":"🇮🇶 Iraq",
        "🇸🇾 Suriye":"🇸🇾 Syria","🇯🇴 Ürdün":"🇯🇴 Jordan","🇱🇧 Lübnan":"🇱🇧 Lebanon",
        "🇾🇪 Yemen":"🇾🇪 Yemen","🇦🇫 Afganistan":"🇦🇫 Afghanistan","🇧🇩 Bangladeş":"🇧🇩 Bangladesh",
        "🇰🇿 Kazakistan":"🇰🇿 Kazakhstan","🇺🇿 Özbekistan":"🇺🇿 Uzbekistan","🇮🇷 İran":"🇮🇷 Iran",
        "🇴🇲 Umman":"🇴🇲 Oman","🇧🇭 Bahreyn":"🇧🇭 Bahrain","🇳🇬 Nijerya":"🇳🇬 Nigeria",
        "🇸🇳 Senegal":"🇸🇳 Senegal","🇵🇸 Filistin":"🇵🇸 Palestine","🇲🇻 Maldivler":"🇲🇻 Maldives",
        "🇲🇰 K.Makedonya":"🇲🇰 N.Macedonia","🇰🇬 Kırgızistan":"🇰🇬 Kyrgyzstan","🇹🇯 Tacikistan":"🇹🇯 Tajikistan",
    },
    "ru": {
        "🇹🇷 Türkiye":"🇹🇷 Турция","🇩🇪 Almanya":"🇩🇪 Германия","🇫🇷 Fransa":"🇫🇷 Франция",
        "🇳🇱 Hollanda":"🇳🇱 Нидерланды","🇧🇪 Belçika":"🇧🇪 Бельгия","🇬🇧 İngiltere":"🇬🇧 Британия",
        "🇨🇭 İsviçre":"🇨🇭 Швейцария","🇦🇹 Avusturya":"🇦🇹 Австрия","🇸🇪 İsveç":"🇸🇪 Швеция",
        "🇳🇴 Norveç":"🇳🇴 Норвегия","🇩🇰 Danimarka":"🇩🇰 Дания","🇺🇸 Amerika":"🇺🇸 США",
        "🇨🇦 Kanada":"🇨🇦 Канада","🇸🇦 S.Arabistan":"🇸🇦 Саудовская А.","🇪🇬 Mısır":"🇪🇬 Египет",
        "🇲🇦 Fas":"🇲🇦 Марокко","🇵🇰 Pakistan":"🇵🇰 Пакистан","🇮🇩 Endonezya":"🇮🇩 Индонезия",
        "🇲🇾 Malezya":"🇲🇾 Малайзия","🇦🇪 BAE":"🇦🇪 ОАЭ","🇶🇦 Katar":"🇶🇦 Катар",
        "🇰🇼 Kuveyt":"🇰🇼 Кувейт","🇦🇿 Azerbaycan":"🇦🇿 Азербайджан","🇷🇺 Rusya":"🇷🇺 Россия",
        "🇧🇦 Bosna":"🇧🇦 Босния","🇦🇱 Arnavutluk":"🇦🇱 Албания","🇸🇬 Singapur":"🇸🇬 Сингапур",
        "🇽🇰 Kosova":"🇽🇰 Косово","🇩🇿 Cezayir":"🇩🇿 Алжир","🇹🇳 Tunus":"🇹🇳 Тунис",
        "🇱🇾 Libya":"🇱🇾 Ливия","🇸🇩 Sudan":"🇸🇩 Судан","🇮🇶 Irak":"🇮🇶 Ирак",
        "🇸🇾 Suriye":"🇸🇾 Сирия","🇯🇴 Ürdün":"🇯🇴 Иордания","🇱🇧 Lübnan":"🇱🇧 Ливан",
        "🇾🇪 Yemen":"🇾🇪 Йемен","🇦🇫 Afganistan":"🇦🇫 Афганистан","🇧🇩 Bangladeş":"🇧🇩 Бангладеш",
        "🇰🇿 Kazakistan":"🇰🇿 Казахстан","🇺🇿 Özbekistan":"🇺🇿 Узбекистан","🇮🇷 İran":"🇮🇷 Иран",
        "🇴🇲 Umman":"🇴🇲 Оман","🇧🇭 Bahreyn":"🇧🇭 Бахрейн","🇳🇬 Nijerya":"🇳🇬 Нигерия",
        "🇸🇳 Senegal":"🇸🇳 Сенегал","🇵🇸 Filistin":"🇵🇸 Палестина","🇲🇻 Maldivler":"🇲🇻 Мальдивы",
        "🇲🇰 K.Makedonya":"🇲🇰 С.Македония","🇰🇬 Kırgızistan":"🇰🇬 Кыргызстан","🇹🇯 Tacikistan":"🇹🇯 Таджикистан",
    },
}
# Diğer diller için TR ile aynı (kendi dillerinde ülke ismi zaten flag+Türkçe'yi kabul edebilir)
for _l in ["nl","ur","id","ms","az","bs","sq"]:
    ULKE_CEVIRI[_l] = ULKE_CEVIRI["en"].copy()
ULKE_CEVIRI["nl"] = ULKE_CEVIRI["de"].copy()

# Şehir koordinatları: (lat, lon, "İngilizce isim")
SEHIR_KOORDINAT = {
    "TR": {
        "Adana":        (37.0000, 35.3213, "Adana"),
        "Adıyaman":     (37.7648, 38.2786, "Adiyaman"),
        "Afyon":        (38.7507, 30.5567, "Afyonkarahisar"),
        "Ağrı":         (39.7191, 43.0503, "Agri"),
        "Amasya":       (40.6499, 35.8353, "Amasya"),
        "Ankara":       (39.9334, 32.8597, "Ankara"),
        "Antalya":      (36.8969, 30.7133, "Antalya"),
        "Artvin":       (41.1828, 41.8183, "Artvin"),
        "Aydın":        (37.8444, 27.8458, "Aydin"),
        "Balıkesir":    (39.6484, 27.8826, "Balikesir"),
        "Bilecik":      (40.1506, 29.9792, "Bilecik"),
        "Bingöl":       (38.8855, 40.4949, "Bingol"),
        "Bitlis":       (38.4006, 42.1095, "Bitlis"),
        "Bolu":         (40.7359, 31.6061, "Bolu"),
        "Burdur":       (37.7203, 30.2904, "Burdur"),
        "Bursa":        (40.1826, 29.0665, "Bursa"),
        "Çanakkale":    (40.1553, 26.4142, "Canakkale"),
        "Çankırı":      (40.6013, 33.6134, "Cankiri"),
        "Çorum":        (40.5506, 34.9556, "Corum"),
        "Denizli":      (37.7765, 29.0864, "Denizli"),
        "Diyarbakır":   (37.9144, 40.2306, "Diyarbakir"),
        "Edirne":       (41.6818, 26.5623, "Edirne"),
        "Elazığ":       (38.6810, 39.2264, "Elazig"),
        "Erzincan":     (39.7500, 39.5000, "Erzincan"),
        "Erzurum":      (39.9055, 41.2658, "Erzurum"),
        "Eskişehir":    (39.7767, 30.5206, "Eskisehir"),
        "Gaziantep":    (37.0662, 37.3833, "Gaziantep"),
        "Giresun":      (40.9128, 38.3895, "Giresun"),
        "Hakkari":      (37.5744, 43.7408, "Hakkari"),
        "Hatay":        (36.4018, 36.3498, "Hatay"),
        "Isparta":      (37.7648, 30.5566, "Isparta"),
        "İstanbul":     (41.0082, 28.9784, "Istanbul"),
        "İzmir":        (38.4192, 27.1287, "Izmir"),
        "Kars":         (40.6013, 43.0975, "Kars"),
        "Kastamonu":    (41.3887, 33.7827, "Kastamonu"),
        "Kayseri":      (38.7312, 35.4787, "Kayseri"),
        "Kırklareli":   (41.7333, 27.2167, "Kirklareli"),
        "Kırşehir":     (39.1425, 34.1709, "Kirsehir"),
        "Kocaeli":      (40.8533, 29.8815, "Kocaeli"),
        "Konya":        (37.8714, 32.4846, "Konya"),
        "Kütahya":      (39.4167, 29.9833, "Kutahya"),
        "Malatya":      (38.3552, 38.3095, "Malatya"),
        "Manisa":       (38.6191, 27.4289, "Manisa"),
        "K.Maraş":      (37.5858, 36.9371, "Kahramanmaras"),
        "Mardin":       (37.3212, 40.7245, "Mardin"),
        "Muğla":        (37.2153, 28.3636, "Mugla"),
        "Muş":          (38.7432, 41.4934, "Mus"),
        "Nevşehir":     (38.6939, 34.6857, "Nevsehir"),
        "Niğde":        (37.9667, 34.6833, "Nigde"),
        "Ordu":         (40.9860, 37.8797, "Ordu"),
        "Rize":         (41.0201, 40.5234, "Rize"),
        "Sakarya":      (40.6940, 30.4358, "Sakarya"),
        "Samsun":       (41.2928, 36.3313, "Samsun"),
        "Siirt":        (37.9333, 41.9500, "Siirt"),
        "Sinop":        (42.0231, 35.1531, "Sinop"),
        "Sivas":        (39.7477, 37.0179, "Sivas"),
        "Tekirdağ":     (40.9781, 27.5115, "Tekirdag"),
        "Tokat":        (40.3167, 36.5500, "Tokat"),
        "Trabzon":      (41.0015, 39.7178, "Trabzon"),
        "Tunceli":      (39.1079, 39.5480, "Tunceli"),
        "Şanlıurfa":    (37.1591, 38.7969, "Sanliurfa"),
        "Uşak":         (38.6823, 29.4082, "Usak"),
        "Van":          (38.4891, 43.4089, "Van"),
        "Yozgat":       (39.8181, 34.8147, "Yozgat"),
        "Zonguldak":    (41.4564, 31.7987, "Zonguldak"),
        "Aksaray":      (38.3687, 34.0370, "Aksaray"),
        "Bayburt":      (40.2552, 40.2249, "Bayburt"),
        "Karaman":      (37.1759, 33.2287, "Karaman"),
        "Kırıkkale":    (39.8468, 33.5153, "Kirikkale"),
        "Batman":       (37.8812, 41.1351, "Batman"),
        "Şırnak":       (37.5181, 42.4618, "Sirnak"),
        "Bartın":       (41.6344, 32.3375, "Bartin"),
        "Ardahan":      (41.1105, 42.7022, "Ardahan"),
        "Iğdır":        (39.9167, 44.0333, "Igdir"),
        "Yalova":       (40.6500, 29.2667, "Yalova"),
        "Karabük":      (41.2061, 32.6204, "Karabuk"),
        "Kilis":        (36.7184, 37.1212, "Kilis"),
        "Osmaniye":     (37.0749, 36.2464, "Osmaniye"),
        "Düzce":        (40.8438, 31.1565, "Duzce"),
    },
    "DE": {
        "Berlin":       (52.5200, 13.4050, "Berlin"),
        "Hamburg":      (53.5753, 10.0153, "Hamburg"),
        "Münih":        (48.1374, 11.5755, "Munich"),
        "Köln":         (50.9333, 6.9500, "Cologne"),
        "Frankfurt":    (50.1109, 8.6821, "Frankfurt"),
        "Stuttgart":    (48.7758, 9.1829, "Stuttgart"),
        "Düsseldorf":   (51.2217, 6.7762, "Dusseldorf"),
        "Dortmund":     (51.5136, 7.4653, "Dortmund"),
        "Essen":        (51.4508, 7.0131, "Essen"),
        "Leipzig":      (51.3397, 12.3731, "Leipzig"),
        "Bremen":       (53.0793, 8.8017, "Bremen"),
        "Dresden":      (51.0504, 13.7373, "Dresden"),
        "Hannover":     (52.3759, 9.7320, "Hanover"),
        "Nürnberg":     (49.4521, 11.0767, "Nuremberg"),
        "Duisburg":     (51.4344, 6.7623, "Duisburg"),
        "Bochum":       (51.4818, 7.2162, "Bochum"),
        "Wuppertal":    (51.2562, 7.1508, "Wuppertal"),
        "Bonn":         (50.7374, 7.0982, "Bonn"),
        "Mannheim":     (49.4878, 8.4660, "Mannheim"),
        "Karlsruhe":    (49.0069, 8.4037, "Karlsruhe"),
        "Augsburg":     (48.3717, 10.8983, "Augsburg"),
        "Münster":      (51.9607, 7.6261, "Munster"),
        "Bielefeld":    (52.0302, 8.5325, "Bielefeld"),
    },
    "FR": {
        "Paris":        (48.8566, 2.3522, "Paris"),
        "Marsilya":     (43.2965, 5.3698, "Marseille"),
        "Lyon":         (45.7640, 4.8357, "Lyon"),
        "Toulouse":     (43.6047, 1.4442, "Toulouse"),
        "Nice":         (43.7102, 7.2620, "Nice"),
        "Nantes":       (47.2184, -1.5536, "Nantes"),
        "Strasbourg":   (48.5734, 7.7521, "Strasbourg"),
        "Montpellier":  (43.6119, 3.8772, "Montpellier"),
        "Bordeaux":     (44.8378, -0.5792, "Bordeaux"),
        "Lille":        (50.6292, 3.0573, "Lille"),
        "Rennes":       (48.1173, -1.6778, "Rennes"),
        "Reims":        (49.2583, 4.0317, "Reims"),
        "Grenoble":     (45.1885, 5.7245, "Grenoble"),
    },
    "NL": {
        "Amsterdam":    (52.3676, 4.9041, "Amsterdam"),
        "Rotterdam":    (51.9244, 4.4777, "Rotterdam"),
        "Lahey":        (52.0705, 4.3007, "The Hague"),
        "Utrecht":      (52.0907, 5.1214, "Utrecht"),
        "Eindhoven":    (51.4416, 5.4697, "Eindhoven"),
        "Groningen":    (53.2194, 6.5665, "Groningen"),
        "Tilburg":      (51.5555, 5.0913, "Tilburg"),
        "Almere":       (52.3508, 5.2647, "Almere"),
        "Breda":        (51.5719, 4.7683, "Breda"),
        "Nijmegen":     (51.8426, 5.8546, "Nijmegen"),
    },
    "BE": {
        "Brüksel":      (50.8503, 4.3517, "Brussels"),
        "Antwerp":      (51.2194, 4.4025, "Antwerp"),
        "Gent":         (51.0543, 3.7174, "Ghent"),
        "Liège":        (50.6320, 5.5797, "Liege"),
        "Brugge":       (51.2093, 3.2247, "Bruges"),
        "Namur":        (50.4669, 4.8675, "Namur"),
        "Leuven":       (50.8798, 4.7005, "Leuven"),
        "Charleroi":    (50.4108, 4.4446, "Charleroi"),
    },
    "GB": {
        "Londra":       (51.5074, -0.1278, "London"),
        "Birmingham":   (52.4862, -1.8904, "Birmingham"),
        "Manchester":   (53.4808, -2.2426, "Manchester"),
        "Glasgow":      (55.8642, -4.2518, "Glasgow"),
        "Liverpool":    (53.4084, -2.9916, "Liverpool"),
        "Leeds":        (53.7997, -1.5492, "Leeds"),
        "Sheffield":    (53.3811, -1.4701, "Sheffield"),
        "Edinburgh":    (55.9533, -3.1883, "Edinburgh"),
        "Bristol":      (51.4545, -2.5879, "Bristol"),
        "Leicester":    (52.6369, -1.1398, "Leicester"),
        "Bradford":     (53.7960, -1.7594, "Bradford"),
        "Coventry":     (52.4068, -1.5197, "Coventry"),
        "Nottingham":   (52.9548, -1.1581, "Nottingham"),
        "Cardiff":      (51.4816, -3.1791, "Cardiff"),
    },
    "CH": {
        "Zürih":        (47.3769, 8.5417, "Zurich"),
        "Cenevre":      (46.2044, 6.1432, "Geneva"),
        "Basel":        (47.5596, 7.5886, "Basel"),
        "Bern":         (46.9481, 7.4474, "Bern"),
        "Lozan":        (46.5197, 6.6323, "Lausanne"),
        "Luzern":       (47.0502, 8.3093, "Lucerne"),
        "St.Gallen":    (47.4245, 9.3767, "St. Gallen"),
        "Lugano":       (46.0037, 8.9511, "Lugano"),
    },
    "AT": {
        "Viyana":       (48.2082, 16.3738, "Vienna"),
        "Graz":         (47.0707, 15.4395, "Graz"),
        "Linz":         (48.3069, 14.2858, "Linz"),
        "Salzburg":     (47.8095, 13.0550, "Salzburg"),
        "Innsbruck":    (47.2692, 11.4041, "Innsbruck"),
        "Klagenfurt":   (46.6228, 14.3050, "Klagenfurt"),
    },
    "SE": {
        "Stockholm":    (59.3293, 18.0686, "Stockholm"),
        "Göteborg":     (57.7089, 11.9746, "Gothenburg"),
        "Malmö":        (55.6050, 13.0038, "Malmo"),
        "Uppsala":      (59.8586, 17.6389, "Uppsala"),
        "Västerås":     (59.6162, 16.5528, "Vasteras"),
        "Örebro":       (59.2741, 15.2066, "Orebro"),
        "Linköping":    (58.4108, 15.6214, "Linkoping"),
        "Helsingborg":  (56.0465, 12.6945, "Helsingborg"),
    },
    "NO": {
        "Oslo":         (59.9139, 10.7522, "Oslo"),
        "Bergen":       (60.3913, 5.3221, "Bergen"),
        "Stavanger":    (58.9700, 5.7331, "Stavanger"),
        "Trondheim":    (63.4305, 10.3951, "Trondheim"),
        "Drammen":      (59.7440, 10.2045, "Drammen"),
        "Kristiansand": (58.1599, 8.0182, "Kristiansand"),
    },
    "DK": {
        "Kopenhag":     (55.6761, 12.5683, "Copenhagen"),
        "Aarhus":       (56.1629, 10.2039, "Aarhus"),
        "Odense":       (55.4038, 10.4024, "Odense"),
        "Aalborg":      (57.0480, 9.9187, "Aalborg"),
        "Esbjerg":      (55.4761, 8.4597, "Esbjerg"),
    },
    "US": {
        "New York":     (40.7128, -74.0060, "New York"),
        "Los Angeles":  (34.0522, -118.2437, "Los Angeles"),
        "Chicago":      (41.8781, -87.6298, "Chicago"),
        "Houston":      (29.7604, -95.3698, "Houston"),
        "Phoenix":      (33.4484, -112.0740, "Phoenix"),
        "Philadelphia": (39.9526, -75.1652, "Philadelphia"),
        "San Antonio":  (29.4241, -98.4936, "San Antonio"),
        "Dallas":       (32.7767, -96.7970, "Dallas"),
        "Detroit":      (42.3314, -83.0458, "Detroit"),
        "Seattle":      (47.6062, -122.3321, "Seattle"),
        "Denver":       (39.7392, -104.9903, "Denver"),
        "Boston":       (42.3601, -71.0589, "Boston"),
        "Nashville":    (36.1627, -86.7816, "Nashville"),
        "San Diego":    (32.7157, -117.1611, "San Diego"),
        "Washington":   (38.9072, -77.0369, "Washington DC"),
        "Miami":        (25.7617, -80.1918, "Miami"),
        "Atlanta":      (33.7490, -84.3880, "Atlanta"),
    },
    "CA": {
        "Toronto":      (43.6532, -79.3832, "Toronto"),
        "Montreal":     (45.5017, -73.5673, "Montreal"),
        "Vancouver":    (49.2827, -123.1207, "Vancouver"),
        "Calgary":      (51.0447, -114.0719, "Calgary"),
        "Edmonton":     (53.5461, -113.4938, "Edmonton"),
        "Ottawa":       (45.4215, -75.6972, "Ottawa"),
        "Winnipeg":     (49.8951, -97.1384, "Winnipeg"),
        "Quebec":       (46.8139, -71.2082, "Quebec City"),
        "Hamilton":     (43.2557, -79.8711, "Hamilton"),
    },
    "SA": {
        "Riyad":        (24.6877, 46.7219, "Riyadh"),
        "Cidde":        (21.4858, 39.1925, "Jeddah"),
        "Mekke":        (21.3891, 39.8579, "Mecca"),
        "Medine":       (24.5247, 39.5692, "Medina"),
        "Dammam":       (26.3927, 49.9777, "Dammam"),
        "Taif":         (21.2854, 40.4151, "Taif"),
        "Tabuk":        (28.3998, 36.5700, "Tabuk"),
        "Hail":         (27.5114, 41.6906, "Hail"),
        "Necran":       (17.5656, 44.2289, "Najran"),
    },
    "EG": {
        "Kahire":       (30.0444, 31.2357, "Cairo"),
        "İskenderiye":  (31.2001, 29.9187, "Alexandria"),
        "Giza":         (30.0131, 31.2089, "Giza"),
        "Aswan":        (24.0889, 32.8998, "Aswan"),
        "Luksor":       (25.6872, 32.6396, "Luxor"),
        "Port Said":    (31.2565, 32.2841, "Port Said"),
        "Süveyş":       (29.9737, 32.5311, "Suez"),
        "Mansura":      (31.0409, 31.3785, "Mansoura"),
        "Tanta":        (30.7865, 31.0004, "Tanta"),
    },
    "MA": {
        "Kazablanka":   (33.5731, -7.5898, "Casablanca"),
        "Fas":          (34.0181, -5.0078, "Fez"),
        "Marakeş":      (31.6295, -7.9811, "Marrakesh"),
        "Tanca":        (35.7595, -5.8340, "Tangier"),
        "Agadir":       (30.4278, -9.5981, "Agadir"),
        "Rabat":        (34.0209, -6.8416, "Rabat"),
        "Meknes":       (33.8731, -5.5407, "Meknes"),
        "Oujda":        (34.6814, -1.9086, "Oujda"),
    },
    "PK": {
        "Karaçi":       (24.8607, 67.0011, "Karachi"),
        "Lahor":        (31.5204, 74.3587, "Lahore"),
        "İslamabad":    (33.6844, 73.0479, "Islamabad"),
        "Rawalpindi":   (33.5651, 73.0169, "Rawalpindi"),
        "Faisalabad":   (31.4187, 73.0791, "Faisalabad"),
        "Multan":       (30.1798, 71.4214, "Multan"),
        "Peşaver":      (34.0151, 71.5249, "Peshawar"),
        "Quetta":       (30.1798, 66.9750, "Quetta"),
        "Haydarabad":   (25.3960, 68.3578, "Hyderabad"),
        "Gujranwala":   (32.1877, 74.1945, "Gujranwala"),
    },
    "ID": {
        "Cakarta":      (-6.2088, 106.8456, "Jakarta"),
        "Surabaya":     (-7.2575, 112.7521, "Surabaya"),
        "Bandung":      (-6.9175, 107.6191, "Bandung"),
        "Medan":        (3.5952, 98.6722, "Medan"),
        "Semarang":     (-6.9932, 110.4203, "Semarang"),
        "Makassar":     (-5.1477, 119.4327, "Makassar"),
        "Yogyakarta":   (-7.7956, 110.3695, "Yogyakarta"),
        "Palembang":    (-2.9761, 104.7754, "Palembang"),
        "Tangerang":    (-6.1781, 106.6297, "Tangerang"),
        "Depok":        (-6.4025, 106.7942, "Depok"),
    },
    "MY": {
        "Kuala Lumpur": (3.1390, 101.6869, "Kuala Lumpur"),
        "Johor Bahru":  (1.4927, 103.7414, "Johor Bahru"),
        "Penang":       (5.4141, 100.3288, "Penang"),
        "Kota Kinabalu":(5.9804, 116.0735, "Kota Kinabalu"),
        "Kuching":      (1.5533, 110.3592, "Kuching"),
        "Shah Alam":    (3.0733, 101.5185, "Shah Alam"),
        "Petaling Jaya":(3.1073, 101.6067, "Petaling Jaya"),
        "Ipoh":         (4.5975, 101.0901, "Ipoh"),
    },
    "AE": {
        "Dubai":        (25.2048, 55.2708, "Dubai"),
        "Abu Dabi":     (24.4539, 54.3773, "Abu Dhabi"),
        "Şarcah":       (25.3462, 55.4209, "Sharjah"),
        "Acman":        (25.4052, 55.5136, "Ajman"),
        "Ras el Hayme": (25.7895, 55.9432, "Ras Al Khaimah"),
        "Fujairah":     (25.1288, 56.3265, "Fujairah"),
    },
    "QA": {
        "Doha":         (25.2854, 51.5310, "Doha"),
        "Al Rayyan":    (25.2919, 51.4244, "Al Rayyan"),
        "Al Wakra":     (25.1656, 51.5977, "Al Wakra"),
    },
    "KW": {
        "Kuveyt":       (29.3759, 47.9774, "Kuwait City"),
        "Salmiya":      (29.3373, 48.0779, "Salmiya"),
        "Hawalli":      (29.3408, 48.0367, "Hawalli"),
    },
    "AZ": {
        "Bakü":         (40.4093, 49.8671, "Baku"),
        "Gence":        (40.6828, 46.3606, "Ganja"),
        "Sumqayıt":     (40.5894, 49.6653, "Sumgait"),
        "Naxçıvan":     (39.2092, 45.4114, "Nakhchivan"),
        "Mingəçevir":   (40.7600, 47.0592, "Mingachevir"),
    },
    "RU": {
        "Moskova":      (55.7558, 37.6176, "Moscow"),
        "Ufa":          (54.7388, 55.9721, "Ufa"),
        "Kazan":        (55.8304, 49.0661, "Kazan"),
        "Mahachkale":   (42.9849, 47.5047, "Makhachkala"),
        "Grozni":       (43.3178, 45.6985, "Grozny"),
        "St.Petersburg":(59.9311, 30.3609, "Saint Petersburg"),
        "Nazran":       (43.2255, 44.7685, "Nazran"),
        "Çerkessk":     (44.2272, 42.0586, "Cherkessk"),
    },
    "BA": {
        "Sarajevo":     (43.8563, 18.4131, "Sarajevo"),
        "Banja Luka":   (44.7722, 17.1910, "Banja Luka"),
        "Tuzla":        (44.5384, 18.6734, "Tuzla"),
        "Zenica":       (44.2010, 17.9078, "Zenica"),
        "Mostar":       (43.3438, 17.8078, "Mostar"),
    },
    "AL": {
        "Tiran":        (41.3275, 19.8187, "Tirana"),
        "Durrës":       (41.3246, 19.4565, "Durres"),
        "Vlorë":        (40.4662, 19.4825, "Vlore"),
        "Elbasan":      (41.1125, 20.0822, "Elbasan"),
        "Shkodër":      (42.0683, 19.5126, "Shkoder"),
    },
    "SG": {
        "Singapur":     (1.3521, 103.8198, "Singapore"),
    },
    "XK": {
        "Priştine":     (42.6629, 21.1655, "Pristina"),
        "Prizren":      (42.2139, 20.7420, "Prizren"),
        "Mitrovica":    (42.8914, 20.8659, "Mitrovica"),
        "Peja":         (42.6597, 20.2883, "Peja"),
    },
    "DZ": {
        "Cezayir":      (36.7372, 3.0865, "Algiers"),
        "Oran":         (35.6969, -0.6331, "Oran"),
        "Konstantin":   (36.3650, 6.6147, "Constantine"),
        "Annaba":       (36.9000, 7.7667, "Annaba"),
        "Batna":        (35.5553, 6.1742, "Batna"),
    },
    "TN": {
        "Tunus":        (36.8190, 10.1658, "Tunis"),
        "Sfaks":        (34.7406, 10.7603, "Sfax"),
        "Sousse":       (35.8245, 10.6346, "Sousse"),
        "Gabès":        (33.8814, 10.0982, "Gabes"),
    },
    "LY": {
        "Trablus":      (32.9012, 13.1800, "Tripoli"),
        "Bingazi":      (32.1167, 20.0667, "Benghazi"),
        "Misrata":      (32.3754, 15.0925, "Misrata"),
    },
    "SD": {
        "Hartum":       (15.5007, 32.5599, "Khartoum"),
        "Omdurman":     (15.6333, 32.4833, "Omdurman"),
        "Port Sudan":   (19.6161, 37.2164, "Port Sudan"),
    },
    "IQ": {
        "Bağdat":       (33.3406, 44.4009, "Baghdad"),
        "Basra":        (30.5081, 47.7835, "Basra"),
        "Musul":        (36.3450, 43.1450, "Mosul"),
        "Erbil":        (36.1901, 44.0091, "Erbil"),
        "Kerkük":       (35.4681, 44.3922, "Kirkuk"),
        "Necef":        (32.0025, 44.3351, "Najaf"),
        "Kerbela":      (32.6157, 44.0247, "Karbala"),
    },
    "SY": {
        "Şam":          (33.5102, 36.2913, "Damascus"),
        "Halep":        (36.2021, 37.1343, "Aleppo"),
        "Hama":         (35.1333, 36.7500, "Hama"),
        "Humus":        (34.7338, 36.7213, "Homs"),
        "Lazkiye":      (35.5317, 35.7914, "Latakia"),
    },
    "JO": {
        "Amman":        (31.9554, 35.9454, "Amman"),
        "Zerka":        (32.0553, 36.0881, "Zarqa"),
        "İrbid":        (32.5556, 35.8500, "Irbid"),
        "Akabe":        (29.5321, 35.0063, "Aqaba"),
    },
    "LB": {
        "Beyrut":       (33.8938, 35.5018, "Beirut"),
        "Trablus":      (34.4367, 35.8497, "Tripoli"),
        "Sayda":        (33.5611, 35.3703, "Sidon"),
        "Sur":          (33.2705, 35.1964, "Tyre"),
    },
    "YE": {
        "Sana":         (15.3694, 44.1910, "Sanaa"),
        "Aden":         (12.7797, 45.0367, "Aden"),
        "Taiz":         (13.5789, 44.0209, "Taiz"),
        "Hudeyde":      (14.7978, 42.9550, "Hudaydah"),
    },
    "AF": {
        "Kabil":        (34.5553, 69.2075, "Kabul"),
        "Kandahar":     (31.6289, 65.7372, "Kandahar"),
        "Herat":        (34.3482, 62.1997, "Herat"),
        "Mezar-ı Şerif":(36.7069, 67.1100, "Mazar-i-Sharif"),
        "Celalabad":    (34.4301, 70.4388, "Jalalabad"),
    },
    "BD": {
        "Dakka":        (23.8103, 90.4125, "Dhaka"),
        "Chittagong":   (22.3569, 91.7832, "Chittagong"),
        "Khulna":       (22.8456, 89.5403, "Khulna"),
        "Rajshahi":     (24.3745, 88.6042, "Rajshahi"),
        "Sylhet":       (24.8996, 91.8720, "Sylhet"),
    },
    "KZ": {
        "Almatı":       (43.2220, 76.8512, "Almaty"),
        "Nur-Sultan":   (51.1801, 71.4460, "Astana"),
        "Şımkent":      (42.3000, 69.6000, "Shymkent"),
        "Aktobe":       (50.2839, 57.1670, "Aktobe"),
    },
    "UZ": {
        "Taşkent":      (41.2995, 69.2401, "Tashkent"),
        "Semerkant":    (39.6547, 66.9758, "Samarkand"),
        "Buhara":       (39.7747, 64.4286, "Bukhara"),
        "Namangan":     (41.0011, 71.6723, "Namangan"),
        "Andican":      (40.7821, 72.3443, "Andijan"),
        "Fergana":      (40.3864, 71.7864, "Fergana"),
    },
    "IR": {
        "Tahran":       (35.6892, 51.3890, "Tehran"),
        "Meşhed":       (36.2605, 59.6168, "Mashhad"),
        "İsfahan":      (32.6539, 51.6660, "Isfahan"),
        "Tebriz":       (38.0800, 46.2919, "Tabriz"),
        "Şiraz":        (29.5918, 52.5837, "Shiraz"),
        "Ahvaz":        (31.3203, 48.6692, "Ahvaz"),
        "Kum":          (34.6415, 50.8751, "Qom"),
    },
    "OM": {
        "Maskat":       (23.5880, 58.3829, "Muscat"),
        "Salalah":      (17.0151, 54.0924, "Salalah"),
        "Sohar":        (24.3467, 56.7480, "Sohar"),
        "Nizwa":        (22.9333, 57.5333, "Nizwa"),
    },
    "BH": {
        "Manama":       (26.2154, 50.5832, "Manama"),
        "Muharraq":     (26.2566, 50.6108, "Muharraq"),
        "Riffa":        (26.1296, 50.5554, "Riffa"),
    },
    "NG": {
        "Lagos":        (6.5244, 3.3792, "Lagos"),
        "Kano":         (12.0022, 8.5920, "Kano"),
        "Abuja":        (9.0765, 7.3986, "Abuja"),
        "Kaduna":       (10.5222, 7.4383, "Kaduna"),
        "Zaria":        (11.0851, 7.7199, "Zaria"),
        "Sokoto":       (13.0059, 5.2476, "Sokoto"),
    },
    "SN": {
        "Dakar":        (14.7167, -17.4677, "Dakar"),
        "Thiès":        (14.7833, -16.9167, "Thies"),
        "Kaolack":      (14.1500, -16.0667, "Kaolack"),
        "Touba":        (14.8500, -15.8833, "Touba"),
    },
    "PS": {
        "Gazze":        (31.5017, 34.4674, "Gaza"),
        "Ramallah":     (31.9038, 35.2034, "Ramallah"),
        "Nablus":       (32.2211, 35.2544, "Nablus"),
        "Hebron":       (31.5326, 35.0998, "Hebron"),
        "Jenin":        (32.4608, 35.2964, "Jenin"),
        "Kudüs":        (31.7683, 35.2137, "Jerusalem"),
    },
    "MV": {
        "Malé":         (4.1755, 73.5093, "Male"),
        "Addu":         (-0.6297, 73.1572, "Addu City"),
    },
    "MK": {
        "Üsküp":        (41.9965, 21.4314, "Skopje"),
        "Bitola":       (41.0297, 21.3294, "Bitola"),
        "Tetovo":       (41.9896, 20.9745, "Tetovo"),
        "Gostivar":     (41.7986, 20.9089, "Gostivar"),
    },
    "KG": {
        "Bişkek":       (42.8746, 74.5698, "Bishkek"),
        "Oş":           (40.5283, 72.7985, "Osh"),
        "Celal-Abad":   (40.9333, 72.9833, "Jalal-Abad"),
    },
    "TJ": {
        "Duşanbe":      (38.5598, 68.7733, "Dushanbe"),
        "Hocend":       (40.2833, 69.6167, "Khujand"),
        "Kulob":        (37.9167, 69.7833, "Kulob"),
    },
}

# ═══════════════════════════════════════════════
#  İLÇE VERİSİ
# ═══════════════════════════════════════════════
# ═══════════════════════════════════════════════
#  TÜRKİYE 81 İL İLÇE VERİSİ
# ═══════════════════════════════════════════════
ISTANBUL_ILCE = {
    "Adalar":(40.8760,29.0862),"Arnavutköy":(41.1867,28.7390),"Ataşehir":(40.9925,29.1244),
    "Avcılar":(40.9793,28.7225),"Bağcılar":(41.0366,28.8561),"Bahçelievler":(40.9998,28.8617),
    "Bakırköy":(40.9793,28.8702),"Başakşehir":(41.0925,28.8019),"Bayrampaşa":(41.0435,28.9098),
    "Beşiktaş":(41.0422,29.0077),"Beykoz":(41.1280,29.1101),"Beylikdüzü":(40.9810,28.6437),
    "Beyoğlu":(41.0317,28.9762),"Büyükçekmece":(41.0212,28.5841),"Çatalca":(41.1432,28.4617),
    "Çekmeköy":(41.0347,29.1919),"Esenler":(41.0453,28.8779),"Esenyurt":(41.0290,28.6721),
    "Eyüpsultan":(41.0577,28.9335),"Fatih":(41.0186,28.9397),"Gaziosmanpaşa":(41.0683,28.9119),
    "Güngören":(41.0198,28.8776),"Kadıköy":(40.9813,29.0759),"Kağıthane":(41.0791,28.9704),
    "Kartal":(40.9063,29.1879),"Küçükçekmece":(41.0010,28.7832),"Maltepe":(40.9355,29.1308),
    "Pendik":(40.8765,29.2350),"Sancaktepe":(41.0003,29.2312),"Sarıyer":(41.1682,29.0578),
    "Silivri":(41.0730,28.2468),"Sultanbeyli":(40.9649,29.2646),"Sultangazi":(41.1040,28.8674),
    "Şile":(41.1770,29.6121),"Şişli":(41.0602,28.9877),"Tuzla":(40.8162,29.2965),
    "Ümraniye":(41.0165,29.1233),"Üsküdar":(41.0214,29.0161),"Zeytinburnu":(40.9944,28.9008),
}
ANKARA_ILCE = {
    "Akyurt":(40.1357,33.0856),"Altındağ":(39.9461,32.8810),"Ayaş":(40.0186,32.3358),
    "Bala":(39.5588,33.1207),"Beypazarı":(40.1683,31.9218),"Çankaya":(39.9179,32.8626),
    "Çubuk":(40.2373,33.0344),"Etimesgut":(39.9540,32.6760),"Gölbaşı":(39.7898,32.8126),
    "Haymana":(39.4323,32.4960),"Keçiören":(39.9970,32.8677),"Mamak":(39.9338,32.9261),
    "Nallıhan":(40.1863,31.3525),"Polatlı":(39.5831,32.1440),"Pursaklar":(40.0359,32.9000),
    "Sincan":(39.9716,32.5819),"Yenimahalle":(39.9693,32.7851),
}
IZMIR_ILCE = {
    "Aliağa":(38.7993,26.9747),"Balçova":(38.3876,27.0726),"Bayındır":(38.2184,27.6477),
    "Bayraklı":(38.4622,27.1476),"Bergama":(39.1211,27.1790),"Bornova":(38.4629,27.2162),
    "Buca":(38.3838,27.1696),"Çeşme":(38.3241,26.3047),"Çiğli":(38.4938,27.0736),
    "Dikili":(39.0718,26.8893),"Gaziemir":(38.3188,27.1330),"Karabağlar":(38.3703,27.1218),
    "Karşıyaka":(38.4627,27.1180),"Kemalpaşa":(38.4217,27.4130),"Konak":(38.4127,27.1397),
    "Menderes":(38.2553,27.1326),"Menemen":(38.6080,27.0617),"Narlıdere":(38.3927,26.9986),
    "Ödemiş":(38.2259,28.0027),"Seferihisar":(38.1977,26.8424),"Selçuk":(37.9514,27.3680),
    "Tire":(38.0908,27.7362),"Torbalı":(38.1624,27.3592),"Urla":(38.3221,26.7661),
}
BURSA_ILCE = {
    "Büyükorhan":(39.7614,28.8928),"Gemlik":(40.4313,29.1527),"Gürsu":(40.2206,29.1830),
    "İnegöl":(40.0762,29.5102),"İznik":(40.4286,29.7198),"Karacabey":(40.2168,28.3471),
    "Kestel":(40.1952,29.2233),"Mudanya":(40.3751,28.8843),"Nilüfer":(40.2127,28.9803),
    "Osmangazi":(40.1922,29.0481),"Yenişehir":(40.2609,29.6384),"Yıldırım":(40.1831,29.1011),
}
ANTALYA_ILCE = {
    "Akseki":(37.0497,31.7878),"Aksu":(36.9945,30.8706),"Alanya":(36.5444,32.0019),
    "Demre":(36.2454,29.9838),"Elmalı":(36.7364,29.9156),"Finike":(36.3001,30.1529),
    "Gazipaşa":(36.2702,32.3139),"Kaş":(36.2022,29.6389),"Kemer":(36.5962,30.5553),
    "Kepez":(37.0060,30.7197),"Konyaaltı":(36.8832,30.6419),"Korkuteli":(37.0635,30.1886),
    "Kumluca":(36.3693,30.2911),"Manavgat":(36.7862,31.4335),"Muratpaşa":(36.8969,30.7133),
    "Serik":(36.9204,31.1006),
}
KONYA_ILCE = {
    "Akşehir":(38.3500,31.4167),"Beyşehir":(37.6736,31.7225),"Çumra":(37.5714,32.7725),
    "Ereğli":(37.5181,34.0553),"Ilgın":(38.2872,31.9175),"Karatay":(37.8783,32.5078),
    "Meram":(37.8336,32.4311),"Selçuklu":(37.9375,32.5161),"Seydişehir":(37.4186,31.8483),
}
GAZIANTEP_ILCE = {
    "İslahiye":(37.0236,36.6339),"Nizip":(37.0114,37.7939),"Oğuzeli":(36.9583,37.5083),
    "Şahinbey":(37.0662,37.3833),"Şehitkamil":(37.1014,37.3697),"Nurdağı":(37.1764,36.7375),
}
ADANA_ILCE = {
    "Ceyhan":(37.0272,35.8131),"Çukurova":(36.9878,35.2564),"Kozan":(37.4539,35.8125),
    "Sarıçam":(37.0428,35.3906),"Seyhan":(36.9914,35.3278),"Yüreğir":(37.0108,35.4219),
}
KAYSERI_ILCE = {
    "Bünyan":(38.8517,35.8597),"Develi":(38.3781,35.4925),"Hacılar":(38.6553,35.4928),
    "Kocasinan":(38.7500,35.4786),"Melikgazi":(38.7264,35.4328),"Talas":(38.6933,35.5483),
}
# YENİ: 81 ilin tamamı
ADIYAMAN_ILCE = {
    "Besni":(37.6906,37.8597),"Çelikhan":(38.0147,38.2286),"Gerger":(37.9569,38.9853),
    "Gölbaşı":(37.7883,37.6466),"Kahta":(37.7817,38.6156),"Merkez":(37.7648,38.2786),
    "Samsat":(37.5947,38.4797),"Sincik":(38.0267,38.6236),"Tut":(37.9286,37.9136),
}
AFYON_ILCE = {
    "Bolvadin":(38.7122,31.0589),"Çay":(38.5931,30.7900),"Dinar":(38.0681,30.1650),
    "Emirdağ":(39.0156,31.1531),"İhsaniye":(38.9572,30.5461),"Merkez":(38.7507,30.5567),
    "Sandıklı":(38.4667,30.2625),"Sincanlı":(38.6094,30.7714),"Şuhut":(38.5364,30.5467),
}
AGRI_ILCE = {
    "Diyadin":(39.5469,43.6706),"Doğubeyazıt":(39.5466,44.0819),"Eleşkirt":(39.8025,42.6714),
    "Hamur":(39.5906,43.0428),"Merkez":(39.7191,43.0503),"Patnos":(39.2333,42.8667),
    "Taşlıçay":(39.6164,43.3703),"Tutak":(39.5397,42.7825),
}
AMASYA_ILCE = {
    "Göynücek":(40.3983,35.5117),"Gümüşhacıköy":(40.8722,35.2022),"Hamamözü":(40.7058,35.5311),
    "Merkez":(40.6499,35.8353),"Merzifon":(40.8783,35.4619),"Suluova":(40.8503,35.6556),
    "Taşova":(40.7739,36.3261),
}
ARTVIN_ILCE = {
    "Ardanuç":(41.1100,42.0611),"Arhavi":(41.3617,41.2950),"Borçka":(41.3681,41.6906),
    "Hopa":(41.4108,41.4225),"Merkez":(41.1828,41.8183),"Murgul":(41.1794,41.4914),
    "Şavşat":(41.2497,42.3669),"Yusufeli":(40.8239,41.5189),
}
AYDIN_ILCE = {
    "Bozdoğan":(37.6756,28.3094),"Buharkent":(37.9681,28.7419),"Çine":(37.6108,28.0606),
    "Didim":(37.3792,27.2669),"Efeler":(37.8444,27.8458),"Germencik":(37.8683,27.6069),
    "İncirliova":(37.8567,27.7269),"Karacasu":(37.7242,28.6022),"Karpuzlu":(37.5503,27.8514),
    "Koçarlı":(37.7567,27.6939),"Kuşadası":(37.8564,27.2609),"Kuyucak":(37.9203,28.4731),
    "Nazilli":(37.9122,28.3233),"Söke":(37.7497,27.4131),"Sultanhisar":(37.8878,28.1539),
    "Yenipazar":(37.8272,28.1928),
}
BALIKESIR_ILCE = {
    "Altıeylül":(39.6484,27.8826),"Ayvalık":(39.3186,26.6953),"Bandırma":(40.3506,27.9772),
    "Bigadiç":(39.3928,28.1261),"Burhaniye":(39.4981,26.9811),"Dursunbey":(39.5817,28.6247),
    "Edremit":(39.5953,27.0233),"Erdek":(40.3944,27.7967),"Gömeç":(39.4419,26.8364),
    "Gönen":(40.0989,27.6506),"Havran":(39.5578,27.0919),"İvrindi":(39.5447,27.4878),
    "Karesi":(39.6484,27.8826),"Kepsut":(39.6850,28.1511),"Manyas":(40.0417,27.9769),
    "Marmara":(40.6072,27.5881),"Savaştepe":(39.3831,28.0556),"Sındırgı":(39.2336,28.1861),
    "Susurluk":(40.1736,28.1561),
}
BILECIK_ILCE = {
    "Bozüyük":(39.9089,30.0394),"Gölpazarı":(40.2756,30.3253),"İnhisar":(40.0153,29.8611),
    "Merkez":(40.1506,29.9792),"Osmaneli":(40.3544,30.0164),"Pazaryeri":(39.9869,29.9097),
    "Söğüt":(40.0208,30.1817),"Yenipazar":(40.0669,30.0967),
}
BINGOL_ILCE = {
    "Adaklı":(38.9044,40.5583),"Genç":(38.7400,40.5575),"Karlıova":(39.2961,41.0078),
    "Kiğı":(39.3272,40.3600),"Merkez":(38.8855,40.4949),"Solhan":(38.9522,40.7397),
    "Yayladere":(38.9717,40.2483),"Yedisu":(39.3014,40.6508),
}
BITLIS_ILCE = {
    "Adilcevaz":(38.7994,42.7317),"Ahlat":(38.7528,42.4778),"Güroymak":(38.5789,42.0161),
    "Hizan":(38.2272,42.4164),"Merkez":(38.4006,42.1095),"Mutki":(38.4250,41.9019),
    "Tatvan":(38.5075,42.2786),
}
BOLU_ILCE = {
    "Dörtdivan":(40.7347,31.2317),"Gerede":(40.7944,32.1856),"Göynük":(40.3972,30.7642),
    "Kıbrıscık":(40.4847,31.9292),"Mengen":(41.0019,32.2275),"Merkez":(40.7359,31.6061),
    "Mudurnu":(40.4622,31.2092),"Seben":(40.3750,31.5792),"Yeniçağa":(40.7539,32.0036),
}
BURDUR_ILCE = {
    "Ağlasun":(37.6528,30.5303),"Altınyayla":(37.5289,30.0150),"Bucak":(37.4594,30.5933),
    "Çavdır":(37.1561,29.7394),"Çeltikçi":(37.5181,30.3681),"Gölhisar":(37.1258,29.5131),
    "Karamanlı":(37.3878,30.0036),"Kemer":(37.3333,30.0500),"Merkez":(37.7203,30.2904),
    "Tefenni":(37.3133,29.7692),"Yeşilova":(37.5111,29.7606),
}
CANAKKALE_ILCE = {
    "Ayvacık":(39.5975,26.4053),"Bayramiç":(39.8108,26.6183),"Biga":(40.2261,27.2467),
    "Bozcaada":(39.8314,26.0547),"Çan":(40.0264,27.0592),"Eceabat":(40.1806,26.3594),
    "Ezine":(39.7928,26.3297),"Gelibolu":(40.4039,26.6744),"Gökçeada":(40.1908,25.8808),
    "Lapseki":(40.3556,26.6906),"Merkez":(40.1553,26.4142),"Yenice":(39.9175,27.2672),
}
CANKIRI_ILCE = {
    "Atkaracalar":(41.0622,33.2019),"Bayramören":(41.0775,33.5653),"Çerkeş":(40.8183,32.8925),
    "Eldivan":(40.4783,33.5217),"Ilgaz":(40.9158,33.6200),"Khanköy":(40.5406,33.0297),
    "Korgun":(40.8028,33.5217),"Kurşunlu":(40.8508,33.2611),"Merkez":(40.6013,33.6134),
    "Orta":(40.5208,33.2386),"Şabanözü":(40.7233,33.5361),"Yapraklı":(40.7500,33.7803),
}
CORUM_ILCE = {
    "Alaca":(40.1700,34.8531),"Bayat":(40.6467,34.0706),"Boğazkale":(40.0258,34.6200),
    "Dodurga":(40.8897,34.4172),"İskilip":(40.7428,34.4728),"Kargı":(41.1328,34.8136),
    "Laçin":(41.0386,34.9261),"Mecitözü":(40.5206,35.2786),"Merkez":(40.5506,34.9556),
    "Oğuzlar":(40.5856,34.3697),"Ortaköy":(40.2756,35.2450),"Osmancık":(40.9711,34.8131),
    "Sungurlu":(40.1697,34.3658),"Uğurludağ":(40.4467,35.0939),
}
DENIZLI_ILCE = {
    "Acıpayam":(37.4297,29.3569),"Babadağ":(37.8097,28.8700),"Bekilli":(38.1553,29.4650),
    "Bozkurt":(37.8494,29.6294),"Buldan":(38.0494,28.8336),"Çal":(38.0958,29.3883),"Çameli":(37.0761,29.5336),
    "Çardak":(37.8253,30.1558),"Çivril":(38.2992,29.7333),"Güney":(37.9244,29.2069),
    "Honaz":(37.7522,29.2786),"Kale":(37.4439,28.8131),"Merkezefendi":(37.7765,29.0864),
    "Pamukkale":(37.9167,29.1167),"Sarayköy":(37.9167,28.9167),"Serinhisar":(37.5931,29.2656),
    "Tavas":(37.5722,28.9983),
}
DIYARBAKIR_ILCE = {
    "Bağlar":(37.9050,40.2000),"Bismil":(37.8589,40.6561),"Çermik":(37.9994,39.4783),
    "Çınar":(37.7206,40.4028),"Çüngüş":(38.2244,39.2806),"Dicle":(38.3625,40.0703),
    "Eğil":(38.2586,40.0814),"Ergani":(38.2681,39.7525),"Hani":(38.4025,40.4053),
    "Hazro":(38.2528,40.7883),"Kayapınar":(37.9144,40.2306),"Kocaköy":(38.1869,40.0536),
    "Kulp":(38.5117,41.0064),"Lice":(38.4639,40.6536),"Silvan":(38.1353,41.0008),
    "Sur":(37.9100,40.2153),"Yenişehir":(37.9203,40.2483),
}
EDIRNE_ILCE = {
    "Edirne":(41.6818,26.5623),"Enez":(40.7317,26.4944),"Havsa":(41.5497,26.8247),
    "İpsala":(40.9161,26.3872),"Keşan":(40.8600,26.6347),"Lalapaşa":(41.8244,26.7294),
    "Meriç":(41.1906,26.4100),"Süloğlu":(41.7831,26.9153),"Uzunköprü":(41.2667,26.6917),
}
ELAZIG_ILCE = {
    "Ağın":(38.9486,38.7192),"Alacakaya":(38.5306,39.8036),"Arıcak":(38.5928,40.0536),
    "Baskil":(38.5706,38.8278),"Karakoçan":(38.9542,40.0411),"Keban":(38.7961,38.7561),
    "Kovancılar":(38.7183,40.2931),"Maden":(38.3944,39.6689),"Merkez":(38.6810,39.2264),
    "Palu":(38.6906,40.0631),"Sivrice":(38.4481,39.3194),
}
ERZINCAN_ILCE = {
    "Çayırlı":(39.8000,40.0333),"İliç":(39.4556,38.5597),"Kemah":(39.5869,38.4947),
    "Kemaliye":(39.2664,38.4914),"Merkez":(39.7500,39.5000),"Otlukbeli":(39.5619,40.2869),
    "Refahiye":(39.9042,38.7728),"Tercan":(39.7872,40.3903),"Üzümlü":(39.7017,39.2783),
}
ERZURUM_ILCE = {
    "Aşkale":(39.9167,40.6833),"Aziziye":(39.9100,41.2653),"Çat":(39.6394,41.0381),
    "Hınıs":(39.3681,41.6956),"Horasan":(40.0444,42.1667),"İspir":(40.4906,40.9919),
    "Karaçoban":(39.9664,41.7000),"Karayazı":(39.6908,42.1553),"Köprüköy":(39.9744,41.5358),
    "Merkez":(39.9055,41.2658),"Narman":(40.3408,41.8700),"Oltu":(40.5486,41.9956),
    "Olur":(40.8458,42.1292),"Palandöken":(39.8900,41.2500),"Pazaryolu":(40.3261,40.9192),
    "Şenkaya":(40.5594,42.3525),"Tekman":(39.6272,41.5069),"Tortum":(40.3067,41.5483),
    "Uzundere":(40.2533,41.5631),"Yakutiye":(39.9200,41.2800),
}
ESKISEHIR_ILCE = {
    "Alpu":(39.7406,31.0358),"Beylikova":(39.9164,31.4014),"Çifteler":(39.3700,31.0250),
    "Günyüzü":(38.9694,31.7236),"Han":(39.6361,30.5997),"İnönü":(39.8225,30.1600),
    "Mahmudiye":(39.5347,31.2822),"Mihalgazi":(40.1658,30.5819),"Mihalıççık":(39.8636,31.5400),
    "Odunpazarı":(39.7800,30.5100),"Sarıcakaya":(40.0319,30.6553),"Seyitgazi":(39.4431,30.6961),
    "Sivrihisar":(39.4508,31.5358),"Tepebaşı":(39.8000,30.5200),
}
GIRESUN_ILCE = {
    "Alucra":(40.3483,38.7814),"Bulancak":(40.9389,38.2261),"Çamoluk":(40.0539,38.5061),
    "Çanakçı":(41.1681,38.9219),"Dereli":(40.6808,38.4025),"Doğankent":(40.7264,38.0994),
    "Espiye":(40.9450,38.7153),"Eynesil":(41.0428,38.9736),"Görele":(41.0300,39.2917),
    "Güce":(40.8800,38.4236),"Keşap":(40.9406,38.5303),"Merkez":(40.9128,38.3895),
    "Piraziz":(40.9592,38.1683),"Şebinkarahisar":(40.2883,38.4278),"Tirebolu":(41.0014,38.8153),
    "Yağlıdere":(40.8683,38.2706),
}
HAKKARI_ILCE = {
    "Çukurca":(37.2519,43.6128),"Derecik":(37.3736,43.4936),"Merkez":(37.5744,43.7408),
    "Şemdinli":(37.3028,44.5722),"Yüksekova":(37.5736,44.2836),
}
HATAY_ILCE = {
    "Altınözü":(36.0703,36.2336),"Antakya":(36.2021,36.1606),"Arsuz":(36.4128,36.0211),
    "Belen":(36.4894,36.4919),"Dörtyol":(36.8425,36.2361),"Erzin":(36.9517,36.1978),
    "Hassa":(36.7928,36.5036),"İskenderun":(36.5860,36.1658),"Kırıkhan":(36.4944,36.3622),
    "Kumlu":(36.3619,36.4572),"Payas":(36.7183,36.2358),"Reyhanlı":(36.2681,36.5569),
    "Samandağ":(36.0714,35.9819),"Yayladağı":(35.9064,36.0536),
}
ISPARTA_ILCE = {
    "Aksu":(37.9042,30.7994),"Atabey":(37.9606,30.3928),"Eğirdir":(37.8806,30.8444),
    "Gelendost":(37.9919,31.0192),"Gönen":(38.1308,30.5025),"Keçiborlu":(37.9583,30.2906),
    "Merkez":(37.7648,30.5566),"Senirkent":(38.1008,30.5494),"Sütçüler":(37.4947,31.0206),
    "Şarkikaraağaç":(38.0411,31.3717),"Uluborlu":(38.0947,30.4367),"Yalvaç":(38.2953,31.1700),
    "Yenişarbademli":(37.6578,31.0531),
}
KAHRAMANMARAS_ILCE = {
    "Afşin":(38.2472,36.9158),"Andırın":(37.5728,36.3561),"Çağlayancerit":(37.7231,36.6456),
    "Dulkadiroğlu":(37.5858,36.9371),"Ekinözü":(37.7131,37.1553),"Elbistan":(38.2058,37.1942),
    "Göksun":(38.0231,36.4947),"Nurhak":(37.9669,37.2981),"Onikişubat":(37.5700,36.9500),
    "Pazarcık":(37.4917,37.2878),"Türkoğlu":(37.3819,36.8594),
}
KARABUK_ILCE = {
    "Eflani":(41.4161,32.9514),"Eskipazar":(41.0150,32.9031),"Merkez":(41.2061,32.6204),
    "Ovacık":(41.4506,32.8203),"Safranbolu":(41.2528,32.6897),"Yenice":(41.2003,32.3361),
}
KARAMAN_ILCE = {
    "Ayrancı":(37.3567,33.6858),"Başyayla":(36.9014,33.4881),"Ermenek":(36.6378,32.8992),
    "Kazımkarabekir":(37.2439,33.6853),"Merkez":(37.1759,33.2287),"Sarıveliler":(36.7358,33.1631),
}
KARS_ILCE = {
    "Akyaka":(40.6083,42.7394),"Arpaçay":(40.8297,43.3344),"Digor":(40.3764,43.4094),
    "Kağızman":(40.1425,43.1208),"Merkez":(40.6013,43.0975),"Sarıkamış":(40.3256,42.5869),
    "Selim":(40.4683,42.8036),"Susuz":(40.6736,43.1414),
}
KASTAMONU_ILCE = {
    "Abana":(41.9714,34.0139),"Ağlı":(41.7139,33.9583),"Araç":(41.2428,33.3272),"Azdavay":(41.6664,33.3081),
    "Bozkurt":(41.9514,34.0197),"Çatalzeytin":(41.9097,34.2278),"Cide":(41.8892,33.0144),
    "Daday":(41.4678,33.4639),"Devrekani":(41.5786,33.8444),"Doğanyurt":(41.8939,34.1217),
    "Hanönü":(41.6572,33.7381),"İhsangazi":(41.3886,33.6297),"İnebolu":(41.9739,33.7636),
    "Küre":(41.8297,33.7153),"Merkez":(41.3887,33.7827),"Pınarbaşı":(41.6058,33.9078),
    "Seydiler":(41.3731,34.2064),"Şenpazar":(41.6825,34.0717),"Taşköprü":(41.5144,34.2158),
    "Tosya":(41.0119,34.0408),
}
KIRKLARELI_ILCE = {
    "Babaeski":(41.4336,27.0961),"Demirköy":(41.8261,27.7697),"Kofçaz":(41.9600,27.8467),
    "Lüleburgaz":(41.3997,27.3567),"Merkez":(41.7333,27.2167),"Pehlivanköy":(41.3675,26.9131),
    "Pınarhisar":(41.6236,27.5283),"Vize":(41.5728,27.7608),
}
KIRSEHIR_ILCE = {
    "Akçakent":(39.2753,34.5006),"Akpınar":(39.5578,34.3333),"Boztepe":(39.1703,34.5736),
    "Çiçekdağı":(39.6022,34.3903),"Kaman":(39.3597,33.7289),"Merkez":(39.1425,34.1709),
    "Mucur":(39.0636,34.3833),
}
KILIS_ILCE = {
    "Elbeyli":(36.7794,37.3467),"Merkez":(36.7184,37.1212),"Musabeyli":(36.9503,37.4436),"Polateli":(36.9656,36.8692),
}
KOCAELI_ILCE = {
    "Başiskele":(40.7200,29.9503),"Çayırova":(40.7886,29.4011),"Darıca":(40.7694,29.3742),
    "Derince":(40.7500,29.8167),"Dilovası":(40.7333,29.5500),"Gebze":(40.8028,29.4311),
    "Gölcük":(40.7136,29.8228),"İzmit":(40.7667,29.9167),"Kandıra":(41.0736,30.1439),
    "Karamürsel":(40.6919,29.6139),"Kartepe":(40.7667,30.0667),"Körfez":(40.7500,29.7833),
}
KUTAHYA_ILCE = {
    "Altıntaş":(39.0683,30.1172),"Aslanapa":(39.2394,29.8608),"Çavdarhisar":(39.1981,29.6019),
    "Domaniç":(39.8017,29.5694),"Dumlupınar":(39.0364,29.8361),"Emet":(39.3397,29.2581),
    "Gediz":(39.0447,29.4083),"Hisarcık":(39.2567,29.2097),"Merkez":(39.4167,29.9833),
    "Pazarlar":(39.2236,28.9919),"Şaphane":(39.0208,29.2303),"Simav":(39.0897,28.9794),"Tavşanlı":(39.5481,29.4906),
}
MALATYA_ILCE = {
    "Akçadağ":(38.3397,37.9558),"Arapgir":(38.9106,38.4983),"Arguvan":(38.7364,38.6822),
    "Battalgazi":(38.4000,38.3500),"Darende":(38.5681,37.5097),"Doğanşehir":(38.0961,37.8817),
    "Doğanyol":(38.3936,38.1153),"Hekimhan":(38.8236,37.9397),"Kale":(38.2461,38.1094),
    "Kuluncak":(38.6742,37.6478),"Merkez":(38.3552,38.3095),"Pütürge":(38.2078,38.9022),
    "Yazıhan":(38.5356,38.2158),"Yeşilyurt":(38.3400,38.3100),
}
MANISA_ILCE = {
    "Ahmetli":(38.5281,27.9347),"Akhisar":(38.9181,27.8361),"Alaşehir":(38.3503,28.5164),
    "Demirci":(38.9981,28.6603),"Gölmarmara":(38.7142,27.9161),"Gördes":(38.9275,28.2933),
    "Kırkağaç":(39.0958,27.6703),"Köprübaşı":(38.7383,28.4069),"Kula":(38.5500,28.6503),
    "Merkez":(38.6191,27.4289),"Salihli":(38.4819,28.1361),"Sarıgöl":(38.2400,28.6861),
    "Saruhanlı":(38.7208,27.5756),"Selendi":(38.7408,28.8597),"Soma":(39.1878,27.6064),
    "Şehzadeler":(38.6300,27.4300),"Turgutlu":(38.4967,27.7100),"Yunusemre":(38.6400,27.4200),
}
MARDIN_ILCE = {
    "Artuklu":(37.3212,40.7245),"Dargeçit":(37.5547,41.7158),"Derik":(37.3617,40.2697),
    "Kızıltepe":(37.1928,40.5869),"Mazıdağı":(37.4594,41.1328),"Midyat":(37.4183,41.3456),
    "Nusaybin":(37.0775,41.2136),"Ömerli":(37.4942,40.9783),"Savur":(37.5317,40.8883),
    "Yeşilli":(37.3436,40.8647),
}
MUGLA_ILCE = {
    "Bodrum":(37.0344,27.4305),"Dalaman":(36.7731,28.7956),"Datça":(36.7264,27.6878),
    "Fethiye":(36.6553,29.1175),"Kavaklıdere":(37.4461,28.3794),"Köyceğiz":(36.9617,28.6883),
    "Marmaris":(36.8561,28.2719),"Menteşe":(37.2153,28.3636),"Milas":(37.3108,27.7878),
    "Ortaca":(36.8356,28.7706),"Seydikemer":(36.6358,29.2206),"Ula":(37.1011,28.4411),
    "Yatağan":(37.3347,28.1419),
}
MUS_ILCE = {
    "Bulanık":(38.9456,42.2703),"Hasköy":(38.6814,41.6908),"Korkut":(38.7022,41.9547),
    "Malazgirt":(39.1447,42.5281),"Merkez":(38.7432,41.4934),"Varto":(39.1736,41.4572),
}
NEVSEHIR_ILCE = {
    "Acıgöl":(38.5514,34.5197),"Avanos":(38.7214,34.8453),"Derinkuyu":(38.3731,34.7347),
    "Gülşehir":(38.7356,34.6253),"Hacıbektaş":(38.9553,34.5600),"Kozaklı":(38.9681,34.8439),
    "Merkez":(38.6939,34.6857),"Ürgüp":(38.6406,34.9167),
}
NIGDE_ILCE = {
    "Altunhisar":(37.9869,34.3956),"Bor":(37.8942,34.5658),"Çamardı":(37.8300,34.9803),
    "Çiftlik":(37.6833,34.5167),"Merkez":(37.9667,34.6833),"Ulukışla":(37.5478,34.4806),
}
ORDU_ILCE = {
    "Akkuş":(40.7919,36.9567),"Altınordu":(40.9860,37.8797),"Aybastı":(40.6869,37.3983),
    "Çamaş":(40.8822,37.0181),"Çatalpınar":(40.8572,37.0094),"Çaybaşı":(41.1150,37.1789),
    "Fatsa":(41.0336,37.4986),"Gölköy":(40.7006,37.6253),"Gülyalı":(40.9692,37.6978),
    "Gürgentepe":(40.8053,37.1353),"İkizce":(41.0503,37.0753),"Kabadüz":(40.6458,37.7953),
    "Kabataş":(40.8336,37.4219),"Korgan":(40.8167,37.2197),"Kumru":(40.8703,37.2531),
    "Mesudiye":(40.3783,37.9361),"Perşembe":(41.0664,37.7706),"Ulubey":(40.6853,37.5025),
    "Ünye":(41.1333,37.2919),
}
OSMANIYE_ILCE = {
    "Bahçe":(37.1975,36.5847),"Düziçi":(37.2353,36.4403),"Hasanbeyli":(37.1828,36.5106),
    "Kadirli":(37.3717,36.0922),"Merkez":(37.0749,36.2464),"Sumbas":(37.4406,36.0853),
    "Toprakkale":(37.0672,36.1433),
}
RIZE_ILCE = {
    "Ardeşen":(41.1875,40.9842),"Çamlıhemşin":(41.0636,40.9142),"Çayeli":(41.0872,40.7328),
    "Derepazarı":(41.1200,40.4869),"Fındıklı":(41.2147,41.1450),"Güneysu":(40.9869,40.5883),
    "Hemşin":(40.9981,41.1119),"İkizdere":(40.8028,40.5539),"İyidere":(41.0694,40.8733),
    "Kalkandere":(40.9264,40.5253),"Merkez":(41.0201,40.5234),"Pazar":(41.1764,40.8828),
}
SAKARYA_ILCE = {
    "Adapazarı":(40.7667,30.4000),"Akyazı":(40.6847,30.6289),"Arifiye":(40.7283,30.3947),
    "Erenler":(40.7664,30.3917),"Ferizli":(40.9772,30.3572),"Geyve":(40.5197,30.3089),
    "Hendek":(40.7914,30.7514),"Karapürçek":(40.7239,30.5522),"Karasu":(41.1131,30.6931),
    "Kaynarca":(41.0239,30.7906),"Kocaali":(41.0603,30.8606),"Merkez":(40.6940,30.4358),
    "Pamukova":(40.5031,30.1633),"Sapanca":(40.6906,30.2622),"Serdivan":(40.7800,30.4100),
    "Söğütlü":(40.7328,30.4894),"Taraklı":(40.3942,30.4992),
}
SAMSUN_ILCE = {
    "19 Mayıs":(41.5178,35.8519),"Alaçam":(41.5922,35.5997),"Asarcık":(40.9756,36.3208),
    "Atakum":(41.3200,36.2700),"Ayvacık":(40.9333,36.5333),"Bafra":(41.5681,35.9092),
    "Canik":(41.2800,36.3200),"Çarşamba":(41.2000,36.7167),"Havza":(40.9656,35.6483),
    "İlkadım":(41.2928,36.3313),"Kavak":(41.0794,36.0428),"Ladik":(40.9208,35.9031),
    "Merkez":(41.2928,36.3313),"Ondokuzmayıs":(41.5297,35.8606),"Salıpazarı":(41.0706,36.5167),
    "Tekkeköy":(41.2122,36.4828),"Terme":(41.2033,36.9792),"Vezirköprü":(41.1411,35.4528),
    "Yakakent":(41.6058,35.5156),
}
SIIRT_ILCE = {
    "Baykan":(38.1700,41.7706),"Eruh":(37.7417,42.1733),"Kurtalan":(37.9228,41.7017),
    "Merkez":(37.9333,41.9500),"Pervari":(37.9647,42.5658),"Şirvan":(38.0753,41.9397),"Tillo":(37.9403,41.9378),
}
SINOP_ILCE = {
    "Ayancık":(41.9481,34.5850),"Boyabat":(41.4639,34.7703),"Dikmen":(41.5631,35.2344),
    "Durağan":(41.4106,35.0575),"Erfelek":(41.8700,34.8181),"Gerze":(41.8006,35.2108),
    "Merkez":(42.0231,35.1531),"Saraydüzü":(41.4583,35.2411),"Türkeli":(41.9600,34.3606),
}
SIVAS_ILCE = {
    "Akıncılar":(39.5656,37.3664),"Altınyayla":(39.9033,37.4628),"Divriği":(39.3714,38.1181),
    "Doğanşar":(40.1233,37.3922),"Gemerek":(39.1833,36.0769),"Gölova":(40.0914,38.1522),
    "Hafik":(39.8572,37.4053),"İmranlı":(39.8847,38.1233),"Kangal":(38.9756,37.3892),
    "Koyulhisar":(40.3122,37.7842),"Merkez":(39.7477,37.0179),"Suşehri":(40.1653,38.0928),
    "Şarkışla":(39.3411,36.4042),"Ulaş":(39.4561,37.0289),"Yıldızeli":(39.8594,36.5953),"Zara":(39.8956,37.8003),
}
TEKIRDAG_ILCE = {
    "Çerkezköy":(41.2875,28.0003),"Çorlu":(41.1586,27.7986),"Ergene":(41.2561,27.0519),
    "Hayrabolu":(41.2119,27.1028),"Kapaklı":(41.3181,27.9767),"Malkara":(41.3011,26.8989),
    "Marmaraereğlisi":(40.9742,27.9406),"Merkez":(40.9781,27.5115),"Muratlı":(41.1700,27.4992),
    "Saray":(41.4408,27.9297),"Şarköy":(40.6128,27.1022),
}
TOKAT_ILCE = {
    "Almus":(40.3861,36.9039),"Artova":(40.0931,36.3428),"Başçiftlik":(40.0483,37.5061),
    "Erbaa":(40.6578,36.5731),"Merkez":(40.3167,36.5500),"Niksar":(40.5944,36.9733),
    "Pazar":(40.2667,36.1917),"Reşadiye":(40.3889,37.3206),"Sulusaray":(40.1003,36.0750),
    "Turhal":(40.3897,36.0800),"Yeşilyurt":(40.3156,36.9386),"Zile":(40.3031,35.8903),
}
TRABZON_ILCE = {
    "Akçaabat":(41.0200,39.5617),"Araklı":(40.9431,39.9339),"Arsin":(41.0222,39.9222),
    "Beşikdüzü":(41.0500,39.2261),"Çarşıbaşı":(41.0386,39.4058),"Çaykara":(40.7419,40.2106),
    "Dernekpazarı":(40.7800,39.9561),"Düzköy":(40.9033,39.5156),"Hayrat":(40.8736,40.2403),
    "Köprübaşı":(40.8028,39.5683),"Maçka":(40.8178,39.6125),"Merkez":(41.0015,39.7178),
    "Of":(40.9506,40.2597),"Ortahisar":(41.0015,39.7178),"Sürmene":(40.9089,40.1142),
    "Şalpazarı":(40.8811,39.1589),"Tonya":(40.8878,39.2903),"Vakfıkebir":(41.0706,39.2764),
    "Yomra":(40.9722,39.8533),
}
TUNCELI_ILCE = {
    "Çemişgezek":(39.0947,38.9197),"Hozat":(39.1014,39.3594),"Mazgirt":(39.0394,39.5739),
    "Merkez":(39.1079,39.5480),"Nazımiye":(39.3700,39.8667),"Ovacık":(39.3708,39.1883),
    "Pertek":(38.8428,39.3233),"Pülümür":(39.4936,40.0128),
}
SANLIURFA_ILCE = {
    "Akçakale":(36.7139,38.9461),"Birecik":(37.0244,37.9808),"Bozova":(37.3697,38.5139),
    "Ceylanpınar":(36.8517,40.0372),"Eyyübiye":(37.1591,38.7969),"Halfeti":(37.2567,37.8786),
    "Haliliye":(37.1400,38.8000),"Harran":(36.8628,39.0297),"Hilvan":(37.5603,38.9628),
    "Karaköprü":(37.1700,38.8000),"Merkez":(37.1591,38.7969),"Siverek":(37.7531,39.3206),
    "Suruç":(36.9681,38.4208),"Viranşehir":(37.2344,39.7600),
}
USAK_ILCE = {
    "Banaz":(38.7325,29.7397),"Eşme":(38.4011,28.9625),"Karahallı":(38.3100,29.5225),
    "Merkez":(38.6823,29.4082),"Sivaslı":(38.5039,29.6914),"Ulubey":(38.4267,29.2847),
}
VAN_ILCE = {
    "Bahçesaray":(38.0978,42.7889),"Başkale":(38.0442,44.0131),"Çaldıran":(39.1458,43.9814),
    "Çatak":(38.0172,43.0567),"Edremit":(38.4628,43.3019),"Erciş":(39.0281,43.3603),
    "Gevaş":(38.2931,43.1028),"Gürpınar":(38.3281,43.4119),"İpekyolu":(38.5000,43.4000),
    "Merkez":(38.4891,43.4089),"Muradiye":(39.0078,43.7444),"Özalp":(38.6611,44.1811),
    "Saray":(38.3219,44.3186),"Tuşba":(38.5100,43.4200),
}
YOZGAT_ILCE = {
    "Akdağmadeni":(39.6594,35.8847),"Aydıncık":(39.5942,34.7250),"Boğazlıyan":(39.1964,35.2486),
    "Çandır":(39.3614,35.5553),"Çayıralan":(39.2956,35.6489),"Çekerek":(40.0736,35.4994),
    "Kadışehri":(40.0819,35.2803),"Merkez":(39.8181,34.8147),"Saraykent":(39.7022,35.4019),
    "Sarıkaya":(39.4942,35.3511),"Şefaatli":(39.5267,36.0222),"Sorgun":(39.8119,35.1847),
    "Yenifakılı":(39.2875,35.4369),"Yerköy":(39.6358,34.4703),
}
ZONGULDAK_ILCE = {
    "Alaplı":(41.1756,31.3869),"Çaycuma":(41.4236,32.0944),"Devrek":(41.2258,32.0017),
    "Ereğli":(41.2736,31.4244),"Gökçebey":(41.3028,32.1403),"Kilimli":(41.4831,31.8136),
    "Kozlu":(41.4408,31.7572),"Merkez":(41.4564,31.7987),
}
AKSARAY_ILCE = {
    "Ağaçören":(38.5750,33.5231),"Eskil":(38.3986,33.3097),"Gülağaç":(38.3856,34.1664),
    "Güzelyurt":(38.2978,34.3694),"Merkez":(38.3687,34.0370),"Ortaköy":(38.7264,34.0731),
    "Sarıyahşi":(38.5139,33.7994),"Sultanhani":(38.2556,33.5497),
}
BAYBURT_ILCE = {
    "Aydıntepe":(40.1558,40.2097),"Demirözü":(40.1681,39.8350),"Merkez":(40.2552,40.2249),
}
KIRIKKALE_ILCE = {
    "Bahşili":(39.7944,33.5267),"Balışeyh":(39.6303,33.6825),"Çelebi":(39.4783,33.5181),
    "Delice":(39.9558,33.9217),"Karakeçili":(39.6133,33.3669),"Keskin":(39.6711,33.6014),
    "Merkez":(39.8468,33.5153),"Sulakyurt":(40.1642,33.3547),"Yahşihan":(39.7675,33.4869),
}
BATMAN_ILCE = {
    "Beşiri":(37.9217,41.2908),"Gercüş":(37.5736,41.1506),"Hasankeyf":(37.7072,41.7053),
    "Kozluk":(38.1981,41.4925),"Merkez":(37.8812,41.1351),"Sason":(38.2819,41.4483),
}
SIRNAK_ILCE = {
    "Beytüşşebap":(37.5658,42.5906),"Cizre":(37.3267,42.1906),"Güçlükonak":(37.4539,42.5961),
    "İdil":(37.3281,41.8906),"Merkez":(37.5181,42.4618),"Silopi":(37.2456,42.4722),"Uludere":(37.3819,43.0478),
}
BARTIN_ILCE = {
    "Amasra":(41.7472,32.3844),"Kurucaşile":(41.8386,32.7194),"Merkez":(41.6344,32.3375),"Ulus":(41.5919,32.6372),
}
ARDAHAN_ILCE = {
    "Çıldır":(41.1317,43.1317),"Damal":(41.1183,42.8142),"Göle":(40.7967,42.6050),
    "Hanak":(41.3833,42.8819),"Merkez":(41.1105,42.7022),"Posof":(41.5231,42.7006),
}
IGDIR_ILCE = {
    "Aralık":(39.8792,44.5186),"Karakoyunlu":(39.9456,43.9194),"Merkez":(39.9167,44.0333),"Tuzluca":(40.0489,43.6550),
}
YALOVA_ILCE = {
    "Altınova":(40.6064,29.5186),"Armutlu":(40.5194,28.8317),"Çiftlikkoy":(40.6767,29.3608),
    "Çınarcık":(40.6397,29.1178),"Merkez":(40.6500,29.2667),"Termal":(40.6208,29.1942),
}
DUZCE_ILCE = {
    "Akçakoca":(41.0831,31.1153),"Cumayeri":(40.9181,31.1800),"Çilimli":(40.9225,31.3047),
    "Gölyaka":(40.7511,31.3303),"Gümüşova":(40.8703,30.8775),"Kaynaşlı":(40.7878,31.3831),
    "Merkez":(40.8438,31.1565),"Yığılca":(40.9878,31.5517),
}

TR_ILCE_MAP = {
    "İstanbul":ISTANBUL_ILCE,"Ankara":ANKARA_ILCE,"İzmir":IZMIR_ILCE,
    "Bursa":BURSA_ILCE,"Antalya":ANTALYA_ILCE,"Konya":KONYA_ILCE,
    "Gaziantep":GAZIANTEP_ILCE,"Adana":ADANA_ILCE,"Kayseri":KAYSERI_ILCE,
    "Adıyaman":ADIYAMAN_ILCE,"Afyon":AFYON_ILCE,"Ağrı":AGRI_ILCE,
    "Amasya":AMASYA_ILCE,"Artvin":ARTVIN_ILCE,"Aydın":AYDIN_ILCE,
    "Balıkesir":BALIKESIR_ILCE,"Bilecik":BILECIK_ILCE,"Bingöl":BINGOL_ILCE,
    "Bitlis":BITLIS_ILCE,"Bolu":BOLU_ILCE,"Burdur":BURDUR_ILCE,
    "Çanakkale":CANAKKALE_ILCE,"Çankırı":CANKIRI_ILCE,"Çorum":CORUM_ILCE,
    "Denizli":DENIZLI_ILCE,"Diyarbakır":DIYARBAKIR_ILCE,"Edirne":EDIRNE_ILCE,
    "Elazığ":ELAZIG_ILCE,"Erzincan":ERZINCAN_ILCE,"Erzurum":ERZURUM_ILCE,
    "Eskişehir":ESKISEHIR_ILCE,"Giresun":GIRESUN_ILCE,"Hakkari":HAKKARI_ILCE,
    "Hatay":HATAY_ILCE,"Isparta":ISPARTA_ILCE,"K.Maraş":KAHRAMANMARAS_ILCE,
    "Karabük":KARABUK_ILCE,"Karaman":KARAMAN_ILCE,"Kars":KARS_ILCE,
    "Kastamonu":KASTAMONU_ILCE,"Kırklareli":KIRKLARELI_ILCE,"Kırşehir":KIRSEHIR_ILCE,
    "Kilis":KILIS_ILCE,"Kocaeli":KOCAELI_ILCE,"Kütahya":KUTAHYA_ILCE,
    "Malatya":MALATYA_ILCE,"Manisa":MANISA_ILCE,"Mardin":MARDIN_ILCE,
    "Muğla":MUGLA_ILCE,"Muş":MUS_ILCE,"Nevşehir":NEVSEHIR_ILCE,
    "Niğde":NIGDE_ILCE,"Ordu":ORDU_ILCE,"Osmaniye":OSMANIYE_ILCE,
    "Rize":RIZE_ILCE,"Sakarya":SAKARYA_ILCE,"Samsun":SAMSUN_ILCE,
    "Siirt":SIIRT_ILCE,"Sinop":SINOP_ILCE,"Sivas":SIVAS_ILCE,
    "Tekirdağ":TEKIRDAG_ILCE,"Tokat":TOKAT_ILCE,"Trabzon":TRABZON_ILCE,
    "Tunceli":TUNCELI_ILCE,"Şanlıurfa":SANLIURFA_ILCE,"Uşak":USAK_ILCE,
    "Van":VAN_ILCE,"Yozgat":YOZGAT_ILCE,"Zonguldak":ZONGULDAK_ILCE,
    "Aksaray":AKSARAY_ILCE,"Bayburt":BAYBURT_ILCE,"Kırıkkale":KIRIKKALE_ILCE,
    "Batman":BATMAN_ILCE,"Şırnak":SIRNAK_ILCE,"Bartın":BARTIN_ILCE,
    "Ardahan":ARDAHAN_ILCE,"Iğdır":IGDIR_ILCE,"Yalova":YALOVA_ILCE,
    "Düzce":DUZCE_ILCE,
}

def get_ilce_listesi(sehir, ulke_kod="TR"):
    if ulke_kod != "TR":
        return []
    m = TR_ILCE_MAP.get(sehir, {})
    return list(m.keys()) if m else []

def get_ilce_koord(sehir, ilce):
    return TR_ILCE_MAP.get(sehir, {}).get(ilce)

# Aladhan method per country
ALADHAN_METHOD = {
    "TR":13,"DE":3,"FR":3,"NL":3,"BE":3,"GB":1,"CH":3,"AT":3,
    "SE":3,"NO":3,"DK":3,"US":2,"CA":2,"SA":4,"EG":5,"MA":21,
    "PK":1,"ID":20,"MY":3,"AE":16,"QA":16,"KW":16,"AZ":3,"RU":3,
    "BA":3,"AL":3,"SG":11,"XK":3,"DZ":19,"TN":5,"LY":3,"SD":3,
    "IQ":3,"SY":3,"JO":3,"LB":3,"YE":4,"AF":1,"BD":1,"KZ":3,
    "UZ":3,"IR":7,"OM":16,"BH":16,"NG":3,"SN":3,"PS":3,"MV":4,
    "MK":3,"KG":3,"TJ":3,
}

# ═══════════════════════════════════════════════
#  API — KOORDİNAT BAZLI ALADHAN
# ═══════════════════════════════════════════════
def aladhan_koord(lat, lon, ulke_kod, tarih=None):
    """Koordinat bazlı Aladhan API — en doğru vakitler. (timings, timezone_str) döndürür."""
    try:
        gun = tarih or datetime.now().strftime("%d-%m-%Y")
        method = ALADHAN_METHOD.get(ulke_kod, 3)
        r = requests.get(
            f"https://api.aladhan.com/v1/timings/{gun}",
            params={"latitude": lat, "longitude": lon, "method": method},
            timeout=15
        )
        if r.status_code == 200:
            d = r.json()
            if d.get("code") == 200:
                timings = d["data"]["timings"]
                tz_str = d["data"]["meta"].get("timezone", "UTC")
                return timings, tz_str
    except Exception as e:
        print(f"[API HATA] {e}")
    return None, None

def vakitler_al(kul, tarih=None):
    """Namaz vakitlerini döndürür. (timings_dict veya None)"""
    lat = kul.get("lat")
    lon = kul.get("lon")
    kod = kul.get("ulke_kod", "TR")

    # Koordinat varsa doğrudan kullan
    if lat and lon:
        result, tz_str = aladhan_koord(lat, lon, kod, tarih)
        if result:
            # timezone bilgisini kul dict'ine kaydet (cache amaçlı)
            if tz_str and not tarih:
                kul["_tz"] = tz_str
            return result

    # Fallback: şehir adı ile dene
    sehir_en = kul.get("sehir_en") or kul.get("sehir") or ""
    try:
        gun = tarih or datetime.now().strftime("%d-%m-%Y")
        method = ALADHAN_METHOD.get(kod, 3)
        r = requests.get(
            f"https://api.aladhan.com/v1/timingsByCity/{gun}",
            params={"city": sehir_en, "country": kod, "method": method},
            timeout=15
        )
        if r.status_code == 200:
            d = r.json()
            if d.get("code") == 200:
                tz_str = d["data"]["meta"].get("timezone", "UTC")
                if tz_str and not tarih:
                    kul["_tz"] = tz_str
                return d["data"]["timings"]
    except Exception as e:
        print(f"[API FALLBACK HATA] {e}")
    return None

def fmt(tm, kul, etiket=""):
    lang = kul.get("lang", "tr") or "tr"
    t = T(lang)
    s = kul.get("sehir") or ""
    i = kul.get("ilce") or s
    d = etiket or datetime.now().strftime("%d.%m.%Y")
    msg  = t["bas"].format(s=s, i=i, d=d)
    msg += t["im"].format(t=tm.get("Fajr", "--"))    + "\n"
    msg += t["gu"].format(t=tm.get("Sunrise", "--")) + "\n"
    msg += t["og"].format(t=tm.get("Dhuhr", "--"))   + "\n"
    msg += t["ik"].format(t=tm.get("Asr", "--"))     + "\n"
    msg += t["ak"].format(t=tm.get("Maghrib", "--")) + "\n"
    msg += t["ya"].format(t=tm.get("Isha", "--"))    + "\n"
    sv, st = sonraki(tm, lang)
    if sv:
        msg += t["son"].format(v=sv, t=st)
    msg += "\n\n🤲 @NikeCheatYeniden | 📢 @nikestoretr"
    return msg

def sonraki(tm, lang="tr"):
    now = datetime.now()
    for k in ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]:
        sv = tm.get(k, "")
        if not sv or sv == "--":
            continue
        try:
            h, m = map(int, sv.split(":")[:2])
            dt = now.replace(hour=h, minute=m, second=0, microsecond=0)
            if dt > now:
                return T(lang)["ad"].get(k, k), sv
        except:
            pass
    return None, None

# ═══════════════════════════════════════════════
#  TELEGRAM HTTP
# ═══════════════════════════════════════════════
BASE = f"https://api.telegram.org/bot{BOT_TOKEN}"

def tg_get(method, params=None):
    try:
        r = requests.get(f"{BASE}/{method}", params=params, timeout=15)
        return r.json()
    except:
        return {}

def tg_post(method, data):
    try:
        r = requests.post(f"{BASE}/{method}", json=data, timeout=15)
        return r.json()
    except:
        return {}

def send(chat_id, text, kb=None, parse_mode="Markdown"):
    d = {"chat_id": chat_id, "text": text, "parse_mode": parse_mode}
    if kb:
        d["reply_markup"] = kb
    return tg_post("sendMessage", d)

def send_photo(chat_id, photo_url, caption="", kb=None):
    d = {"chat_id": chat_id, "photo": photo_url, "caption": caption, "parse_mode": "Markdown"}
    if kb:
        d["reply_markup"] = kb
    try:
        r = tg_post("sendPhoto", d)
        return r
    except:
        return {"ok": False}

def edit_caption(chat_id, msg_id, text, kb=None):
    d = {"chat_id": chat_id, "message_id": msg_id, "caption": text[:1024], "parse_mode": "Markdown"}
    if kb: d["reply_markup"] = kb
    return tg_post("editMessageCaption", d)

def logo_send(chat_id, text, kb=None):
    """Bot logosunu caption ve butonlarla BİRLİKTE tek mesaj olarak gönderir."""
    d = {"chat_id": chat_id, "photo": BOT_LOGO, "caption": text[:1024], "parse_mode": "Markdown"}
    if kb: d["reply_markup"] = kb
    r = tg_post("sendPhoto", d)
    if not r.get("ok"):
        return send(chat_id, text, kb)
    return r

def edit(chat_id, msg_id, text, kb=None, parse_mode="Markdown"):
    d = {"chat_id": chat_id, "message_id": msg_id, "text": text, "parse_mode": parse_mode}
    if kb:
        d["reply_markup"] = kb
    return tg_post("editMessageText", d)

def ikb(*rows):
    return {"inline_keyboard": list(rows)}

def btn(text, data):
    return {"text": text, "callback_data": data}

# ═══════════════════════════════════════════════
#  ADMİN
# ═══════════════════════════════════════════════
def admin_ok(uid):
    if not ADMIN_IDS:
        return True
    return uid in ADMIN_IDS

def admin_panel():
    lg = log_yukle()
    events = lg.get("events", [])
    toplam = len(VERI["k"])
    aktif = sum(1 for u in VERI["k"].values() if u.get("aktif") and u.get("sehir"))
    ban_sayisi = sum(1 for b in VERI.get("ban", {}).values() if b.get("banned"))
    son5 = events[-5:] if events else []
    log_str = ""
    for e in reversed(son5):
        log_str += f"\n🔹 {e.get('zaman','')} | {e.get('olay','')} | {e.get('isim','')}"
    kanal_str = str(LOG_KANAL) if LOG_KANAL else "Ayarlanmamış"
    return (
        "🔐 *ADMİN PANELİ*\n━━━━━━━━━━━━━━━━━━\n"
        f"👥 Toplam kullanıcı : {toplam}\n"
        f"✅ Aktif uyarı      : {aktif}\n"
        f"🔔 Bugün gönderilen : {VERI.get('bugun',0)}\n"
        f"📨 Toplam uyarı     : {VERI.get('toplam',0)}\n"
        f"🚫 Banlı kullanıcı  : {ban_sayisi}\n"
        f"📋 Log kanalı       : {kanal_str}\n"
        "━━━━━━━━━━━━━━━━━━\n📜 SON OLAYLAR:"
        + (log_str or "\nHenüz kayıt yok.") + "\n━━━━━━━━━━━━━━━━━━"
    )

def kul_listesi():
    s = ["👥 *KULLANICI LİSTESİ*\n━━━━━━━━━━━━━━━━━━"]
    for uid_str, kul in list(VERI["k"].items())[:20]:
        ban_info = VERI.get("ban", {}).get(uid_str, {})
        if ban_info.get("banned"):
            ak = "🚫"
        elif ban_info.get("mute_until") and datetime.now().timestamp() < ban_info["mute_until"]:
            ak = "🔇"
        elif kul.get("aktif"):
            ak = "✅"
        else:
            ak = "🔕"
        s.append(f"\n{ak} {kul.get('isim','?')} | {kul.get('sehir','--')}/{kul.get('ilce','--')}\n   📅 {kul.get('kayit','--')}")
    if len(VERI["k"]) > 20:
        s.append(f"\n... +{len(VERI['k'])-20} kişi daha")
    return "\n".join(s)

def son_loglar():
    lg = log_yukle()
    events = lg.get("events", [])
    son = events[-15:] if events else []
    s = ["📜 *SON 15 LOG*\n━━━━━━━━━━━━━━━━━━"]
    for e in reversed(son):
        detay = f" — {e.get('detay','')}" if e.get("detay") else ""
        s.append(f"\n🔹 {e.get('zaman','')}\n   {e.get('olay','')} — {e.get('isim','')}{detay}")
    return "\n".join(s) if son else "Henüz log yok."

# ═══════════════════════════════════════════════
#  KLAVYELER
# ═══════════════════════════════════════════════
def dil_kb():
    rows = []
    row = []
    for kod, isim in DILLER.items():
        row.append(btn(isim, f"L_{kod}"))
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    return ikb(*rows)

def ulke_kb(s=0, lang="tr"):
    liste = list(ULKELER.keys())
    ceviri = ULKE_CEVIRI.get(lang, ULKE_CEVIRI["tr"])
    n = 9
    b = s * n
    p = liste[b:b+n]
    rows = []
    row = []
    for x in p:
        row.append(btn(ceviri.get(x, x), f"U_{x}"))
        if len(row) == 3:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    nav = []
    if s > 0:
        nav.append(btn("◀️", f"US_{s-1}"))
    nav.append(btn(f"• {s+1} •", "US_X"))
    if b + n < len(liste):
        nav.append(btn("▶️", f"US_{s+1}"))
    rows.append(nav)
    rows.append([btn(kb(lang)["ana_menu"], "M_menu")])
    return ikb(*rows)

def sehir_kb(ulke_kod, s=0, lang="tr"):
    veri = SEHIR_KOORDINAT.get(ulke_kod, {})
    liste = list(veri.keys())
    if not liste:
        return None
    n = 9
    b = s * n
    p = liste[b:b+n]
    rows = []
    row = []
    for x in p:
        row.append(btn(x, f"S_{x}"))
        if len(row) == 3:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    nav = []
    if s > 0:
        nav.append(btn("◀️", f"SS_{s-1}"))
    nav.append(btn(f"• {s+1} •", "SS_X"))
    if b + n < len(liste):
        nav.append(btn("▶️", f"SS_{s+1}"))
    rows.append(nav)
    rows.append([btn(kb(lang)["ulkelere"], "M_k"), btn(kb(lang)["ana_menu"], "M_menu")])
    return ikb(*rows)

def ilce_kb(sehir, s=0, ulke_kod="TR", lang="tr"):
    ilceler = get_ilce_listesi(sehir, ulke_kod)
    if not ilceler:
        return None
    n = 9
    b = s * n
    p = ilceler[b:b+n]
    rows = []
    row = []
    for x in p:
        row.append(btn(x, f"I_{x}"))
        if len(row) == 3:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    nav = []
    if s > 0:
        nav.append(btn("◀️", f"IS_{sehir}_{s-1}"))
    if b + n < len(ilceler):
        nav.append(btn("▶️", f"IS_{sehir}_{s+1}"))
    if nav:
        rows.append(nav)
    rows.append([btn(kb(lang)["sehirlere"], f"SB_{ulke_kod}")])
    rows.append([btn(kb(lang)["ana_menu"], "M_menu")])
    return ikb(*rows)

def uyari_kb():
    return ikb(
        [btn("⏰ 5dk", "A_5"),  btn("⏰ 10dk", "A_10"), btn("⏰ 15dk", "A_15")],
        [btn("⏰ 20dk", "A_20"), btn("⏰ 30dk", "A_30"), btn("⏰ 45dk", "A_45")],
        [btn("⏰ 60dk", "A_60"), btn("🏠 Ana Menü", "M_menu")]
    )

def api_kb():
    return ikb(
        [btn("🌍 Aladhan", "P_aladhan"), btn("🤖 Otomatik", "P_auto")],
        [btn("🏠 Ana Menü", "M_menu")]
    )

# Menü butonları — her dilde farklı
MENU_BTN = {
    # (Vakitler, Yarın, Haftalık, Konum, Uyarı, Ayarlar, Yardım, Dil, ÖzelGünler)
    "tr": ("🕌 Vakitler","📅 Yarın","📆 Haftalık","📍 Konum","⏰ Uyarı","⚙️ Ayarlar","📖 Yardım","🌐 Dil","🌙 Özel Günler"),
    "ar": ("🕌 اليوم","📅 الغد","📆 الأسبوع","📍 الموقع","⏰ التنبيه","⚙️ الإعدادات","📖 مساعدة","🌐 اللغة","🌙 مناسبات"),
    "de": ("🕌 Zeiten","📅 Morgen","📆 Wöchentlich","📍 Standort","⏰ Alarm","⚙️ Einstellungen","📖 Hilfe","🌐 Sprache","🌙 Heilige Tage"),
    "fr": ("🕌 Prières","📅 Demain","📆 Semaine","📍 Localisation","⏰ Alerte","⚙️ Paramètres","📖 Aide","🌐 Langue","🌙 Jours Spéciaux"),
    "nl": ("🕌 Tijden","📅 Morgen","📆 Wekelijks","📍 Locatie","⏰ Alarm","⚙️ Instellingen","📖 Help","🌐 Taal","🌙 Heilige Dagen"),
    "en": ("🕌 Times","📅 Tomorrow","📆 Weekly","📍 Location","⏰ Alert","⚙️ Settings","📖 Help","🌐 Language","🌙 Special Days"),
    "ur": ("🕌 اوقات","📅 کل","📆 ہفتہ","📍 مقام","⏰ اطلاع","⚙️ ترتیبات","📖 مدد","🌐 زبان","🌙 خاص دن"),
    "id": ("🕌 Waktu","📅 Besok","📆 Mingguan","📍 Lokasi","⏰ Alarm","⚙️ Pengaturan","📖 Bantuan","🌐 Bahasa","🌙 Hari Khusus"),
    "ms": ("🕌 Waktu","📅 Esok","📆 Mingguan","📍 Lokasi","⏰ Amaran","⚙️ Tetapan","📖 Bantuan","🌐 Bahasa","🌙 Hari Istimewa"),
    "ru": ("🕌 Намазы","📅 Завтра","📆 Неделя","📍 Место","⏰ Аларм","⚙️ Настройки","📖 Помощь","🌐 Язык","🌙 Особые Дни"),
    "az": ("🕌 Vaxtlar","📅 Sabah","📆 Həftəlik","📍 Məkan","⏰ Alarm","⚙️ Ayarlar","📖 Kömək","🌐 Dil","🌙 Xüsusi Günlər"),
    "bs": ("🕌 Namazi","📅 Sutra","📆 Sedmica","📍 Lokacija","⏰ Alarm","⚙️ Postavke","📖 Pomoć","🌐 Jezik","🌙 Posebni Dani"),
    "sq": ("🕌 Kohët","📅 Nesër","📆 Java","📍 Vendndodhja","⏰ Alarm","⚙️ Cilësime","📖 Ndihmë","🌐 Gjuhë","🌙 Ditë Speciale"),
}

# Klavye buton çevirileri (navigasyon butonları)
KB_BTN = {
    "tr": {"ana_menu":"🏠 Ana Menü","ulkelere":"◀️ Ülkelere","sehirlere":"◀️ Şehirlere","ilce_yok_btn":"✅ Tamam"},
    "ar": {"ana_menu":"🏠 الرئيسية","ulkelere":"◀️ الدول","sehirlere":"◀️ المدن","ilce_yok_btn":"✅ حسناً"},
    "de": {"ana_menu":"🏠 Hauptmenü","ulkelere":"◀️ Länder","sehirlere":"◀️ Städte","ilce_yok_btn":"✅ OK"},
    "fr": {"ana_menu":"🏠 Menu","ulkelere":"◀️ Pays","sehirlere":"◀️ Villes","ilce_yok_btn":"✅ OK"},
    "nl": {"ana_menu":"🏠 Menu","ulkelere":"◀️ Landen","sehirlere":"◀️ Steden","ilce_yok_btn":"✅ OK"},
    "en": {"ana_menu":"🏠 Main Menu","ulkelere":"◀️ Countries","sehirlere":"◀️ Cities","ilce_yok_btn":"✅ OK"},
    "ur": {"ana_menu":"🏠 مین مینو","ulkelere":"◀️ ممالک","sehirlere":"◀️ شہر","ilce_yok_btn":"✅ ٹھیک"},
    "id": {"ana_menu":"🏠 Menu","ulkelere":"◀️ Negara","sehirlere":"◀️ Kota","ilce_yok_btn":"✅ OK"},
    "ms": {"ana_menu":"🏠 Menu","ulkelere":"◀️ Negara","sehirlere":"◀️ Bandar","ilce_yok_btn":"✅ OK"},
    "ru": {"ana_menu":"🏠 Меню","ulkelere":"◀️ Страны","sehirlere":"◀️ Города","ilce_yok_btn":"✅ ОК"},
    "az": {"ana_menu":"🏠 Menyu","ulkelere":"◀️ Ölkələr","sehirlere":"◀️ Şəhərlər","ilce_yok_btn":"✅ Tamam"},
    "bs": {"ana_menu":"🏠 Meni","ulkelere":"◀️ Države","sehirlere":"◀️ Gradovi","ilce_yok_btn":"✅ OK"},
    "sq": {"ana_menu":"🏠 Menyja","ulkelere":"◀️ Vendet","sehirlere":"◀️ Qytetet","ilce_yok_btn":"✅ OK"},
}

def kb(lang="tr"):
    return KB_BTN.get(lang, KB_BTN["tr"])

def url_btn(text, url):
    return {"text": text, "url": url}

def menu_kb(lang="tr"):
    b = MENU_BTN.get(lang, MENU_BTN["tr"])
    return {
        "inline_keyboard": [
            [btn(b[0], "M_v"), btn(b[1], "M_y"), btn(b[2], "M_h7")],
            [btn(b[3], "M_k"), btn(b[4], "M_u"), btn(b[5], "M_a")],
            [btn(b[8], "M_og"), btn(b[6], "M_h"), btn(b[7], "M_dil")],
            [url_btn(KURUCU_LABEL, KURUCU_URL), url_btn(KANAL_LABEL, KANAL_URL)],
        ]
    }

def admin_kb():
    return ikb(
        [btn("👥 Kullanıcılar", "AD_users"), btn("📜 Loglar", "AD_logs"), btn("📊 İstatistik", "AD_stat")],
        [btn("🚫 Banlı Listesi", "AD_banlist"), btn("🗑️ Log Temizle", "AD_clearlog")],
        [btn("🏠 Ana Menü", "M_menu")]
    )

def haftalik_alt_kb(lang="tr"):
    """Vakitler/Yarın/Haftalık mesajlarının altına kanal/kurucu + ana menü butonu"""
    return {
        "inline_keyboard": [
            [btn("🏠 Ana Menü", "M_menu")],
            [
                {"text": KURUCU_LABEL, "url": KURUCU_URL},
                {"text": KANAL_LABEL, "url": KANAL_URL},
            ]
        ]
    }

# Vakit isimleri
VAKIT_ISIM = {
    "Fajr":    ("🌙", "İmsak"),
    "Dhuhr":   ("🌤️", "Öğle"),
    "Asr":     ("🌇", "İkindi"),
    "Maghrib": ("🌆", "Akşam/İftar"),
    "Isha":    ("🌃", "Yatsı"),
}

def grup_ayar_kb(chat_id):
    """Grup ezan bildirimi ayar klavyesi"""
    g = VERI.get("gruplar", {}).get(str(chat_id), {})
    aktif_vakitler = g.get("aktif_vakitler", [])
    genel_aktif = g.get("aktif", False)
    sehir = g.get("sehir", "—")

    rows = []
    # Genel açma/kapama
    durum = "🟢 AKTİF" if genel_aktif else "🔴 PASİF"
    rows.append([btn(f"⚡ Bildirim: {durum}", f"GA_TOGGLE_{chat_id}")])
    # Konum ayarla
    rows.append([btn(f"📍 Konum: {sehir}", f"GA_KONUM_{chat_id}")])
    rows.append([btn("━━━━ Vakitler ━━━━", "GA_NOP")])
    # Her vakit için açma/kapama
    for vakit_k, (emoji, vakit_isim) in VAKIT_ISIM.items():
        ac = vakit_k in aktif_vakitler
        durum_v = "✅" if ac else "❌"
        rows.append([btn(f"{durum_v} {emoji} {vakit_isim}", f"GA_V_{chat_id}_{vakit_k}")])
    # Uyarı süresi
    dk = g.get("dk", 0)
    dk_label = f"{dk} dk önce" if dk > 0 else "Vakitte"
    rows.append([btn(f"⏰ Bildirim: {dk_label}", f"GA_DK_{chat_id}")])
    return ikb(*rows)

def grup_dk_kb(chat_id):
    """Grup bildirim süresi seçimi"""
    return ikb(
        [btn("Vakitte (0dk)", f"GD_{chat_id}_0"),  btn("5 dk önce",  f"GD_{chat_id}_5")],
        [btn("10 dk önce",   f"GD_{chat_id}_10"), btn("15 dk önce", f"GD_{chat_id}_15")],
        [btn("20 dk önce",   f"GD_{chat_id}_20"), btn("30 dk önce", f"GD_{chat_id}_30")],
        [btn("◀️ Geri",       f"GA_GERI_{chat_id}")]
    )

def grup_konum_kb(chat_id, ulke_kod="TR", sayfa=0):
    """Grup konum seçimi - ülke listesi"""
    return ikb(
        [btn("🇹🇷 Türkiye", f"GK_TR_{chat_id}"),   btn("🇸🇦 S.Arabistan", f"GK_SA_{chat_id}")],
        [btn("🇩🇪 Almanya",  f"GK_DE_{chat_id}"),   btn("🇬🇧 İngiltere",  f"GK_GB_{chat_id}")],
        [btn("🇳🇱 Hollanda", f"GK_NL_{chat_id}"),   btn("🇫🇷 Fransa",     f"GK_FR_{chat_id}")],
        [btn("🇵🇰 Pakistan", f"GK_PK_{chat_id}"),   btn("🇮🇩 Endonezya",  f"GK_ID_{chat_id}")],
        [btn("🌍 Diğer ülkeler → DM'den /konum", "GA_NOP")],
        [btn("◀️ Geri", f"GA_GERI_{chat_id}")]
    )

def grup_sehir_kb(chat_id, ulke_kod, sayfa=0):
    """Grup şehir seçim klavyesi"""
    veri = SEHIR_KOORDINAT.get(ulke_kod, {})
    liste = list(veri.keys())
    n = 8
    b = sayfa * n
    p = liste[b:b+n]
    rows = []
    row = []
    for x in p:
        row.append(btn(x, f"GS_{chat_id}_{ulke_kod}_{x}"))
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    nav = []
    if sayfa > 0:
        nav.append(btn("◀️", f"GSP_{chat_id}_{ulke_kod}_{sayfa-1}"))
    if b + n < len(liste):
        nav.append(btn("▶️", f"GSP_{chat_id}_{ulke_kod}_{sayfa+1}"))
    if nav:
        rows.append(nav)
    rows.append([btn("◀️ Geri", f"GA_GERI_{chat_id}")])
    return ikb(*rows)

def ozel_gun_kb(yil=None):
    """Özel günler yıl seçimi klavyesi"""
    if yil is None:
        yil = datetime.now().year
    rows = []
    # Yıl navigasyonu
    rows.append([
        btn("◀️", f"OG_Y_{yil-1}"),
        btn(f"📅 {yil}", f"OG_Y_{yil}"),
        btn("▶️", f"OG_Y_{yil+1}")
    ])
    # Ay butonları
    aylar = ["Ocak","Şubat","Mart","Nisan","Mayıs","Haziran",
             "Tem.","Ağu.","Eylül","Ekim","Kasım","Aralık"]
    row = []
    for i, ay in enumerate(aylar, 1):
        row.append(btn(ay, f"OG_A_{yil}_{i}"))
        if len(row) == 4:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([btn("📋 Yıllık Tüm Günler", f"OG_TUM_{yil}")])
    rows.append([btn("🏠 Ana Menü", "M_menu")])
    return ikb(*rows)

# ═══════════════════════════════════════════════
#  İSLAMİ ÖZEL GÜNLER VERİSİ (2020–2050)
# ═══════════════════════════════════════════════
# Format: (tarih_str, isim, açıklama_kısa, emoji)
# Tarih: "DD.MM.YYYY"
OZEL_GUNLER = [
    # 2020
    ("23.04.2020","🌙 Ramazan Başlangıcı","Ramazan ayı başladı — mübarek olsun!","🌙"),
    ("23.05.2020","🎉 Ramazan Bayramı (1. Gün)","Ramazan Bayramı'nın ilk günü","🎉"),
    ("24.05.2020","🎉 Ramazan Bayramı (2. Gün)","Ramazan Bayramı'nın ikinci günü","🎉"),
    ("25.05.2020","🎉 Ramazan Bayramı (3. Gün)","Ramazan Bayramı'nın üçüncü günü","🎉"),
    ("19.06.2020","🕋 Arefe Günü","Hac ibadetinin en önemli günü","🕋"),
    ("20.06.2020","🐑 Kurban Bayramı (1. Gün)","Kurban Bayramı'nın ilk günü","🐑"),
    ("21.06.2020","🐑 Kurban Bayramı (2. Gün)","Kurban Bayramı'nın ikinci günü","🐑"),
    ("22.06.2020","🐑 Kurban Bayramı (3. Gün)","Kurban Bayramı'nın üçüncü günü","🐑"),
    ("23.06.2020","🐑 Kurban Bayramı (4. Gün)","Kurban Bayramı'nın dördüncü günü","🐑"),
    ("28.08.2020","🕌 Muharrem (Hicri Yılbaşı)","Hicri 1442 yılının başlangıcı","🕌"),
    ("07.09.2020","😔 Aşure Günü","Hz. Nuh'un gemisinin karaya oturduğu gün","😔"),
    ("29.10.2020","🌟 Mevlid Kandili","Hz. Muhammed'in doğum gecesi","🌟"),
    # 2021
    ("12.03.2021","🌺 Regaib Kandili","İlk kandil gecesi","🌺"),
    ("24.03.2021","💫 Miraç Kandili","Hz. Muhammed'in miraca yükseldiği gece","💫"),
    ("08.04.2021","🌙 Berat Kandili","Günahların bağışlandığı mübarek gece","🌙"),
    ("12.04.2021","🌙 Ramazan Başlangıcı","Ramazan ayı başladı — mübarek olsun!","🌙"),
    ("13.05.2021","🌙 Kadir Gecesi","Bin aydan daha hayırlı gece","🌙"),
    ("13.05.2021","🎉 Ramazan Bayramı (1. Gün)","Ramazan Bayramı'nın ilk günü","🎉"),
    ("14.05.2021","🎉 Ramazan Bayramı (2. Gün)","Ramazan Bayramı'nın ikinci günü","🎉"),
    ("15.05.2021","🎉 Ramazan Bayramı (3. Gün)","Ramazan Bayramı'nın üçüncü günü","🎉"),
    ("18.07.2021","🕋 Arefe Günü","Hac ibadetinin en önemli günü","🕋"),
    ("19.07.2021","🐑 Kurban Bayramı (1. Gün)","Kurban Bayramı'nın ilk günü","🐑"),
    ("20.07.2021","🐑 Kurban Bayramı (2. Gün)","Kurban Bayramı'nın ikinci günü","🐑"),
    ("21.07.2021","🐑 Kurban Bayramı (3. Gün)","Kurban Bayramı'nın üçüncü günü","🐑"),
    ("22.07.2021","🐑 Kurban Bayramı (4. Gün)","Kurban Bayramı'nın dördüncü günü","🐑"),
    ("19.08.2021","🕌 Muharrem (Hicri Yılbaşı)","Hicri 1443 yılının başlangıcı","🕌"),
    ("28.08.2021","😔 Aşure Günü","Hz. Hüseyin'in şehadet günü anması","😔"),
    ("19.10.2021","🌟 Mevlid Kandili","Hz. Muhammed'in doğum gecesi","🌟"),
    # 2022
    ("01.03.2022","🌺 Regaib Kandili","İlk kandil gecesi","🌺"),
    ("13.03.2022","💫 Miraç Kandili","Hz. Muhammed'in miraca yükseldiği gece","💫"),
    ("28.03.2022","🌙 Berat Kandili","Günahların bağışlandığı mübarek gece","🌙"),
    ("02.04.2022","🌙 Ramazan Başlangıcı","Ramazan ayı başladı — mübarek olsun!","🌙"),
    ("01.05.2022","🌙 Kadir Gecesi","Bin aydan daha hayırlı gece","🌙"),
    ("02.05.2022","🎉 Ramazan Bayramı (1. Gün)","Ramazan Bayramı'nın ilk günü","🎉"),
    ("03.05.2022","🎉 Ramazan Bayramı (2. Gün)","Ramazan Bayramı'nın ikinci günü","🎉"),
    ("04.05.2022","🎉 Ramazan Bayramı (3. Gün)","Ramazan Bayramı'nın üçüncü günü","🎉"),
    ("08.07.2022","🕋 Arefe Günü","Hac ibadetinin en önemli günü","🕋"),
    ("09.07.2022","🐑 Kurban Bayramı (1. Gün)","Kurban Bayramı'nın ilk günü","🐑"),
    ("10.07.2022","🐑 Kurban Bayramı (2. Gün)","Kurban Bayramı'nın ikinci günü","🐑"),
    ("11.07.2022","🐑 Kurban Bayramı (3. Gün)","Kurban Bayramı'nın üçüncü günü","🐑"),
    ("12.07.2022","🐑 Kurban Bayramı (4. Gün)","Kurban Bayramı'nın dördüncü günü","🐑"),
    ("30.07.2022","🕌 Muharrem (Hicri Yılbaşı)","Hicri 1444 yılının başlangıcı","🕌"),
    ("08.08.2022","😔 Aşure Günü","Muharrem'in 10. günü","😔"),
    ("08.10.2022","🌟 Mevlid Kandili","Hz. Muhammed'in doğum gecesi","🌟"),
    # 2023
    ("16.02.2023","🌺 Regaib Kandili","İlk kandil gecesi","🌺"),
    ("18.02.2023","💫 Miraç Kandili","Hz. Muhammed'in miraca yükseldiği gece","💫"),
    ("07.03.2023","🌙 Berat Kandili","Günahların bağışlandığı mübarek gece","🌙"),
    ("23.03.2023","🌙 Ramazan Başlangıcı","Ramazan ayı başladı — mübarek olsun!","🌙"),
    ("18.04.2023","🌙 Kadir Gecesi","Bin aydan daha hayırlı gece","🌙"),
    ("21.04.2023","🎉 Ramazan Bayramı (1. Gün)","Ramazan Bayramı'nın ilk günü","🎉"),
    ("22.04.2023","🎉 Ramazan Bayramı (2. Gün)","Ramazan Bayramı'nın ikinci günü","🎉"),
    ("23.04.2023","🎉 Ramazan Bayramı (3. Gün)","Ramazan Bayramı'nın üçüncü günü","🎉"),
    ("27.06.2023","🕋 Arefe Günü","Hac ibadetinin en önemli günü","🕋"),
    ("28.06.2023","🐑 Kurban Bayramı (1. Gün)","Kurban Bayramı'nın ilk günü","🐑"),
    ("29.06.2023","🐑 Kurban Bayramı (2. Gün)","Kurban Bayramı'nın ikinci günü","🐑"),
    ("30.06.2023","🐑 Kurban Bayramı (3. Gün)","Kurban Bayramı'nın üçüncü günü","🐑"),
    ("01.07.2023","🐑 Kurban Bayramı (4. Gün)","Kurban Bayramı'nın dördüncü günü","🐑"),
    ("19.07.2023","🕌 Muharrem (Hicri Yılbaşı)","Hicri 1445 yılının başlangıcı","🕌"),
    ("29.07.2023","😔 Aşure Günü","Muharrem'in 10. günü","😔"),
    ("28.09.2023","🌟 Mevlid Kandili","Hz. Muhammed'in doğum gecesi","🌟"),
    # 2024
    ("08.02.2024","🌺 Regaib Kandili","İlk kandil gecesi","🌺"),
    ("07.03.2024","💫 Miraç Kandili","Hz. Muhammed'in miraca yükseldiği gece","💫"),
    ("25.03.2024","🌙 Berat Kandili","Günahların bağışlandığı mübarek gece","🌙"),
    ("10.03.2024","🌙 Ramazan Başlangıcı","Ramazan ayı başladı — mübarek olsun!","🌙"),
    ("05.04.2024","🌙 Kadir Gecesi","Bin aydan daha hayırlı gece","🌙"),
    ("10.04.2024","🎉 Ramazan Bayramı (1. Gün)","Ramazan Bayramı'nın ilk günü","🎉"),
    ("11.04.2024","🎉 Ramazan Bayramı (2. Gün)","Ramazan Bayramı'nın ikinci günü","🎉"),
    ("12.04.2024","🎉 Ramazan Bayramı (3. Gün)","Ramazan Bayramı'nın üçüncü günü","🎉"),
    ("15.06.2024","🕋 Arefe Günü","Hac ibadetinin en önemli günü","🕋"),
    ("16.06.2024","🐑 Kurban Bayramı (1. Gün)","Kurban Bayramı'nın ilk günü","🐑"),
    ("17.06.2024","🐑 Kurban Bayramı (2. Gün)","Kurban Bayramı'nın ikinci günü","🐑"),
    ("18.06.2024","🐑 Kurban Bayramı (3. Gün)","Kurban Bayramı'nın üçüncü günü","🐑"),
    ("19.06.2024","🐑 Kurban Bayramı (4. Gün)","Kurban Bayramı'nın dördüncü günü","🐑"),
    ("07.07.2024","🕌 Muharrem (Hicri Yılbaşı)","Hicri 1446 yılının başlangıcı","🕌"),
    ("17.07.2024","😔 Aşure Günü","Muharrem'in 10. günü","😔"),
    ("15.09.2024","🌟 Mevlid Kandili","Hz. Muhammed'in doğum gecesi","🌟"),
    # 2025
    ("30.01.2025","🌺 Regaib Kandili","İlk kandil gecesi","🌺"),
    ("27.02.2025","💫 Miraç Kandili","Hz. Muhammed'in miraca yükseldiği gece","💫"),
    ("14.03.2025","🌙 Berat Kandili","Günahların bağışlandığı mübarek gece","🌙"),
    ("01.03.2025","🌙 Ramazan Başlangıcı","Ramazan ayı başladı — mübarek olsun!","🌙"),
    ("27.03.2025","🌙 Kadir Gecesi","Bin aydan daha hayırlı gece","🌙"),
    ("30.03.2025","🎉 Ramazan Bayramı (1. Gün)","Ramazan Bayramı'nın ilk günü","🎉"),
    ("31.03.2025","🎉 Ramazan Bayramı (2. Gün)","Ramazan Bayramı'nın ikinci günü","🎉"),
    ("01.04.2025","🎉 Ramazan Bayramı (3. Gün)","Ramazan Bayramı'nın üçüncü günü","🎉"),
    ("05.06.2025","🕋 Arefe Günü","Hac ibadetinin en önemli günü","🕋"),
    ("06.06.2025","🐑 Kurban Bayramı (1. Gün)","Kurban Bayramı'nın ilk günü","🐑"),
    ("07.06.2025","🐑 Kurban Bayramı (2. Gün)","Kurban Bayramı'nın ikinci günü","🐑"),
    ("08.06.2025","🐑 Kurban Bayramı (3. Gün)","Kurban Bayramı'nın üçüncü günü","🐑"),
    ("09.06.2025","🐑 Kurban Bayramı (4. Gün)","Kurban Bayramı'nın dördüncü günü","🐑"),
    ("27.06.2025","🕌 Muharrem (Hicri Yılbaşı)","Hicri 1447 yılının başlangıcı","🕌"),
    ("07.07.2025","😔 Aşure Günü","Muharrem'in 10. günü","😔"),
    ("04.09.2025","🌟 Mevlid Kandili","Hz. Muhammed'in doğum gecesi","🌟"),
    # 2026
    ("22.01.2026","🌺 Regaib Kandili","İlk kandil gecesi","🌺"),
    ("16.02.2026","💫 Miraç Kandili","Hz. Muhammed'in miraca yükseldiği gece","💫"),
    ("03.03.2026","🌙 Berat Kandili","Günahların bağışlandığı mübarek gece","🌙"),
    ("18.02.2026","🌙 Ramazan Başlangıcı","Ramazan ayı başladı — mübarek olsun!","🌙"),
    ("16.03.2026","🌙 Kadir Gecesi","Bin aydan daha hayırlı gece","🌙"),
    ("20.03.2026","🎉 Ramazan Bayramı (1. Gün)","Ramazan Bayramı'nın ilk günü","🎉"),
    ("21.03.2026","🎉 Ramazan Bayramı (2. Gün)","Ramazan Bayramı'nın ikinci günü","🎉"),
    ("22.03.2026","🎉 Ramazan Bayramı (3. Gün)","Ramazan Bayramı'nın üçüncü günü","🎉"),
    ("26.05.2026","🕋 Arefe Günü","Hac ibadetinin en önemli günü","🕋"),
    ("27.05.2026","🐑 Kurban Bayramı (1. Gün)","Kurban Bayramı'nın ilk günü","🐑"),
    ("28.05.2026","🐑 Kurban Bayramı (2. Gün)","Kurban Bayramı'nın ikinci günü","🐑"),
    ("29.05.2026","🐑 Kurban Bayramı (3. Gün)","Kurban Bayramı'nın üçüncü günü","🐑"),
    ("30.05.2026","🐑 Kurban Bayramı (4. Gün)","Kurban Bayramı'nın dördüncü günü","🐑"),
    ("16.06.2026","🕌 Muharrem (Hicri Yılbaşı)","Hicri 1448 yılının başlangıcı","🕌"),
    ("26.06.2026","😔 Aşure Günü","Muharrem'in 10. günü","😔"),
    ("24.08.2026","🌟 Mevlid Kandili","Hz. Muhammed'in doğum gecesi","🌟"),
    # 2027
    ("10.01.2027","🌺 Regaib Kandili","İlk kandil gecesi","🌺"),
    ("05.02.2027","💫 Miraç Kandili","Hz. Muhammed'in miraca yükseldiği gece","💫"),
    ("20.02.2027","🌙 Berat Kandili","Günahların bağışlandığı mübarek gece","🌙"),
    ("08.02.2027","🌙 Ramazan Başlangıcı","Ramazan ayı başladı — mübarek olsun!","🌙"),
    ("05.03.2027","🌙 Kadir Gecesi","Bin aydan daha hayırlı gece","🌙"),
    ("10.03.2027","🎉 Ramazan Bayramı (1. Gün)","Ramazan Bayramı'nın ilk günü","🎉"),
    ("11.03.2027","🎉 Ramazan Bayramı (2. Gün)","Ramazan Bayramı'nın ikinci günü","🎉"),
    ("12.03.2027","🎉 Ramazan Bayramı (3. Gün)","Ramazan Bayramı'nın üçüncü günü","🎉"),
    ("16.05.2027","🕋 Arefe Günü","Hac ibadetinin en önemli günü","🕋"),
    ("17.05.2027","🐑 Kurban Bayramı (1. Gün)","Kurban Bayramı'nın ilk günü","🐑"),
    ("18.05.2027","🐑 Kurban Bayramı (2. Gün)","Kurban Bayramı'nın ikinci günü","🐑"),
    ("19.05.2027","🐑 Kurban Bayramı (3. Gün)","Kurban Bayramı'nın üçüncü günü","🐑"),
    ("20.05.2027","🐑 Kurban Bayramı (4. Gün)","Kurban Bayramı'nın dördüncü günü","🐑"),
    ("06.06.2027","🕌 Muharrem (Hicri Yılbaşı)","Hicri 1449 yılının başlangıcı","🕌"),
    ("16.06.2027","😔 Aşure Günü","Muharrem'in 10. günü","😔"),
    ("14.08.2027","🌟 Mevlid Kandili","Hz. Muhammed'in doğum gecesi","🌟"),
    # 2028
    ("31.12.2027","🌺 Regaib Kandili","İlk kandil gecesi","🌺"),
    ("25.01.2028","💫 Miraç Kandili","Hz. Muhammed'in miraca yükseldiği gece","💫"),
    ("09.02.2028","🌙 Berat Kandili","Günahların bağışlandığı mübarek gece","🌙"),
    ("28.01.2028","🌙 Ramazan Başlangıcı","Ramazan ayı başladı — mübarek olsun!","🌙"),
    ("23.02.2028","🌙 Kadir Gecesi","Bin aydan daha hayırlı gece","🌙"),
    ("27.02.2028","🎉 Ramazan Bayramı (1. Gün)","Ramazan Bayramı'nın ilk günü","🎉"),
    ("28.02.2028","🎉 Ramazan Bayramı (2. Gün)","Ramazan Bayramı'nın ikinci günü","🎉"),
    ("29.02.2028","🎉 Ramazan Bayramı (3. Gün)","Ramazan Bayramı'nın üçüncü günü","🎉"),
    ("04.05.2028","🕋 Arefe Günü","Hac ibadetinin en önemli günü","🕋"),
    ("05.05.2028","🐑 Kurban Bayramı (1. Gün)","Kurban Bayramı'nın ilk günü","🐑"),
    ("06.05.2028","🐑 Kurban Bayramı (2. Gün)","Kurban Bayramı'nın ikinci günü","🐑"),
    ("07.05.2028","🐑 Kurban Bayramı (3. Gün)","Kurban Bayramı'nın üçüncü günü","🐑"),
    ("08.05.2028","🐑 Kurban Bayramı (4. Gün)","Kurban Bayramı'nın dördüncü günü","🐑"),
    ("25.05.2028","🕌 Muharrem (Hicri Yılbaşı)","Hicri 1450 yılının başlangıcı","🕌"),
    ("04.06.2028","😔 Aşure Günü","Muharrem'in 10. günü","😔"),
    ("01.08.2028","🌟 Mevlid Kandili","Hz. Muhammed'in doğum gecesi","🌟"),
    # 2029
    ("07.01.2029","🌙 Ramazan Başlangıcı","Ramazan ayı başladı — mübarek olsun!","🌙"),
    ("06.02.2029","🎉 Ramazan Bayramı (1. Gün)","Ramazan Bayramı'nın ilk günü","🎉"),
    ("07.02.2029","🎉 Ramazan Bayramı (2. Gün)","Ramazan Bayramı'nın ikinci günü","🎉"),
    ("08.02.2029","🎉 Ramazan Bayramı (3. Gün)","Ramazan Bayramı'nın üçüncü günü","🎉"),
    ("23.04.2029","🕋 Arefe Günü","Hac ibadetinin en önemli günü","🕋"),
    ("24.04.2029","🐑 Kurban Bayramı (1. Gün)","Kurban Bayramı'nın ilk günü","🐑"),
    ("25.04.2029","🐑 Kurban Bayramı (2. Gün)","Kurban Bayramı'nın ikinci günü","🐑"),
    ("26.04.2029","🐑 Kurban Bayramı (3. Gün)","Kurban Bayramı'nın üçüncü günü","🐑"),
    ("27.04.2029","🐑 Kurban Bayramı (4. Gün)","Kurban Bayramı'nın dördüncü günü","🐑"),
    ("14.05.2029","🕌 Muharrem (Hicri Yılbaşı)","Hicri 1451 yılının başlangıcı","🕌"),
    ("22.07.2029","🌟 Mevlid Kandili","Hz. Muhammed'in doğum gecesi","🌟"),
    # 2030
    ("27.12.2029","🌙 Ramazan Başlangıcı","Ramazan ayı başladı — mübarek olsun!","🌙"),
    ("26.01.2030","🎉 Ramazan Bayramı (1. Gün)","Ramazan Bayramı'nın ilk günü","🎉"),
    ("27.01.2030","🎉 Ramazan Bayramı (2. Gün)","Ramazan Bayramı'nın ikinci günü","🎉"),
    ("28.01.2030","🎉 Ramazan Bayramı (3. Gün)","Ramazan Bayramı'nın üçüncü günü","🎉"),
    ("12.04.2030","🕋 Arefe Günü","Hac ibadetinin en önemli günü","🕋"),
    ("13.04.2030","🐑 Kurban Bayramı (1. Gün)","Kurban Bayramı'nın ilk günü","🐑"),
    ("14.04.2030","🐑 Kurban Bayramı (2. Gün)","Kurban Bayramı'nın ikinci günü","🐑"),
    ("15.04.2030","🐑 Kurban Bayramı (3. Gün)","Kurban Bayramı'nın üçüncü günü","🐑"),
    ("16.04.2030","🐑 Kurban Bayramı (4. Gün)","Kurban Bayramı'nın dördüncü günü","🐑"),
    ("03.05.2030","🕌 Muharrem (Hicri Yılbaşı)","Hicri 1452 yılının başlangıcı","🕌"),
    ("12.07.2030","🌟 Mevlid Kandili","Hz. Muhammed'in doğum gecesi","🌟"),
    # 2031
    ("16.12.2030","🌙 Ramazan Başlangıcı","Ramazan ayı başladı — mübarek olsun!","🌙"),
    ("14.01.2031","🎉 Ramazan Bayramı (1. Gün)","Ramazan Bayramı'nın ilk günü","🎉"),
    ("15.01.2031","🎉 Ramazan Bayramı (2. Gün)","Ramazan Bayramı'nın ikinci günü","🎉"),
    ("16.01.2031","🎉 Ramazan Bayramı (3. Gün)","Ramazan Bayramı'nın üçüncü günü","🎉"),
    ("01.04.2031","🕋 Arefe Günü","Hac ibadetinin en önemli günü","🕋"),
    ("02.04.2031","🐑 Kurban Bayramı (1. Gün)","Kurban Bayramı'nın ilk günü","🐑"),
    ("03.04.2031","🐑 Kurban Bayramı (2. Gün)","Kurban Bayramı'nın ikinci günü","🐑"),
    ("04.04.2031","🐑 Kurban Bayramı (3. Gün)","Kurban Bayramı'nın üçüncü günü","🐑"),
    ("05.04.2031","🐑 Kurban Bayramı (4. Gün)","Kurban Bayramı'nın dördüncü günü","🐑"),
    ("22.04.2031","🕌 Muharrem (Hicri Yılbaşı)","Hicri 1453 yılının başlangıcı","🕌"),
    ("02.07.2031","🌟 Mevlid Kandili","Hz. Muhammed'in doğum gecesi","🌟"),
    # 2032 - 2035
    ("06.12.2031","🌙 Ramazan Başlangıcı","Ramazan ayı başladı — mübarek olsun!","🌙"),
    ("04.01.2032","🎉 Ramazan Bayramı (1. Gün)","Ramazan Bayramı'nın ilk günü","🎉"),
    ("20.03.2032","🕋 Arefe Günü","Hac ibadetinin en önemli günü","🕋"),
    ("21.03.2032","🐑 Kurban Bayramı (1. Gün)","Kurban Bayramı'nın ilk günü","🐑"),
    ("11.04.2032","🕌 Muharrem (Hicri Yılbaşı)","Hicri 1454 yılının başlangıcı","🕌"),
    ("25.11.2032","🌙 Ramazan Başlangıcı","Ramazan ayı başladı — mübarek olsun!","🌙"),
    ("24.12.2032","🎉 Ramazan Bayramı (1. Gün)","Ramazan Bayramı'nın ilk günü","🎉"),
    ("09.03.2033","🕋 Arefe Günü","Hac ibadetinin en önemli günü","🕋"),
    ("10.03.2033","🐑 Kurban Bayramı (1. Gün)","Kurban Bayramı'nın ilk günü","🐑"),
    ("14.11.2033","🌙 Ramazan Başlangıcı","Ramazan ayı başladı — mübarek olsun!","🌙"),
    ("13.12.2033","🎉 Ramazan Bayramı (1. Gün)","Ramazan Bayramı'nın ilk günü","🎉"),
    ("26.02.2034","🕋 Arefe Günü","Hac ibadetinin en önemli günü","🕋"),
    ("27.02.2034","🐑 Kurban Bayramı (1. Gün)","Kurban Bayramı'nın ilk günü","🐑"),
    ("04.11.2034","🌙 Ramazan Başlangıcı","Ramazan ayı başladı — mübarek olsun!","🌙"),
    ("03.12.2034","🎉 Ramazan Bayramı (1. Gün)","Ramazan Bayramı'nın ilk günü","🎉"),
    ("16.02.2035","🕋 Arefe Günü","Hac ibadetinin en önemli günü","🕋"),
    ("17.02.2035","🐑 Kurban Bayramı (1. Gün)","Kurban Bayramı'nın ilk günü","🐑"),
    # 2036-2040
    ("25.10.2035","🌙 Ramazan Başlangıcı","Ramazan ayı başladı — mübarek olsun!","🌙"),
    ("23.11.2035","🎉 Ramazan Bayramı (1. Gün)","Ramazan Bayramı'nın ilk günü","🎉"),
    ("05.02.2036","🕋 Arefe Günü","Hac ibadetinin en önemli günü","🕋"),
    ("06.02.2036","🐑 Kurban Bayramı (1. Gün)","Kurban Bayramı'nın ilk günü","🐑"),
    ("14.10.2036","🌙 Ramazan Başlangıcı","Ramazan ayı başladı — mübarek olsun!","🌙"),
    ("12.11.2036","🎉 Ramazan Bayramı (1. Gün)","Ramazan Bayramı'nın ilk günü","🎉"),
    ("25.01.2037","🕋 Arefe Günü","Hac ibadetinin en önemli günü","🕋"),
    ("26.01.2037","🐑 Kurban Bayramı (1. Gün)","Kurban Bayramı'nın ilk günü","🐑"),
    ("03.10.2037","🌙 Ramazan Başlangıcı","Ramazan ayı başladı — mübarek olsun!","🌙"),
    ("01.11.2037","🎉 Ramazan Bayramı (1. Gün)","Ramazan Bayramı'nın ilk günü","🎉"),
    ("14.01.2038","🕋 Arefe Günü","Hac ibadetinin en önemli günü","🕋"),
    ("15.01.2038","🐑 Kurban Bayramı (1. Gün)","Kurban Bayramı'nın ilk günü","🐑"),
    ("22.09.2038","🌙 Ramazan Başlangıcı","Ramazan ayı başladı — mübarek olsun!","🌙"),
    ("21.10.2038","🎉 Ramazan Bayramı (1. Gün)","Ramazan Bayramı'nın ilk günü","🎉"),
    ("04.01.2039","🕋 Arefe Günü","Hac ibadetinin en önemli günü","🕋"),
    ("05.01.2039","🐑 Kurban Bayramı (1. Gün)","Kurban Bayramı'nın ilk günü","🐑"),
    ("11.09.2039","🌙 Ramazan Başlangıcı","Ramazan ayı başladı — mübarek olsun!","🌙"),
    ("10.10.2039","🎉 Ramazan Bayramı (1. Gün)","Ramazan Bayramı'nın ilk günü","🎉"),
    ("24.12.2039","🕋 Arefe Günü","Hac ibadetinin en önemli günü","🕋"),
    ("25.12.2039","🐑 Kurban Bayramı (1. Gün)","Kurban Bayramı'nın ilk günü","🐑"),
    # 2040-2050
    ("31.08.2040","🌙 Ramazan Başlangıcı","Ramazan ayı başladı — mübarek olsun!","🌙"),
    ("30.09.2040","🎉 Ramazan Bayramı (1. Gün)","Ramazan Bayramı'nın ilk günü","🎉"),
    ("12.12.2040","🕋 Arefe Günü","Hac ibadetinin en önemli günü","🕋"),
    ("13.12.2040","🐑 Kurban Bayramı (1. Gün)","Kurban Bayramı'nın ilk günü","🐑"),
    ("20.08.2041","🌙 Ramazan Başlangıcı","Ramazan ayı başladı — mübarek olsun!","🌙"),
    ("18.09.2041","🎉 Ramazan Bayramı (1. Gün)","Ramazan Bayramı'nın ilk günü","🎉"),
    ("01.12.2041","🕋 Arefe Günü","Hac ibadetinin en önemli günü","🕋"),
    ("02.12.2041","🐑 Kurban Bayramı (1. Gün)","Kurban Bayramı'nın ilk günü","🐑"),
    ("09.08.2042","🌙 Ramazan Başlangıcı","Ramazan ayı başladı — mübarek olsun!","🌙"),
    ("07.09.2042","🎉 Ramazan Bayramı (1. Gün)","Ramazan Bayramı'nın ilk günü","🎉"),
    ("20.11.2042","🕋 Arefe Günü","Hac ibadetinin en önemli günü","🕋"),
    ("21.11.2042","🐑 Kurban Bayramı (1. Gün)","Kurban Bayramı'nın ilk günü","🐑"),
    ("29.07.2043","🌙 Ramazan Başlangıcı","Ramazan ayı başladı — mübarek olsun!","🌙"),
    ("28.08.2043","🎉 Ramazan Bayramı (1. Gün)","Ramazan Bayramı'nın ilk günü","🎉"),
    ("09.11.2043","🕋 Arefe Günü","Hac ibadetinin en önemli günü","🕋"),
    ("10.11.2043","🐑 Kurban Bayramı (1. Gün)","Kurban Bayramı'nın ilk günü","🐑"),
    ("18.07.2044","🌙 Ramazan Başlangıcı","Ramazan ayı başladı — mübarek olsun!","🌙"),
    ("16.08.2044","🎉 Ramazan Bayramı (1. Gün)","Ramazan Bayramı'nın ilk günü","🎉"),
    ("29.10.2044","🕋 Arefe Günü","Hac ibadetinin en önemli günü","🕋"),
    ("30.10.2044","🐑 Kurban Bayramı (1. Gün)","Kurban Bayramı'nın ilk günü","🐑"),
    ("07.07.2045","🌙 Ramazan Başlangıcı","Ramazan ayı başladı — mübarek olsun!","🌙"),
    ("05.08.2045","🎉 Ramazan Bayramı (1. Gün)","Ramazan Bayramı'nın ilk günü","🎉"),
    ("19.10.2045","🕋 Arefe Günü","Hac ibadetinin en önemli günü","🕋"),
    ("20.10.2045","🐑 Kurban Bayramı (1. Gün)","Kurban Bayramı'nın ilk günü","🐑"),
    ("27.06.2046","🌙 Ramazan Başlangıcı","Ramazan ayı başladı — mübarek olsun!","🌙"),
    ("26.07.2046","🎉 Ramazan Bayramı (1. Gün)","Ramazan Bayramı'nın ilk günü","🎉"),
    ("08.10.2046","🕋 Arefe Günü","Hac ibadetinin en önemli günü","🕋"),
    ("09.10.2046","🐑 Kurban Bayramı (1. Gün)","Kurban Bayramı'nın ilk günü","🐑"),
    ("16.06.2047","🌙 Ramazan Başlangıcı","Ramazan ayı başladı — mübarek olsun!","🌙"),
    ("15.07.2047","🎉 Ramazan Bayramı (1. Gün)","Ramazan Bayramı'nın ilk günü","🎉"),
    ("27.09.2047","🕋 Arefe Günü","Hac ibadetinin en önemli günü","🕋"),
    ("28.09.2047","🐑 Kurban Bayramı (1. Gün)","Kurban Bayramı'nın ilk günü","🐑"),
    ("05.06.2048","🌙 Ramazan Başlangıcı","Ramazan ayı başladı — mübarek olsun!","🌙"),
    ("04.07.2048","🎉 Ramazan Bayramı (1. Gün)","Ramazan Bayramı'nın ilk günü","🎉"),
    ("16.09.2048","🕋 Arefe Günü","Hac ibadetinin en önemli günü","🕋"),
    ("17.09.2048","🐑 Kurban Bayramı (1. Gün)","Kurban Bayramı'nın ilk günü","🐑"),
    ("26.05.2049","🌙 Ramazan Başlangıcı","Ramazan ayı başladı — mübarek olsun!","🌙"),
    ("24.06.2049","🎉 Ramazan Bayramı (1. Gün)","Ramazan Bayramı'nın ilk günü","🎉"),
    ("06.09.2049","🕋 Arefe Günü","Hac ibadetinin en önemli günü","🕋"),
    ("07.09.2049","🐑 Kurban Bayramı (1. Gün)","Kurban Bayramı'nın ilk günü","🐑"),
    ("15.05.2050","🌙 Ramazan Başlangıcı","Ramazan ayı başladı — mübarek olsun!","🌙"),
    ("13.06.2050","🎉 Ramazan Bayramı (1. Gün)","Ramazan Bayramı'nın ilk günü","🎉"),
    ("26.08.2050","🕋 Arefe Günü","Hac ibadetinin en önemli günü","🕋"),
    ("27.08.2050","🐑 Kurban Bayramı (1. Gün)","Kurban Bayramı'nın ilk günü","🐑"),
]

def ozel_gunler_yil(yil):
    """Verilen yıla ait özel günleri döndürür"""
    return [g for g in OZEL_GUNLER if g[0].endswith(f".{yil}")]

def ozel_gunler_ay(yil, ay):
    """Verilen yıl ve aya ait özel günleri döndürür"""
    prefix = f".{ay:02d}.{yil}"
    return [g for g in OZEL_GUNLER if g[0][2:] == prefix[1:] or g[0][2:].startswith(f"{ay:02d}.{yil}")]

def ozel_gun_bugun():
    """Bugün veya yakında (7 gün içinde) olan özel günleri döndürür"""
    bugun = datetime.now().date()
    sonuc = []
    for tarih_str, isim, acik, emoji in OZEL_GUNLER:
        try:
            gun = datetime.strptime(tarih_str, "%d.%m.%Y").date()
            fark = (gun - bugun).days
            if -1 <= fark <= 7:
                sonuc.append((tarih_str, isim, acik, emoji, fark))
        except:
            pass
    return sonuc

def fmt_ozel_gunler_yil(yil):
    """Yıllık özel günler listesi mesajı"""
    gunler = ozel_gunler_yil(yil)
    if not gunler:
        return f"🗓️ *{yil} yılı için kayıtlı özel gün bulunamadı.*"
    bugun = datetime.now().date()
    msg = f"🌙 *{yil} İSLAMİ ÖZEL GÜNLER*\n━━━━━━━━━━━━━━━━━━\n\n"
    son_ay = ""
    for tarih_str, isim, acik, emoji in sorted(gunler, key=lambda x: datetime.strptime(x[0], "%d.%m.%Y")):
        try:
            gun = datetime.strptime(tarih_str, "%d.%m.%Y").date()
            ay_ismi = ["","Ocak","Şubat","Mart","Nisan","Mayıs","Haziran",
                       "Temmuz","Ağustos","Eylül","Ekim","Kasım","Aralık"][gun.month]
            if ay_ismi != son_ay:
                msg += f"\n📆 *{ay_ismi}*\n"
                son_ay = ay_ismi
            gecmis = "~~" if gun < bugun else ""
            msg += f"  {emoji} `{tarih_str}` — {isim}\n"
        except:
            pass
    msg += f"\n━━━━━━━━━━━━━━━━━━\n👤 @NikeCheatYeniden | 📢 @nikestoretr"
    return msg

def fmt_ozel_gunler_ay(yil, ay):
    """Aylık özel günler mesajı"""
    ay_ismi = ["","Ocak","Şubat","Mart","Nisan","Mayıs","Haziran",
               "Temmuz","Ağustos","Eylül","Ekim","Kasım","Aralık"][ay]
    # O aya ait günleri filtrele
    gunler = []
    for g in OZEL_GUNLER:
        try:
            d = datetime.strptime(g[0], "%d.%m.%Y")
            if d.year == yil and d.month == ay:
                gunler.append(g)
        except:
            pass
    if not gunler:
        return f"🗓️ *{ay_ismi} {yil}* — Bu ay için kayıtlı özel gün yok."
    bugun = datetime.now().date()
    msg = f"🌙 *{ay_ismi} {yil} — İSLAMİ ÖZEL GÜNLER*\n━━━━━━━━━━━━━━━━━━\n\n"
    for tarih_str, isim, acik, emoji in sorted(gunler, key=lambda x: datetime.strptime(x[0], "%d.%m.%Y")):
        gun = datetime.strptime(tarih_str, "%d.%m.%Y").date()
        fark = (gun - bugun).days
        if fark == 0:
            durum = "🟢 *BUGÜN!*"
        elif fark > 0:
            durum = f"⏳ {fark} gün sonra"
        else:
            durum = f"✅ {abs(fark)} gün önce geçti"
        msg += f"{emoji} *{isim}*\n  📅 `{tarih_str}` — {durum}\n  📝 _{acik}_\n\n"
    msg += f"━━━━━━━━━━━━━━━━━━\n👤 @NikeCheatYeniden | 📢 @nikestoretr"
    return msg

def uyari_dongu(dummy=None):
    # pytz opsiyonel — yoksa utc kullan
    try:
        import pytz
        HAS_PYTZ = True
    except ImportError:
        HAS_PYTZ = False
        print("[UYARI] pytz kurulu değil! pip install pytz — timezone hatası olabilir.")

    def now_for_tz(tz_str):
        """Verilen timezone için şu anki zamanı döndür."""
        if HAS_PYTZ and tz_str:
            try:
                tz = pytz.timezone(tz_str)
                return datetime.now(tz).replace(tzinfo=None)
            except Exception:
                pass
        return datetime.now()

    while True:
        try:
            now = datetime.now()
            bugun_str = now.strftime("%d-%m-%Y")
            bugun_key = now.strftime("%Y-%m-%d")

            # Günlük sayacı sıfırla
            if VERI.get("tarih") != bugun_key:
                VERI["bugun"] = 0
                VERI["tarih"] = bugun_key
                GNDR.clear()
                _VAKIT_CACHE.clear()
                veri_kaydet(VERI)

            # ── DM kullanıcıları — kişisel uyarılar
            for uid_str, kul in list(VERI["k"].items()):
                try:
                    if not kul.get("aktif", True): continue
                    if not kul.get("sehir"): continue
                    if is_banned(int(uid_str)): continue

                    lang = kul.get("lang", "tr") or "tr"
                    dk = int(kul.get("dk", 15))

                    cache = _VAKIT_CACHE.get(uid_str, {})
                    if cache.get("tarih") == bugun_str and cache.get("tm"):
                        tm = cache["tm"]
                    else:
                        tm = vakitler_al(kul)
                        if tm:
                            _VAKIT_CACHE[uid_str] = {"tarih": bugun_str, "tm": tm}
                        else:
                            continue

                    uid = int(uid_str)
                    if uid not in GNDR:
                        GNDR[uid] = {}

                    # Kullanıcının timezone'u ile şu anki zamanı al
                    tz_str = kul.get("_tz", "")
                    now_kul = now_for_tz(tz_str)
                    now_kul_bugun_str = now_kul.strftime("%d-%m-%Y")

                    for k in ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]:
                        sv = tm.get(k, "")
                        if not sv or sv == "--": continue
                        try:
                            sv_clean = sv.split(" ")[0].strip()
                            h, m = map(int, sv_clean.split(":")[:2])
                            dt_vakit = now_kul.replace(hour=h, minute=m, second=0, microsecond=0)
                            fark = (dt_vakit - now_kul).total_seconds() / 60
                            lk = f"{bugun_key}_{k}_{dk}"
                            if GNDR[uid].get(lk): continue
                            if dk - 1 < fark <= dk + 1:
                                ad = T(lang)["ad"].get(k, k)
                                mesaj = T(lang)["umsg"].format(
                                    s=kul.get("sehir") or "",
                                    i=kul.get("ilce") or (kul.get("sehir") or ""),
                                    v=ad, m=int(round(fark)), t=sv_clean
                                )
                                sonuc = tg_post("sendMessage", {
                                    "chat_id": uid, "text": mesaj,
                                    "parse_mode": "Markdown",
                                    "reply_markup": haftalik_alt_kb()
                                })
                                if sonuc.get("ok"):
                                    GNDR[uid][lk] = True
                                    VERI["bugun"] = VERI.get("bugun", 0) + 1
                                    VERI["toplam"] = VERI.get("toplam", 0) + 1
                                    veri_kaydet(VERI)
                                    print(f"[UYARI ✅] {kul.get('isim','?')} — {ad} {sv_clean} (fark:{fark:.1f}dk, dk={dk})")
                                    log_ekle("EZAN_UYARISI", uid, kul.get("isim","?"),
                                             f"{kul.get('sehir','')} — {ad} ({sv_clean})")
                                else:
                                    print(f"[UYARI ❌ GÖNDERELEMEDI] uid={uid} {k} {sv_clean} — {sonuc}")
                        except Exception as e:
                            print(f"[DM VAKIT HATA] uid={uid_str} {k}: {e}")
                except Exception as e:
                    print(f"[DM KUL HATA] uid={uid_str}: {e}")

            # ── GRUPLAR — grup ezan bildirimleri
            for grp_str, g in list(VERI.get("gruplar", {}).items()):
                try:
                    if not g.get("aktif"): continue
                    if not g.get("sehir"): continue
                    aktif_vakitler = g.get("aktif_vakitler", [])
                    if not aktif_vakitler: continue

                    dk = int(g.get("dk", 0))  # 0 = vakitte bildirim

                    gcache = _VAKIT_CACHE.get(f"grp_{grp_str}", {})
                    if gcache.get("tarih") == bugun_str and gcache.get("tm"):
                        tm = gcache["tm"]
                    else:
                        tm = vakitler_al(g)
                        if tm:
                            _VAKIT_CACHE[f"grp_{grp_str}"] = {"tarih": bugun_str, "tm": tm}
                        else:
                            continue

                    grp_id = int(grp_str)
                    if grp_id not in GNDR:
                        GNDR[grp_id] = {}

                    sehir = g.get("sehir", "")
                    ilce  = g.get("ilce") or sehir

                    # Grubun timezone'u ile şu anki zamanı al
                    tz_str = g.get("_tz", "")
                    now_grp = now_for_tz(tz_str)

                    for k in aktif_vakitler:
                        sv = tm.get(k, "")
                        if not sv or sv == "--": continue
                        try:
                            sv_clean = sv.split(" ")[0].strip()
                            h, m2 = map(int, sv_clean.split(":")[:2])
                            dt_vakit = now_grp.replace(hour=h, minute=m2, second=0, microsecond=0)
                            fark = (dt_vakit - now_grp).total_seconds() / 60
                            lk = f"grp_{bugun_key}_{k}_{dk}"
                            if GNDR[grp_id].get(lk): continue

                            # dk=0 → vakitte (fark -1 ile +1 arası)
                            if dk == 0:
                                tetik = -1 < fark <= 1
                            else:
                                tetik = dk - 1 < fark <= dk + 1

                            if tetik:
                                # ── Saat aralığı kontrolü
                                acilis_str = g.get("bildirim_acilis", "00:00")
                                kapanis_str = g.get("bildirim_kapanis", "23:59")
                                try:
                                    ah, am = map(int, acilis_str.split(":"))
                                    kh, km = map(int, kapanis_str.split(":"))
                                    now_dk = now_grp.hour * 60 + now_grp.minute
                                    ac_dk  = ah * 60 + am
                                    kp_dk  = kh * 60 + km
                                    if not (ac_dk <= now_dk <= kp_dk):
                                        continue  # saat aralığı dışında
                                except:
                                    pass

                                emoji, vakit_isim = VAKIT_ISIM.get(k, ("🕌", k))

                                # ── Özel İFTAR bildirimi (Maghrib vakti)
                                if k == "Maghrib":
                                    if dk == 0:
                                        mesaj = (
                                            f"🌙 *İFTAR VAKTİ GELDİ!*\n"
                                            f"━━━━━━━━━━━━━━━━━━\n"
                                            f"📍 *{sehir}* İftar vakti: `{sv_clean}`\n"
                                            f"━━━━━━━━━━━━━━━━━━\n"
                                            f"🤲 *Hayırlı iftarlar! Allah oruçlarınızı kabul etsin.*\n"
                                            f"👤 @NikeCheatYeniden | 📢 @nikestoretr"
                                        )
                                    else:
                                        mesaj = (
                                            f"🌙 *İFTAR VAKTİNE {dk} DAKİKA KALDI!*\n"
                                            f"━━━━━━━━━━━━━━━━━━\n"
                                            f"📍 *{sehir}* İftar saati: `{sv_clean}`\n"
                                            f"⏳ Kalan süre: *{dk} dakika*\n"
                                            f"━━━━━━━━━━━━━━━━━━\n"
                                            f"🤲 İftar hazırlıklarınızı yapın!\n"
                                            f"👤 @NikeCheatYeniden | 📢 @nikestoretr"
                                        )
                                else:
                                    if dk == 0:
                                        bildirim_metni = f"vakti geldi! 🕐 `{sv_clean}`"
                                    else:
                                        bildirim_metni = f"vaktine *{dk} dakika* kaldı! 🕐 `{sv_clean}`"
                                    mesaj = (
                                        f"{emoji} *{vakit_isim.upper()} VAKTİ*\n"
                                        f"━━━━━━━━━━━━━━━━━━\n"
                                        f"📍 *{sehir}* — {vakit_isim} {bildirim_metni}\n"
                                        f"━━━━━━━━━━━━━━━━━━\n"
                                        f"🤲 Hayırlı namazlar!\n"
                                        f"👤 @NikeCheatYeniden | 📢 @nikestoretr"
                                    )
                                sonuc = tg_post("sendMessage", {
                                    "chat_id": grp_id, "text": mesaj,
                                    "parse_mode": "Markdown"
                                })
                                if sonuc.get("ok"):
                                    GNDR[grp_id][lk] = True
                                    print(f"[GRUP UYARI ✅] {grp_str} {sehir} — {vakit_isim} {sv_clean} (fark:{fark:.1f}dk, dk={dk})")
                                    log_ekle("GRUP_EZAN", grp_id, sehir,
                                             f"{vakit_isim} ({sv_clean})")
                                else:
                                    print(f"[GRUP UYARI ❌] {grp_str} {k} — {sonuc}")
                        except Exception as e:
                            print(f"[GRUP VAKIT HATA] {grp_str} {k}: {e}")
                except Exception as e:
                    print(f"[GRUP HATA] {grp_str}: {e}")

        except Exception as e:
            import traceback
            print(f"[UYARI_DONGU HATA] {e}")
            traceback.print_exc()
        time.sleep(30)

# ═══════════════════════════════════════════════
#  SPAM KORUMASI
# ═══════════════════════════════════════════════
def spam_kontrol(uid):
    """(is_spam, kalan_sn) döndürür."""
    if uid in ADMIN_IDS:
        return False, 0
    now = time.time()
    son = SPAM_CACHE.get(uid, 0)
    kalan = SPAM_SURE - (now - son)
    if kalan > 0:
        return True, max(1, int(kalan))
    SPAM_CACHE[uid] = now
    return False, 0

# ═══════════════════════════════════════════════
#  MESAJ İŞLEYİCİ
# ═══════════════════════════════════════════════
def isle_mesaj(msg):
    global LOG_KANAL
    if not msg:
        return
    chat_id = msg["chat"]["id"]
    chat_type = msg["chat"].get("type", "private")  # private / group / supergroup / channel
    is_dm = chat_type == "private"
    text = msg.get("text", "") or ""
    frm = msg.get("from", {})
    uid = frm.get("id", 0)
    isim = str(frm.get("first_name") or "")
    uname = str(frm.get("username") or "")
    kul = kul_al(VERI, uid)
    kul["isim"] = isim
    kul["username"] = uname
    lang = kul.get("lang", "tr") or "tr"
    t = T(lang)

    # Gruba eklenme
    if "new_chat_members" in msg:
        for u in msg["new_chat_members"]:
            if str(u["id"]) == BOT_TOKEN.split(":")[0]:
                send(chat_id, t.get("grup", M["tr"]["grup"]), parse_mode="Markdown")
                log_ekle("GRUBA_EKLENDI", uid, isim, msg["chat"].get("title", ""))
        return

    if not text.startswith("/"):
        return

    cmd = text.split()[0].lower().split("@")[0]

    # Ban kontrolü (admin komutları hariç)
    admin_cmds = ("/bk", "/kb", "/km", "/ku", "/log", "/logayarla", "/admin", "/adminpanel", "/duyuru")
    if cmd not in admin_cmds and is_banned(uid):
        send(chat_id, t.get("ban", "🚫 Erişiminiz kısıtlanmış."))
        return

    # Spam kontrolü — /start muaf, diğer komutlara 5 sn bekleme
    is_spam, kalan_sn = (False, 0) if cmd == "/start" else spam_kontrol(uid)
    if is_spam:
        if not SPAM_CACHE.get(f"warned_{uid}"):
            SPAM_CACHE[f"warned_{uid}"] = True
            sure_emoji = "🔴" if kalan_sn >= 4 else ("🟡" if kalan_sn >= 2 else "🟢")
            spam_mesaj = t.get("spam", M["tr"]["spam"]).format(emoji=sure_emoji, sn=kalan_sn)
            send(chat_id, spam_mesaj)
        return
    SPAM_CACHE.pop(f"warned_{uid}", None)

    # ── /start
    if cmd == "/start":
        veri_kaydet(VERI)
        log_ekle("START", uid, isim, (kul.get("sehir") or "") + "/" + (kul.get("ilce") or ""))
        # İlk kez → çok dilli dil seçimi
        if not kul.get("lang"):
            logo_send(chat_id, HOSGELDIN_MULTI, dil_kb())
            return
        # Dil var ama konum yok → konuma yönlendir
        if not kul.get("sehir"):
            logo_send(chat_id, t["ulke"], ulke_kb(0, lang))
            return
        # Her şey ayarlı → ana menü (önce foto, olmezsa text)
        caption = t["menu_bilgi"].format(s=kul.get("sehir") or "--", i=kul.get("ilce") or "--")
        logo_send(chat_id, caption, menu_kb(lang))

    # ── /vakitler
    elif cmd == "/vakitler":
        if not kul.get("sehir"):
            logo_send(chat_id, t["yok"])
            return
        tm = vakitler_al(kul)
        if tm:
            logo_send(chat_id, fmt(tm, kul), haftalik_alt_kb())
        else:
            logo_send(chat_id, t["hata_api"])
        log_ekle("VAKITLER", uid, isim, kul.get("sehir") or "")

    # ── /yarin
    elif cmd == "/yarin":
        if not kul.get("sehir"):
            logo_send(chat_id, t["yok"])
            return
        yarin = (datetime.now() + timedelta(days=1)).strftime("%d-%m-%Y")
        etiket = (datetime.now() + timedelta(days=1)).strftime("%d.%m.%Y")
        tm = vakitler_al(kul, tarih=yarin)
        if tm:
            logo_send(chat_id, fmt(tm, kul, etiket), haftalik_alt_kb())
        else:
            logo_send(chat_id, t["hata_api"])
        log_ekle("YARIN", uid, isim, kul.get("sehir") or "")

    # ── /haftalik
    elif cmd == "/haftalik":
        if not kul.get("sehir"):
            send(chat_id, t["yok"])
            return
        s = [f"📆 *{kul.get('sehir','')} / {kul.get('ilce','')} HAFTALIK*\n━━━━━━━━━━━━━━━━━━"]
        for i in range(7):
            gun = datetime.now() + timedelta(days=i)
            tm = vakitler_al(kul, tarih=gun.strftime("%d-%m-%Y"))
            if tm:
                s.append(f"\n📅 *{gun.strftime('%d.%m %A')}*\n"
                         f"🌙`{tm.get('Fajr','--')}` "
                         f"🌤️`{tm.get('Dhuhr','--')}` "
                         f"🌇`{tm.get('Asr','--')}` "
                         f"🌆`{tm.get('Maghrib','--')}` "
                         f"🌃`{tm.get('Isha','--')}`")
        s.append("\n🤲 @NikeCheatYeniden | 📢 @nikestoretr")
        logo_send(chat_id, "\n".join(s), haftalik_alt_kb())
        log_ekle("HAFTALIK", uid, isim, kul.get("sehir") or "")

    # ── /konum
    elif cmd == "/konum":
        logo_send(chat_id, t["ulke"], ulke_kb(0, lang))
        log_ekle("KONUM", uid, isim, "")

    # ── /uyari
    elif cmd == "/uyari":
        logo_send(chat_id, t["usor"], uyari_kb())
        log_ekle("UYARI_KMT", uid, isim, "")

    # ── /api
    elif cmd == "/api":
        logo_send(chat_id, t["apisor"], api_kb())
        log_ekle("API_KMT", uid, isim, "")

    # ── /dil
    elif cmd == "/dil":
        logo_send(chat_id, HOSGELDIN_MULTI, dil_kb())
        log_ekle("DİL", uid, isim, "")

    # ── /ayarlar
    elif cmd == "/ayarlar":
        logo_send(chat_id, t["ayar"].format(
            u=kul.get("ulke_label") or "--", s=kul.get("sehir") or "--",
            i=kul.get("ilce") or "--", m=kul.get("dk", 15),
            a=kul.get("api", "auto").upper()
        ))
        log_ekle("AYARLAR", uid, isim, "")

    # ── /durdur
    elif cmd == "/durdur":
        kul["aktif"] = False
        veri_kaydet(VERI)
        logo_send(chat_id, t["dur"])
        log_ekle("DURDUR", uid, isim, "")

    # ── /devam
    elif cmd == "/devam":
        kul["aktif"] = True
        veri_kaydet(VERI)
        logo_send(chat_id, t["dev"])
        log_ekle("DEVAM", uid, isim, "")

    # ── /yardim
    elif cmd in ("/yardim", "/help"):
        logo_send(chat_id, t["yard"])
        log_ekle("YARDIM", uid, isim, "")

    # ── /hakkinda
    elif cmd == "/hakkinda":
        logo_send(chat_id, t["hak"])
        log_ekle("HAKKINDA", uid, isim, "")

    # ── /ozelgunler
    elif cmd in ("/ozelgunler", "/ozelgun"):
        yil = datetime.now().year
        yakin = ozel_gun_bugun()
        msg = "🌙 *İSLAMİ ÖZEL GÜNLER*\n━━━━━━━━━━━━━━━━━━\n"
        if yakin:
            msg += "\n⭐ *YAKIN / BUGÜN:*\n"
            for tarih_str, isim_g, acik, emoji, fark in yakin:
                if fark == 0:
                    msg += f"{emoji} *{isim_g}* — 🟢 *BUGÜN!*\n"
                elif fark > 0:
                    msg += f"{emoji} *{isim_g}* — ⏳ {fark} gün sonra\n"
            msg += "\n━━━━━━━━━━━━━━━━━━\n"
        msg += f"\n📅 Yıl ve ay seçin:"
        send(chat_id, msg, ozel_gun_kb(yil))
        log_ekle("OZEL_GUNLER", uid, isim, "")

    # ── /istatistik
    elif cmd == "/istatistik":
        toplam = len(VERI["k"])
        aktif = sum(1 for u in VERI["k"].values() if u.get("aktif") and u.get("sehir"))
        logo_send(chat_id, t["stat"].format(
            t=toplam, a=aktif, b=VERI.get("bugun", 0), top=VERI.get("toplam", 0)
        ))
        log_ekle("İSTATİSTİK", uid, isim, "")

    # ══════════════════════════════
    #  ADMİN KOMUTLARI
    # ══════════════════════════════

    # ── /admin / /adminpanel
    elif cmd in ("/admin", "/adminpanel"):
        if not admin_ok(uid):
            send(chat_id, "❌ Bu komut sadece adminlere aittir.")
            return
        log_ekle("ADMIN", uid, isim, "")
        send(chat_id, admin_panel(), admin_kb())

    # ── /duyuru
    elif cmd == "/duyuru":
        if not admin_ok(uid):
            return
        mt = text[8:].strip()
        if not mt:
            send(chat_id, "ℹ️ Kullanım: `/duyuru <mesaj>`")
            return
        say = 0
        for uid_str in list(VERI["k"].keys()):
            try:
                tg_post("sendMessage", {"chat_id": int(uid_str), "text": f"📢 *DUYURU*\n━━━━━━━━━━━━━━━━━━\n{mt}", "parse_mode": "Markdown"})
                say += 1
            except:
                pass
        send(chat_id, f"✅ {say} kişiye gönderildi.")
        log_ekle("DUYURU", uid, isim, mt[:50])

    # ── /kban — kullanıcı banla
    elif cmd in ("/bk", "/kban"):
        if not admin_ok(uid):
            send(chat_id, "❌ Bu komut sadece adminlere aittir.")
            return
        parts = text.split()
        hedef_uid = None
        # Yanıt ile veya UID ile
        if msg.get("reply_to_message"):
            hedef_uid = msg["reply_to_message"]["from"]["id"]
        elif len(parts) >= 2:
            try:
                hedef_uid = int(parts[1])
            except:
                send(chat_id, "❌ Geçersiz kullanıcı ID!\nKullanım: `/kban <uid>` veya mesaja yanıt ver.")
                return
        if not hedef_uid:
            send(chat_id, "❌ Kullanıcı belirtilmedi!\nKullanım: `/kban <uid>` veya mesaja yanıt ver.")
            return
        if not VERI.get("ban"):
            VERI["ban"] = {}
        VERI["ban"][str(hedef_uid)] = {"banned": True, "mute_until": None}
        veri_kaydet(VERI)
        hedef_isim = VERI["k"].get(str(hedef_uid), {}).get("isim", str(hedef_uid))
        send(chat_id, f"🚫 *{hedef_isim}* (`{hedef_uid}`) *BANLANDI!*\n\n• /kb ile kaldırabilirsiniz.")
        log_ekle("BAN", uid, isim, f"{hedef_isim}({hedef_uid})")
        tg_post("sendMessage", {"chat_id": hedef_uid, "text": "🚫 *Bot erişiminiz kısıtlandı.*", "parse_mode": "Markdown"})

    # ── /uban — ban kaldır
    elif cmd in ("/kb", "/uban"):
        if not admin_ok(uid):
            send(chat_id, "❌ Bu komut sadece adminlere aittir.")
            return
        parts = text.split()
        hedef_uid = None
        if msg.get("reply_to_message"):
            hedef_uid = msg["reply_to_message"]["from"]["id"]
        elif len(parts) >= 2:
            try:
                hedef_uid = int(parts[1])
            except:
                send(chat_id, "❌ Geçersiz kullanıcı ID!")
                return
        if not hedef_uid:
            send(chat_id, "❌ Kullanıcı belirtilmedi!")
            return
        if VERI.get("ban", {}).get(str(hedef_uid)):
            VERI["ban"][str(hedef_uid)] = {"banned": False, "mute_until": None}
            veri_kaydet(VERI)
        hedef_isim = VERI["k"].get(str(hedef_uid), {}).get("isim", str(hedef_uid))
        send(chat_id, f"✅ *{hedef_isim}* (`{hedef_uid}`) *BAN KALDIRILDI!*")
        log_ekle("UBAN", uid, isim, f"{hedef_isim}({hedef_uid})")
        tg_post("sendMessage", {"chat_id": hedef_uid, "text": "✅ *Bot erişiminiz tekrar açıldı.*", "parse_mode": "Markdown"})

    # ── /km — süreli ban (saniye cinsinden, 0=sınırsız)
    elif cmd in ("/km", "/mute"):
        if not admin_ok(uid):
            send(chat_id, "❌ Bu komut sadece adminlere aittir.")
            return
        parts = text.split()
        hedef_uid = None
        sure_sn = 3600  # varsayılan 1 saat (saniye)
        if msg.get("reply_to_message"):
            hedef_uid = msg["reply_to_message"]["from"]["id"]
            if len(parts) >= 2:
                try:
                    sure_sn = int(parts[1])
                except:
                    pass
        elif len(parts) >= 2:
            try:
                hedef_uid = int(parts[1])
            except:
                send(chat_id, "❌ Kullanım: `/mute <uid> [saniye]` veya mesaja yanıt ver.\n\n💡 0 = Sınırsız mute")
                return
            if len(parts) >= 3:
                try:
                    sure_sn = int(parts[2])
                except:
                    pass
        if not hedef_uid:
            send(chat_id, "❌ Kullanıcı belirtilmedi!\n\n💡 Kullanım: `/mute <uid> [saniye]`\n• 0 saniye = sınırsız")
            return
        if not VERI.get("ban"):
            VERI["ban"] = {}
        if sure_sn == 0:
            # Sınırsız mute
            VERI["ban"][str(hedef_uid)] = {"banned": False, "mute_until": 9999999999}
            hedef_isim = VERI["k"].get(str(hedef_uid), {}).get("isim", str(hedef_uid))
            send(chat_id, f"🔇 *{hedef_isim}* (`{hedef_uid}`) *SINIRSİZ susturuldu!*\n\n• /ku ile kaldırılabilir.")
            log_ekle("MUTE", uid, isim, f"{hedef_isim}({hedef_uid}) sınırsız")
            tg_post("sendMessage", {"chat_id": hedef_uid, "text": "🔇 *Sınırsız süreyle erişiminiz kısıtlandı.*", "parse_mode": "Markdown"})
        else:
            bitis = datetime.now() + timedelta(seconds=sure_sn)
            VERI["ban"][str(hedef_uid)] = {"banned": False, "mute_until": bitis.timestamp()}
            veri_kaydet(VERI)
            hedef_isim = VERI["k"].get(str(hedef_uid), {}).get("isim", str(hedef_uid))
            bitis_str = bitis.strftime("%d.%m.%Y %H:%M:%S")
            sure_label = f"{sure_sn} saniye" if sure_sn < 60 else f"{sure_sn//60} dakika {sure_sn%60} saniye" if sure_sn < 3600 else f"{sure_sn//3600} saat"
            send(chat_id, f"🔇 *{hedef_isim}* (`{hedef_uid}`) *{sure_label} susturuldu!*\n📅 Bitiş: `{bitis_str}`")
            log_ekle("MUTE", uid, isim, f"{hedef_isim}({hedef_uid}) {sure_sn}sn")
            tg_post("sendMessage", {
                "chat_id": hedef_uid,
                "text": f"🔇 *{sure_label} süreyle erişiminiz kısıtlandı.*\n📅 Bitiş: `{bitis_str}`",
                "parse_mode": "Markdown"
            })

    # ── /ku — susturma kaldır
    elif cmd in ("/ku", "/umute"):
        if not admin_ok(uid):
            send(chat_id, "❌ Bu komut sadece adminlere aittir.")
            return
        parts = text.split()
        hedef_uid = None
        if msg.get("reply_to_message"):
            hedef_uid = msg["reply_to_message"]["from"]["id"]
        elif len(parts) >= 2:
            try:
                hedef_uid = int(parts[1])
            except:
                send(chat_id, "❌ Geçersiz kullanıcı ID!")
                return
        if not hedef_uid:
            send(chat_id, "❌ Kullanıcı belirtilmedi!")
            return
        if VERI.get("ban", {}).get(str(hedef_uid)):
            VERI["ban"][str(hedef_uid)]["mute_until"] = None
            veri_kaydet(VERI)
        hedef_isim = VERI["k"].get(str(hedef_uid), {}).get("isim", str(hedef_uid))
        send(chat_id, f"🔊 *{hedef_isim}* (`{hedef_uid}`) *susturma kaldırıldı!*")
        log_ekle("UMUTE", uid, isim, f"{hedef_isim}({hedef_uid})")
        tg_post("sendMessage", {"chat_id": hedef_uid, "text": "🔊 *Susturmanız kaldırıldı.*", "parse_mode": "Markdown"})

    # ── /log — log kanalını ayarla (@kanal ile)
    elif cmd in ("/logayarla", "/log"):
        if not admin_ok(uid):
            send(chat_id, "❌ Bu komut sadece adminlere aittir.")
            return
        parts = text.split()
        if len(parts) < 2:
            mevcut = str(LOG_KANAL) if LOG_KANAL else "Ayarlanmamış"
            send(chat_id, (
                f"ℹ️ *LOG KANALI AYARLA*\n━━━━━━━━━━━━━━━━━━\n"
                f"📋 Mevcut kanal: `{mevcut}`\n\n"
                f"• `/log @kanaladi` — @ ile kanal\n"
                f"• `/log -100123456789` — ID ile kanal\n\n"
                f"📌 Bot o kanala *admin* olmalı ve *mesaj gönderme* yetkisi olmalı!"
            ))
            return
        kanal = parts[1]
        try:
            kanal_id = int(kanal)
        except:
            kanal_id = kanal
        LOG_KANAL = kanal_id
        VERI["log_kanal"] = kanal_id
        veri_kaydet(VERI)
        send(chat_id, f"✅ Log kanalı `{kanal_id}` olarak ayarlandı!\n\n🔔 Artık tüm komutlar ve olaylar bu kanala iletilecek.")
        log_ekle("LOG_AYARLA", uid, isim, str(kanal_id))
        tg_post("sendMessage", {
            "chat_id": kanal_id,
            "text": (
                f"✅ *LOG KANALI AKTİF!*\n━━━━━━━━━━━━━━━━━━\n"
                f"🕌 Ezan Vakti Botu log kanalı ayarlandı.\n"
                f"📝 Tüm komutlar burada görünecek.\n"
                f"⚙️ Admin: {isim} (`{uid}`)"
            ),
            "parse_mode": "Markdown"
        })

    # ── /grubayarla — Grup ezan bildirimi ayarla (sadece grup adminleri)
    elif cmd == "/grubayarla":
        if is_dm:
            send(chat_id, "❌ Bu komut sadece gruplarda kullanılır!")
            return
        # Grup admin kontrolü
        try:
            cm = tg_get("getChatMember", {"chat_id": chat_id, "user_id": uid})
            rol = cm.get("result", {}).get("status", "")
            if rol not in ("creator", "administrator") and uid not in ADMIN_IDS:
                send(chat_id, "❌ Bu komutu sadece grup adminleri kullanabilir.")
                return
        except:
            pass
        send(chat_id, (
            f"⚙️ *GRUP EZAN BİLDİRİMİ AYARLA*\n━━━━━━━━━━━━━━━━━━\n\n"
            f"📍 Mevcut konum: *{VERI.get('gruplar',{}).get(str(chat_id),{}).get('sehir','Ayarlanmamış')}*\n\n"
            f"Aşağıdan vakit bildirimi ayarlarını yapın:"
        ), grup_ayar_kb(chat_id))

    # ── Bilinmeyen komut — SADECE DM'de bildir
    else:
        if is_dm:
            mesaj = t.get("bilinmeyen", M["tr"]["bilinmeyen"]).format(cmd=cmd)
            send(chat_id, mesaj)

# ═══════════════════════════════════════════════
#  CALLBACK İŞLEYİCİ
# ═══════════════════════════════════════════════
def isle_callback(cq):
    global LOG_KANAL
    if not cq:
        return
    cq_id = cq["id"]
    chat_id = cq["message"]["chat"]["id"]
    msg_id = cq["message"]["message_id"]
    uid = cq["from"]["id"]
    isim = cq["from"].get("first_name", "") or ""
    d = cq.get("data", "")
    kul = kul_al(VERI, uid)
    kul["isim"] = isim
    lang = kul.get("lang", "tr") or "tr"
    t = T(lang)

    tg_post("answerCallbackQuery", {"callback_query_id": cq_id})

    if is_banned(uid):
        return

    def upd(text, kb=None):
        r = edit(chat_id, msg_id, text, kb)
        if not (r and r.get("ok")):
            edit_caption(chat_id, msg_id, text, kb)
    def rep(text, kb=None): send(chat_id, text, kb)

    if d in ("US_X", "SS_X"):
        return

    # Dil seçimi
    if d.startswith("L_"):
        secim = d[2:]
        if secim not in M:
            return
        kul["lang"] = secim
        veri_kaydet(VERI)
        lang = secim
        t = T(lang)
        upd(t["dil_ok"])
        # Dil seçildi → ülke seçimine geç
        rep(t["ulke"], ulke_kb(0, lang))
        log_ekle("DIL", uid, isim, secim)

    # Ülke sayfa
    elif d.startswith("US_"):
        upd(t["ulke"], ulke_kb(int(d[3:]), lang))

    # Ülke seçimi
    elif d.startswith("U_"):
        ulke_label = d[2:]
        if ulke_label not in ULKELER:
            return
        kod, onerik_lang = ULKELER[ulke_label]
        kul["ulke_label"] = ulke_label
        kul["ulke_kod"] = kod
        kul["sehir"] = None
        kul["ilce"] = None
        kul["lat"] = None
        kul["lon"] = None
        veri_kaydet(VERI)
        log_ekle("ULKE", uid, isim, ulke_label)
        if kod in SEHIR_KOORDINAT and SEHIR_KOORDINAT[kod]:
            upd(t["il"], sehir_kb(kod, 0, lang))
        else:
            upd("❌ Bu ülke için şehir listesi yakında eklenecek.", menu_kb(lang))

    # Şehir sayfa
    elif d.startswith("SS_"):
        kod = kul.get("ulke_kod", "TR")
        upd(t["il"], sehir_kb(kod, int(d[3:]), lang))

    # Şehir seçimi
    elif d.startswith("S_"):
        sehir = d[2:]
        kod = kul.get("ulke_kod", "TR")
        veri = SEHIR_KOORDINAT.get(kod, {})
        if sehir not in veri:
            return
        lat, lon, sehir_en = veri[sehir]
        kul["sehir"] = sehir
        kul["sehir_en"] = sehir_en
        kul["lat"] = lat
        kul["lon"] = lon
        kul["ilce"] = sehir
        kul["ilce_en"] = sehir_en
        veri_kaydet(VERI)
        log_ekle("SEHIR", uid, isim, sehir)
        # İlçe var mı?
        ilceler = get_ilce_listesi(sehir)
        if ilceler:
            upd(t["ilce"].format(s=sehir), ilce_kb(sehir, 0, kod, lang))
        else:
            msg_ok = t["konum_ok"].format(u=kul.get("ulke_label", ""), s=sehir, i=sehir)
            msg_yok = t.get("ilce_yok", M["tr"]["ilce_yok"]).format(s=sehir)
            upd(msg_ok, menu_kb(lang))
            rep(msg_yok)

    # İlçe sayfa
    elif d.startswith("IS_"):
        p = d[3:].rsplit("_", 1)
        if len(p) == 2:
            sh, sayfa = p[0], int(p[1])
            kod = kul.get("ulke_kod", "TR")
            upd(t["ilce"].format(s=sh), ilce_kb(sh, sayfa, kod, lang))

    # Şehire geri dön
    elif d.startswith("SB_"):
        kod = d[3:] or kul.get("ulke_kod", "TR")
        upd(t["il"], sehir_kb(kod, 0, lang))

    # İlçe seçimi
    elif d.startswith("I_"):
        ilce = d[2:]
        sehir = kul.get("sehir") or ""
        koord = get_ilce_koord(sehir, ilce)
        kul["ilce"] = ilce
        kul["ilce_en"] = ilce
        if koord:
            kul["lat"] = koord[0]
            kul["lon"] = koord[1]
        veri_kaydet(VERI)
        log_ekle("ILCE", uid, isim, (sehir or "") + "/" + (ilce or ""))
        kod = kul.get("ulke_kod", "TR")
        msg_ok = t["konum_ok"].format(u=kul.get("ulke_label", ""), s=sehir, i=ilce)
        upd(msg_ok, menu_kb(lang))

    # Uyarı dk
    elif d.startswith("A_"):
        dk = int(d[2:])
        kul["dk"] = dk
        veri_kaydet(VERI)
        upd(t["uok"].format(m=dk), menu_kb(lang))
        log_ekle("UYARI", uid, isim, f"{dk}dk")

    # API
    elif d.startswith("P_"):
        api = d[2:]
        kul["api"] = api
        veri_kaydet(VERI)
        upd(t["apiok"].format(a=api.upper()), menu_kb(lang))
        log_ekle("API", uid, isim, api)

    # Ana Menü
    elif d == "M_menu":
        upd(t["menu_bilgi"].format(s=kul.get("sehir") or "--", i=kul.get("ilce") or "--"), menu_kb(lang))

    # Vakitler
    elif d == "M_v":
        if not kul.get("sehir"):
            upd(t["yok"])
            return
        tm = vakitler_al(kul)
        upd(fmt(tm, kul) if tm else t["hata_api"], haftalik_alt_kb())
        log_ekle("VAKITLER_CB", uid, isim, kul.get("sehir") or "")

    # Yarın
    elif d == "M_y":
        if not kul.get("sehir"):
            upd(t["yok"])
            return
        yarin = (datetime.now() + timedelta(days=1)).strftime("%d-%m-%Y")
        etiket = (datetime.now() + timedelta(days=1)).strftime("%d.%m.%Y")
        tm = vakitler_al(kul, tarih=yarin)
        upd(fmt(tm, kul, etiket) if tm else t["hata_api"], haftalik_alt_kb())
        log_ekle("YARIN_CB", uid, isim, kul.get("sehir") or "")

    # Haftalık
    elif d == "M_h7":
        if not kul.get("sehir"):
            upd(t["yok"])
            return
        s = [f"📆 *{kul.get('sehir','')} / {kul.get('ilce','')} HAFTALIK*\n━━━━━━━━━━━━━━━━━━"]
        for i in range(7):
            gun = datetime.now() + timedelta(days=i)
            tm = vakitler_al(kul, tarih=gun.strftime("%d-%m-%Y"))
            if tm:
                s.append(f"\n📅 *{gun.strftime('%d.%m %A')}*\n"
                         f"🌙`{tm.get('Fajr','--')}` "
                         f"🌤️`{tm.get('Dhuhr','--')}` "
                         f"🌇`{tm.get('Asr','--')}` "
                         f"🌆`{tm.get('Maghrib','--')}` "
                         f"🌃`{tm.get('Isha','--')}`")
        s.append("\n🤲 @NikeCheatYeniden | 📢 @nikestoretr")
        upd("\n".join(s), haftalik_alt_kb())
        log_ekle("HAFTALIK_CB", uid, isim, kul.get("sehir") or "")

    elif d == "M_k":
        upd(t["ulke"], ulke_kb(0, lang))
    elif d == "M_u":
        upd(t["usor"], uyari_kb())
    elif d == "M_api":
        upd(t["apisor"], api_kb())
    elif d == "M_dil":
        upd(HOSGELDIN_MULTI, dil_kb())
    elif d == "M_a":
        upd(t["ayar"].format(
            u=kul.get("ulke_label") or "--", s=kul.get("sehir") or "--",
            i=kul.get("ilce") or "--", m=kul.get("dk", 15),
            a=kul.get("api", "auto").upper()
        ), ikb([btn("🏠 Ana Menü", "M_menu")]))
    elif d == "M_h":
        upd(t["yard"], ikb([btn("🏠 Ana Menü", "M_menu")]))

    # ── Özel Günler
    elif d == "M_og":
        yil = datetime.now().year
        # Yakında olan günleri de göster
        yakin = ozel_gun_bugun()
        msg = "🌙 *İSLAMİ ÖZEL GÜNLER*\n━━━━━━━━━━━━━━━━━━\n"
        if yakin:
            msg += "\n⭐ *YAKIN / BUGÜN:*\n"
            for tarih_str, isim, acik, emoji, fark in yakin:
                if fark == 0:
                    msg += f"{emoji} *{isim}* — 🟢 *BUGÜN!*\n"
                elif fark > 0:
                    msg += f"{emoji} *{isim}* — ⏳ {fark} gün sonra\n"
                else:
                    msg += f"{emoji} ~~{isim}~~ — dün/geçti\n"
            msg += "\n━━━━━━━━━━━━━━━━━━\n"
        msg += f"\n📅 Yıl ve ay seçerek özel günleri görüntüleyin:"
        upd(msg, ozel_gun_kb(yil))

    elif d.startswith("OG_Y_"):
        yil = int(d[5:])
        msg = f"🌙 *{yil} İSLAMİ ÖZEL GÜNLER*\n━━━━━━━━━━━━━━━━━━\n\nAy seçin:"
        upd(msg, ozel_gun_kb(yil))

    elif d.startswith("OG_A_"):
        parca = d[5:].split("_")
        yil, ay = int(parca[0]), int(parca[1])
        msg = fmt_ozel_gunler_ay(yil, ay)
        ay_ismi = ["","Ocak","Şubat","Mart","Nisan","Mayıs","Haziran",
                   "Temmuz","Ağustos","Eylül","Ekim","Kasım","Aralık"][ay]
        kb = ikb(
            [btn(f"◀️ {yil} Yılına Dön", f"OG_Y_{yil}")],
            [btn("🏠 Ana Menü", "M_menu")]
        )
        upd(msg, kb)

    elif d.startswith("OG_TUM_"):
        yil = int(d[7:])
        msg = fmt_ozel_gunler_yil(yil)
        # Uzunsa kes
        if len(msg) > 4000:
            msg = msg[:3950] + "\n\n_(Devamı için aylara bakın)_"
        upd(msg, ikb(
            [btn(f"◀️ {yil} Yılına Dön", f"OG_Y_{yil}")],
            [btn("🏠 Ana Menü", "M_menu")]
        ))

    # Admin paneli callbackları
    elif d == "AD_users":
        if not admin_ok(uid):
            return
        upd(kul_listesi(), admin_kb())
    elif d == "AD_logs":
        if not admin_ok(uid):
            return
        upd(son_loglar(), admin_kb())
    elif d == "AD_stat":
        if not admin_ok(uid):
            return
        toplam = len(VERI["k"])
        aktif = sum(1 for u in VERI["k"].values() if u.get("aktif") and u.get("sehir"))
        seh = {}
        for u in VERI["k"].values():
            sh = u.get("sehir")
            if sh:
                seh[sh] = seh.get(sh, 0) + 1
        top5 = sorted(seh.items(), key=lambda x: -x[1])[:5]
        metin = (f"📊 *DETAYLI İSTATİSTİK*\n━━━━━━━━━━━━━━━━━━\n"
                 f"👥 Toplam : {toplam}\n✅ Aktif   : {aktif}\n"
                 f"🔔 Bugün  : {VERI.get('bugun',0)}\n📨 Toplam  : {VERI.get('toplam',0)}\n"
                 "━━━━━━━━━━━━━━━━━━\n🏙️ *TOP 5:*\n")
        for sh, cnt in top5:
            metin += f"  • {sh}: {cnt}\n"
        upd(metin, admin_kb())
    elif d == "AD_clearlog":
        if not admin_ok(uid):
            return
        log_kaydet({"events": []})
        upd("✅ Log temizlendi.", admin_kb())
        log_ekle("LOG_TEMIZLENDI", uid, isim, "")

    # ══════════════════════════════════════════════
    #  GRUP EZAN BİLDİRİM CALLBACKS
    # ══════════════════════════════════════════════

    elif d == "GA_NOP":
        pass  # pasif buton, sadece bilgi

    elif d.startswith("GA_TOGGLE_"):
        grp_id = d[10:]
        if "gruplar" not in VERI:
            VERI["gruplar"] = {}
        if grp_id not in VERI["gruplar"]:
            VERI["gruplar"][grp_id] = {"aktif": False, "aktif_vakitler": [], "dk": 0, "sehir": None}
        g = VERI["gruplar"][grp_id]
        g["aktif"] = not g.get("aktif", False)
        veri_kaydet(VERI)
        durum = "🟢 AKTİF" if g["aktif"] else "🔴 PASİF"
        upd(
            f"⚙️ *GRUP EZAN BİLDİRİMİ*\n━━━━━━━━━━━━━━━━━━\n"
            f"📍 Konum: *{g.get('sehir','Ayarlanmamış')}*\n"
            f"⚡ Durum: {durum}\n\nAyarlar:",
            grup_ayar_kb(int(grp_id))
        )
        log_ekle("GRUP_TOGGLE", uid, isim, f"{grp_id} → {durum}")

    elif d.startswith("GA_V_"):
        # GA_V_{grp_id}_{vakit}
        parca = d[5:].rsplit("_", 1)
        grp_id = parca[0]
        vakit = parca[1]
        if "gruplar" not in VERI: VERI["gruplar"] = {}
        if grp_id not in VERI["gruplar"]:
            VERI["gruplar"][grp_id] = {"aktif": False, "aktif_vakitler": [], "dk": 0, "sehir": None}
        g = VERI["gruplar"][grp_id]
        av = g.get("aktif_vakitler", [])
        if vakit in av:
            av.remove(vakit)
            eylem = "kapatıldı"
        else:
            av.append(vakit)
            eylem = "açıldı"
        g["aktif_vakitler"] = av
        veri_kaydet(VERI)
        emoji, vakit_isim = VAKIT_ISIM.get(vakit, ("🕌", vakit))
        upd(
            f"⚙️ *GRUP EZAN BİLDİRİMİ*\n━━━━━━━━━━━━━━━━━━\n"
            f"📍 Konum: *{g.get('sehir','Ayarlanmamış')}*\n"
            f"{emoji} *{vakit_isim}* bildirimi {eylem}!\n\nAyarlar:",
            grup_ayar_kb(int(grp_id))
        )

    elif d.startswith("GA_DK_"):
        grp_id = d[6:]
        upd(
            f"⏰ *BİLDİRİM ZAMANI SEÇ*\n━━━━━━━━━━━━━━━━━━\n"
            f"Vakitten kaç dakika önce bildirim atsın?\n"
            f"(0 = vakit gelince, 15 = 15 dk önce vb.)",
            grup_dk_kb(grp_id)
        )

    elif d.startswith("GD_"):
        # GD_{grp_id}_{dk}
        parca = d[3:].rsplit("_", 1)
        grp_id = parca[0]
        dk = int(parca[1])
        if "gruplar" not in VERI: VERI["gruplar"] = {}
        if grp_id not in VERI["gruplar"]:
            VERI["gruplar"][grp_id] = {"aktif": False, "aktif_vakitler": [], "dk": 0, "sehir": None}
        VERI["gruplar"][grp_id]["dk"] = dk
        veri_kaydet(VERI)
        dk_label = f"{dk} dk önce" if dk > 0 else "Vakitte (0 dk)"
        upd(
            f"⚙️ *GRUP EZAN BİLDİRİMİ*\n━━━━━━━━━━━━━━━━━━\n"
            f"⏰ Bildirim süresi: *{dk_label}* olarak ayarlandı!\n\nAyarlar:",
            grup_ayar_kb(int(grp_id))
        )

    elif d.startswith("GA_KONUM_"):
        grp_id = d[9:]
        upd(
            f"📍 *GRUP KONUMU SEÇ*\n━━━━━━━━━━━━━━━━━━\n"
            f"Ülke seçin:",
            grup_konum_kb(grp_id)
        )

    elif d.startswith("GA_GERI_"):
        grp_id = d[8:]
        g = VERI.get("gruplar", {}).get(grp_id, {})
        upd(
            f"⚙️ *GRUP EZAN BİLDİRİMİ AYARLA*\n━━━━━━━━━━━━━━━━━━\n"
            f"📍 Konum: *{g.get('sehir','Ayarlanmamış')}*\n"
            f"⚡ Durum: {'🟢 AKTİF' if g.get('aktif') else '🔴 PASİF'}\n\nAyarlar:",
            grup_ayar_kb(int(grp_id))
        )

    elif d.startswith("GK_"):
        # GK_{ulke_kod}_{grp_id}
        parca = d[3:].split("_", 1)
        ulke_kod = parca[0]
        grp_id = parca[1]
        upd(
            f"🏙️ *Şehir seçin ({ulke_kod}):*",
            grup_sehir_kb(grp_id, ulke_kod, 0)
        )

    elif d.startswith("GSP_"):
        # GSP_{grp_id}_{ulke_kod}_{sayfa}
        parca = d[4:].split("_")
        grp_id = parca[0]
        ulke_kod = parca[1]
        sayfa = int(parca[2])
        upd(f"🏙️ *Şehir seçin ({ulke_kod}):*", grup_sehir_kb(grp_id, ulke_kod, sayfa))

    elif d.startswith("GS_"):
        # GS_{grp_id}_{ulke_kod}_{sehir}
        parca = d[3:].split("_", 2)
        grp_id = parca[0]
        ulke_kod = parca[1]
        sehir = parca[2]
        veri_sehir = SEHIR_KOORDINAT.get(ulke_kod, {}).get(sehir)
        if not veri_sehir:
            return
        lat, lon, sehir_en = veri_sehir
        if "gruplar" not in VERI: VERI["gruplar"] = {}
        if grp_id not in VERI["gruplar"]:
            VERI["gruplar"][grp_id] = {"aktif": False, "aktif_vakitler": [], "dk": 0}
        g = VERI["gruplar"][grp_id]
        g["sehir"] = sehir
        g["sehir_en"] = sehir_en
        g["ilce"] = sehir
        g["ilce_en"] = sehir_en
        g["lat"] = lat
        g["lon"] = lon
        g["ulke_kod"] = ulke_kod
        veri_kaydet(VERI)
        log_ekle("GRUP_KONUM", uid, isim, f"{grp_id} → {sehir}")
        upd(
            f"⚙️ *GRUP EZAN BİLDİRİMİ*\n━━━━━━━━━━━━━━━━━━\n"
            f"✅ Konum *{sehir}* olarak ayarlandı!\n\n"
            f"Şimdi hangi vakitlerde bildirim almak istediğinizi seçin:",
            grup_ayar_kb(int(grp_id))
        )

# ═══════════════════════════════════════════════
#  POLLING
# ═══════════════════════════════════════════════
def polling():
    offset = 0
    print("✅ Bot aktif! CTRL+C ile durdur.")
    while True:
        try:
            r = tg_get("getUpdates", {"offset": offset, "timeout": 30, "limit": 100})
            for upd in r.get("result", []):
                offset = upd["update_id"] + 1
                try:
                    if "message" in upd:
                        isle_mesaj(upd["message"])
                    elif "callback_query" in upd:
                        isle_callback(upd["callback_query"])
                except Exception as e:
                    import traceback
                    print(f"[İŞLEM HATA] {e}")
                    traceback.print_exc()
        except KeyboardInterrupt:
            print("Bot durduruldu.")
            break
        except Exception as e:
            print(f"[POLLING HATA] {e}")
            time.sleep(3)
# ═══════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════
def main():
    global LOG_KANAL
    if BOT_TOKEN == "BURAYA_TOKEN_YAZ":
        print("HATA: BOT_TOKEN yazılmamış!")
        return
    LOG_KANAL = VERI.get("log_kanal", None)
    print("╔══════════════════════════════════╗")
    print("║   🕌  EZAN VAKTİ BOTU BAŞLIYOR  ║")
    print("║  Kurucu : @NikeCheatYeniden     ║")
    print("║  Kanal  : @nikestoretr          ║")
    print("╚══════════════════════════════════╝")
    threading.Thread(target=uyari_dongu, daemon=True).start()
    print("🔔 Uyarı sistemi başlatıldı.")
    log_ekle("BOT_BASLADI", 0, "SISTEM", "")
    # Varsa eski webhook'u temizle, polling moduna geç
    tg_post("deleteWebhook", {"drop_pending_updates": True})
    time.sleep(1)
    polling()

def saglik_sunucusu():
    """Replit Deployment için zorunlu healthcheck sunucusu."""
    from http.server import HTTPServer, BaseHTTPRequestHandler
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")
        def log_message(self, *a): pass
    srv = HTTPServer(("0.0.0.0", 8080), Handler)
    srv.serve_forever()

if __name__ == "__main__":
    threading.Thread(target=saglik_sunucusu, daemon=True).start()
    print("🌐 Healthcheck sunucusu başlatıldı (port 8080)")
    main()

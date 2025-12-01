# 🎬 GitHappens - Proje Yapısı Rehberi

Bu belge, projede değişiklik yapmak isteyen geliştiriciler için hazırlanmıştır.

---

## 📁 Klasör Yapısı

```text
├── main.py                 # Uygulamayı başlatan ana dosya
├── requirements.txt        # Gerekli Python paketleri
│
├── routes/                 # Sayfa yönlendirmeleri (URL'ler)
│   ├── main_routes.py      # Ana sayfa, hakkında, quiz, öneri
│   ├── auth_routes.py      # Giriş, kayıt, çıkış + User modeli
│   ├── user_routes.py      # Kullanıcı profili
│   ├── movie_routes.py     # Film listesi ve detay sayfası
│   ├── series_routes.py    # Dizi listesi
│   ├── episode_routes.py   # Bölüm listesi ve detay
│   └── celebrity_routes.py # Ünlüler listesi
│
├── templates/              # HTML şablonları (sayfaların görünümü)
│   ├── base.html           # Tüm sayfalara ortak şablon (navbar, footer)
│   ├── home.html           # Ana sayfa
│   ├── movies.html         # Film listesi sayfası
│   ├── movie.html          # Tek film detay sayfası
│   ├── series.html         # Dizi listesi sayfası
│   ├── episodes.html       # Bölüm listesi sayfası
│   ├── episode.html        # Tek bölüm detay sayfası
│   ├── celebrities.html    # Ünlüler sayfası
│   ├── login.html          # Giriş sayfası
│   ├── signup.html         # Kayıt sayfası
│   ├── profile.html        # Kullanıcı profili
│   └── ...                 # Diğer sayfalar
│
├── static/                 # Statik dosyalar
│   ├── css/                # Stil dosyaları
│   │   ├── base.css        # Genel stiller
│   │   ├── home.css        # Ana sayfa stilleri
│   │   ├── movies.css      # Film sayfası stilleri
│   │   └── ...             # Her sayfa için ayrı CSS
│   ├── js/                 # JavaScript dosyaları
│   └── img/                # Görseller
│
├── database/               # Veritabanı bağlantısı
│   └── db.py               # MySQL bağlantı ayarları
│
├── admin/                  # Admin paneli
│   ├── routes.py           # Admin sayfaları
│   └── admin.py            # Admin işlemleri
│
├── data/                   # CSV veri dosyaları
└── sql/                    # SQL sorgu dosyaları
```

---

## 🔧 Ne Yapmak İstiyorsun?

### 🎨 "Bir sayfanın görünümünü değiştirmek istiyorum"

**→ `templates/` klasörüne git**

| Sayfa | Dosya |
|-------|-------|
| Ana sayfa | `templates/home.html` |
| Film listesi | `templates/movies.html` |
| Film detay | `templates/movie.html` |
| Dizi listesi | `templates/series.html` |
| Bölümler | `templates/episodes.html` |
| Ünlüler | `templates/celebrities.html` |
| Giriş | `templates/login.html` |
| Kayıt | `templates/signup.html` |
| Profil | `templates/profile.html` |

> 💡 Tüm sayfalarda ortak olan navbar ve footer → `templates/base.html`

---

### 🎭 "Bir sayfanın stilini (renk, font, boyut) değiştirmek istiyorum"

**→ `static/css/` klasörüne git**

Her sayfa için ayrı CSS dosyası var:

- `base.css` → Genel stiller, navbar, footer
- `home.css` → Ana sayfa
- `movies.css` → Film sayfası
- `series.css` → Dizi sayfası
- vb.

---

### ⚙️ "Bir sayfanın veritabanından çektiği veriyi değiştirmek istiyorum"

**→ `routes/` klasörüne git**

| Ne değiştirmek istiyorsun | Dosya |
|---------------------------|-------|
| Film verisi, arama, filtreleme | `routes/movie_routes.py` |
| Dizi verisi | `routes/series_routes.py` |
| Bölüm verisi | `routes/episode_routes.py` |
| Ünlü verisi | `routes/celebrity_routes.py` |
| Giriş/kayıt mantığı | `routes/auth_routes.py` |
| Ana sayfa, quiz, öneri | `routes/main_routes.py` |
| Profil sayfası | `routes/user_routes.py` |

---

### 👤 "Kullanıcı bilgilerini değiştirmek istiyorum (yeni alan eklemek vb.)"

**→ `routes/auth_routes.py` dosyasını aç**

Dosyanın üst kısmında `User` sınıfı var. Kullanıcının sahip olduğu alanlar:

- username, email, password
- dob (doğum tarihi), gender
- liked_movies, liked_series, liked_actors

---

### 🗄️ "Veritabanı bağlantısını değiştirmek istiyorum"

**→ `database/db.py` dosyasını aç**

MySQL bağlantı bilgileri burada.

---

### 🛠️ "Admin panelini değiştirmek istiyorum"

**→ `admin/` klasörüne git**

- `admin/routes.py` → Admin sayfa yönlendirmeleri
- `templates/admin/` → Admin HTML şablonları

---

### ➕ "Yeni bir sayfa eklemek istiyorum"

1. `routes/` içinde uygun dosyaya yeni route ekle (veya yeni dosya oluştur)
2. `templates/` içine yeni HTML dosyası ekle
3. `static/css/` içine stil dosyası ekle (opsiyonel)
4. Yeni route dosyası oluşturduysan `routes/__init__.py` ve `main.py`'a ekle

---

## 🚀 Uygulamayı Çalıştırma

```bash
# Virtual environment aktif et
.\.venv\Scripts\Activate.ps1

# Uygulamayı başlat
python main.py
```

Tarayıcıda: `http://localhost:8080`

---

## 📝 Özet Tablo

| Amaç | Dosya/Klasör |
|------|--------------|
| Sayfa görünümü (HTML) | `templates/` |
| Sayfa stili (CSS) | `static/css/` |
| Sayfa mantığı (Python) | `routes/` |
| Kullanıcı yapısı | `routes/auth_routes.py` |
| Veritabanı bağlantısı | `database/db.py` |
| Admin paneli | `admin/` |
| Uygulamayı başlat | `main.py` |

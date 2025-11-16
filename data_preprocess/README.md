# Data Preprocess Pipeline

Bu klasördeki script'ler IMDb veri seti benzeri **TSV** dosyalarından başlayıp, proje tarafından kullanılan son **CSV** dosyalarına kadar bir preprocessing pipeline'ı oluşturur.

Aşağıdaki adımlar, elinde ham `.tsv` dosyaları olan birinin bu script'leri **hangi sırayla** çalıştıracağını gösterir.

> Çalıştırma komutları, proje kök dizininde (repo root) olduğun varsayılarak verilmiştir.

---

## 1. TSV → CSV dönüşümü

**Amaç:** `data/` klasöründeki tüm `.tsv` dosyalarını aynı klasörde `.csv`'ye dönüştürmek.

Script: `data_preprocess/tsv2csv.py`

```bash
python data_preprocess/tsv2csv.py
```

**Ne üretir?**
- `data/title.basics.tsv` → `data/title.basics.csv`
- `data/title.ratings.tsv` → `data/title.ratings.csv`
- vb. (klasördeki tüm `.tsv` dosyaları için)

Bu adım bittikten sonra **en azından** `data/title.basics.csv` dosyasının oluşmuş olması gerekir.

---

## 2. Genre dimension tablosu oluşturma

**Amaç:** `title.basics.csv` içindeki `genres` sütunundan distinct türleri çıkarıp her birine `genre_id` atamak.

Script: `data_preprocess/genre_df.py`

```bash
python data_preprocess/genre_df.py
```

**Ne üretir?**
- `data/genre.csv`
  - Sütunlar: `genre_id, genre`
  - Örnek: `1,Action`, `2,Adult`, ...

Bu tablo, veritabanında **genre** dimension tablosu olarak kullanılabilir.

---

## 3. Filmleri ve dizileri ayırma

**Amaç:** `title.basics.csv` dosyasını, `titleType` değerlerine göre **filmler** ve **diziler** olarak ikiye ayırmak.

Script: `data_preprocess/type_seperator.py`

```bash
python data_preprocess/type_seperator.py
```

**Ne yapar?**
- `title.basics.csv` dosyasını okur.
- `titleType` değerlerine göre ayırır:
  - Filmler (`movies`): `movie`, `short`, `tvMovie`, `video`
  - Diziler (`series`): `tvSeries`, `tvMiniSeries`, `tvEpisode`, `tvPilot`, `tvShort`, `tvSpecial`
  - `videoGame` ve diğer tipler **yok sayılır**.

**Ne üretir?**
- `data/movies.basics.csv`
- `data/series.basics.csv`

---

## 4. Genre FK uygulama (genre isimlerini genre_id'ye çevirme)

**Amaç:** `movies.basics.csv` ve `series.basics.csv` içindeki `genres` sütunlarını, `genre.csv`'deki `genre_id` değerleri ile değiştirmek.

Script: `data_preprocess/genre_fk.py`

```bash
python data_preprocess/genre_fk.py
```

**Ne yapar?**
- `data/genre.csv` dosyasını okur (`genre_id, genre`).
- `movies.basics.csv` ve `series.basics.csv` içindeki `genres` kolonunu işler:
  - Önce genre isimlerini virgüle göre ayırır.
  - Her bir genre ismini `genre.csv`'deki `genre_id` ile eşleştirir.
  - Her `tconst` için birden fazla tür varsa, `genre_id`'leri virgülle birleştirir.
- Sonuçta **her satırdaki `genres` sütunu artık genre isimleri değil, `genre_id` listesi** olur.

**Örnek:**
- Önce: `genres = "Documentary,Short"`
- Sonra: `genres = "8,23"` (8 = Documentary, 23 = Short)

**Üzerine yazdığı dosyalar:**
- `data/movies.basics.csv`
- `data/series.basics.csv`

---

## 5. Kolon sadeleştirme (table fix)

**Amaç:** Projede kullanılmayan bazı kolonları düşürerek tabloyu sadeleştirmek.

Script: `data_preprocess/tablefix.py`

```bash
python data_preprocess/tablefix.py
```

**Ne yapar?**
- Hem `movies.basics.csv` hem `series.basics.csv` için `originalTitle` sütununu siler.
- Ek olarak **sadece** `movies.basics.csv` için `endYear` sütununu siler.

**Son durumda kolonlar:**

- `data/movies.basics.csv`:
  - `tconst, titleType, primaryTitle, isAdult, startYear, runtimeMinutes, genres`

- `data/series.basics.csv`:
  - `tconst, titleType, primaryTitle, isAdult, startYear, endYear, runtimeMinutes, genres`

---

## Özet: Doğru çalışma sırası

1. **TSV → CSV**
   ```bash
   python data_preprocess/tsv2csv.py
   ```
2. **Genre dimension** (`genre.csv` üret)
   ```bash
   python data_preprocess/genre_df.py
   ```
3. **Filmleri ve dizileri ayır** (`movies.basics.csv`, `series.basics.csv` üret)
   ```bash
   python data_preprocess/type_seperator.py
   ```
4. **Genre FK uygula** (`genres` → `genre_id` listesi)
   ```bash
   python data_preprocess/genre_fk.py
   ```
5. **Tabloları sadeleştir** (gereksiz kolonları kaldır)
   ```bash
   python data_preprocess/tablefix.py
   ```

Bu 5 adımı sırayla çalıştırdığında, veritabanına yüklemeye hazır, temizlenmiş:
- `data/genre.csv`
- `data/movies.basics.csv`
- `data/series.basics.csv`

dosyalarına sahip olursun.

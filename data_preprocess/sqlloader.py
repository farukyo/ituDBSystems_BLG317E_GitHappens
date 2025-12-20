import os
import re

# --- AYARLAR ---
# Parçalanmış dosyaların olduğu klasör
input_folder = r'C:/Users/faruk/Desktop/Code/ituDBSystems_BLG317E_GitHappens/data/principals_parts'

# Çıktı olarak üretilecek SQL dosyasının yeri
output_sql_file = r'C:/Users/faruk/Desktop/Code/ituDBSystems_BLG317E_GitHappens/data/load_all_parts.sql'

# Klasörün var olup olmadığını kontrol et
if not os.path.exists(input_folder):
    print(f"HATA: '{input_folder}' klasörü bulunamadı!")
    exit(1)

# Dosyaları listele
files = [f for f in os.listdir(input_folder) if f.endswith('.tsv') and f.startswith('principals_part_')]

if len(files) == 0:
    print(f"HATA: '{input_folder}' içinde principals_part_*.tsv dosyası bulunamadı!")
    exit(1)

# Dosyaları numarasına göre sırala (Önemli: part_1, part_2... part_10 sırasıyla gitmesi için)
# Yoksa part_1, part_10, part_11... part_2 şeklinde sıralanır.
files.sort(key=lambda f: int(re.search(r'\d+', f).group()))

print(f"Toplam {len(files)} dosya bulundu. SQL oluşturuluyor...")

# Çıktı klasörünün var olduğundan emin ol
os.makedirs(os.path.dirname(output_sql_file), exist_ok=True)

with open(output_sql_file, 'w', encoding='utf-8') as f:
    # 1. Başlangıç Ayarları (Hızlandırma)
    f.write("-- Hızlandırma ve Güvenlik Ayarları\n")
    f.write("TRUNCATE TABLE principals;\n")
    f.write("ALTER TABLE principals DISABLE KEYS;\n")
    f.write("SET autocommit = 0;\n")
    f.write("SET unique_checks = 0;\n")
    f.write("SET foreign_key_checks = 0;\n")
    f.write("SET sql_log_bin = 0;\n\n")

    # 2. Döngü ile LOAD DATA komutlarını yaz
    for filename in files:
        # Windows yolu için ters slash düzeltmesi
        full_path = os.path.join(input_folder, filename).replace('\\', '/')

        sql_command = f"""LOAD DATA LOCAL INFILE '{full_path}' 
INTO TABLE principals 
FIELDS TERMINATED BY ',' 
OPTIONALLY ENCLOSED BY '"' 
LINES TERMINATED BY '\\n' 
IGNORE 1 LINES;

"""
        f.write(f"-- {filename} yükleniyor\n")
        f.write(sql_command)

    # 3. Bitiş Ayarları (Eski haline getirme ve Commit)
    f.write("\n-- İşlemi Tamamla\n")
    f.write("COMMIT;\n")
    f.write("ALTER TABLE principals ENABLE KEYS;\n")
    f.write("SET unique_checks = 1;\n")
    f.write("SET foreign_key_checks = 1;\n")
    f.write("SET sql_log_bin = 1;\n")
    f.write("SET autocommit = 1;\n")

print(f"Bitti! '{output_sql_file}' dosyası oluşturuldu.")
print("Bu dosyayı MySQL Workbench'te File -> Open SQL Script diyerek aç ve çalıştır.")
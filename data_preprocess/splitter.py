import csv
import os

# --- AYARLAR ---
# Temizlenmiş dosyanın yolu (örneğin principals_clean.csv)
input_file = r'C:/Users/faruk/Desktop/Code/ituDBSystems_BLG317E_GitHappens/data/principals_clean.tsv'

# Parçaların kaydedileceği klasör
output_folder = r'C:/Users/faruk/Desktop/Code/ituDBSystems_BLG317E_GitHappens/data/principals_parts/'

# Her dosyada kaç satır olsun? (1 Milyon idealdir)
CHUNK_SIZE = 1000000

# Klasör yoksa oluştur
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

print(f"Bölme işlemi başlıyor: {input_file}")


def write_chunk(part_num, header, rows):
    filename = os.path.join(output_folder, f'principals_part_{part_num}.tsv')
    with open(filename, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)  # Başlığı her dosyaya ekle
        writer.writerows(rows)
    print(f"--> {filename} oluşturuldu ({len(rows)} satır).")


with open(input_file, mode='r', encoding='utf-8', newline='') as infile:
    reader = csv.reader(infile)

    try:
        header = next(reader)  # İlk satırı (başlık) al
    except StopIteration:
        print("Dosya boş!")
        exit()

    current_chunk = []
    part_counter = 1

    for row in reader:
        current_chunk.append(row)

        # Liste dolunca dosyaya yaz ve hafızayı boşalt
        if len(current_chunk) == CHUNK_SIZE:
            write_chunk(part_counter, header, current_chunk)
            current_chunk = []
            part_counter += 1

    # Döngü bittiğinde kalan son satırları yaz
    if current_chunk:
        write_chunk(part_counter, header, current_chunk)

print("\nBitti! Dosyalar klasörde hazır.")
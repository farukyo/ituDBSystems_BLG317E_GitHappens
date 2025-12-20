import csv
import re

input_file = r'C:/Users/faruk/Desktop/Code/ituDBSystems_BLG317E_GitHappens/data/principals.csv'
output_file = r'C:/Users/faruk/Desktop/Code/ituDBSystems_BLG317E_GitHappens/data/principals_clean.csv'

# Regex: [" ve "] ve " işaretlerini temizlemek için
chars_pattern = re.compile(r'[\[\]"]')

print("Temizleme işlemi başlıyor... Bu işlem RAM ve CPU kullanır, diske yazar.")

with open(input_file, mode='r', encoding='utf-8', newline='') as infile, \
        open(output_file, mode='w', encoding='utf-8', newline='') as outfile:
    reader = csv.reader(infile)
    writer = csv.writer(outfile)

    # Başlık satırını atla veya yaz (MySQL'de IGNORE 1 LINES kullanıyorsan yazabilirsin)
    headers = next(reader)
    writer.writerow(headers)

    row_count = 0

    for row in reader:
        # row[4] -> job, row[5] -> characters

        # Job: '0' ise boş string (MySQL \N null algılar) veya NULL yap
        if row[4] == '0':
            row[4] = '\\N'  # MySQL text yüklemesinde NULL ifadesi

        # Characters: Temizlik işlemi
        if row[5] == '0':
            row[5] = '\\N'
        else:
            # ["Blacksmith"] -> Blacksmith dönüşümü
            # Köşeli parantez ve tırnakları sil
            row[5] = chars_pattern.sub('', row[5]).strip()

        writer.writerow(row)
        row_count += 1

        if row_count % 500000 == 0:
            print(f"{row_count} satır işlendi...")

print(f"İşlem tamamlandı! Toplam {row_count} satır.")
print(f"Yeni dosya: {output_file}")
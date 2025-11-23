import csv

# Dosya isimlerini buraya yazın
giris_dosyasi = '../data/names_clean.csv'
cikis_dosyasi = '../data/names.csv'

print("İşlem başlıyor...")

with open(giris_dosyasi, mode='r', encoding='utf-8', newline='') as f_in, \
        open(cikis_dosyasi, mode='w', encoding='utf-8', newline='') as f_out:
    reader = csv.reader(f_in)
    writer = csv.writer(f_out)

    for row in reader:
        # List comprehension ile satırdaki her hücreye bakıyoruz
        # Eğer hücre boşsa ('') yerine '0' yazıyoruz, değilse aynen bırakıyoruz.
        yeni_satir = ['0' if hucre == '' else hucre for hucre in row]

        writer.writerow(yeni_satir)

print(f"Tamamlandı! '{cikis_dosyasi}' dosyasını MySQL'e import edebilirsiniz.")
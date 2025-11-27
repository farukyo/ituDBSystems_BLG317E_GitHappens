document.addEventListener('DOMContentLoaded', () => {
    let expanded = false;
    const selectBox = document.querySelector('.selectBox');
    const checkboxes = document.getElementById("checkboxes");
    const container = document.querySelector('.multiselect');

    // 1. Kutucuğa tıklanınca menüyü aç/kapat
    if (selectBox) {
        selectBox.addEventListener('click', (e) => {
            // Olayın yukarı (document) taşınmasını engelle
            e.stopPropagation();
            
            if (!expanded) {
                checkboxes.style.display = "block";
                expanded = true;
            } else {
                checkboxes.style.display = "none";
                expanded = false;
            }
        });
    }

    // 2. Menünün içine tıklanınca (checkbox'lara) menü KAPANMASIN
    if (checkboxes) {
        checkboxes.addEventListener('click', (e) => {
            e.stopPropagation(); // Tıklama olayını burada durdur
        });
    }

    // 3. Sayfanın boş bir yerine tıklanırsa menüyü kapat
    document.addEventListener('click', (e) => {
        if (expanded) {
            checkboxes.style.display = "none";
            expanded = false;
        }
    });
});

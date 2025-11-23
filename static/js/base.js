// Sidebar öğelerini ve butonları seçme
const sidebar = document.getElementById("sidebar");
const mainContent = document.getElementById("main-content");
const openBtn = document.getElementById("openMenuBtn");
const closeBtn = document.querySelector(".sidebar .closebtn");
// Menü durumunu CSS'teki genişlik üzerinden kontrol edeceğiz.
const sidebarWidth = "250px";


// Sidebar'ı açıp kapatmayı yöneten tek fonksiyon
function toggleNav() {
    // Sidebar şu anda açıksa (genişliği 0'dan büyükse)
    if (sidebar.style.width === sidebarWidth) {
        // Kapat
        sidebar.style.width = "0";
        // Ana içeriği kaydırmıyoruz artık
        return false; // Kapalı durum
    } else {
        // Aç
        sidebar.style.width = sidebarWidth;
        // Ana içeriği kaydırmıyoruz artık
        return true; // Açık durum
    }
}


// Olay dinleyicileri (Event Listeners) ekleme
document.addEventListener('DOMContentLoaded', () => {

    // 1. Açma Butonuna tıklandığında sadece toggleNav'ı çağır
    if (openBtn) {
        openBtn.addEventListener('click', toggleNav);
    }

    // 2. Kapatma Butonuna tıklandığında sadece toggleNav'ı çağır (veya doğrudan closeNav)
    if (closeBtn) {
        closeBtn.addEventListener('click', toggleNav);
        // Veya daha net olması için: closeBtn.addEventListener('click', closeNav);
    }

    // 3. Sidebar dışına tıklandığında kapatma mantığı
    document.addEventListener('click', function (event) {
        // 3a. Eğer sidebar şu anda açıksa (toggleNav ile kontrol edilebilir)
        if (sidebar.style.width === sidebarWidth) {

            // 3b. Tıklama ne sidebar'ın içinde NE DE açma butonunun içindeyse
            if (!sidebar.contains(event.target) && !openBtn.contains(event.target)) {
                // Kapat
                toggleNav();
            }
        }
    });
});
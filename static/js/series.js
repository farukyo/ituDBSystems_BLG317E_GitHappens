// Form submit olayını yönet
document.addEventListener("DOMContentLoaded", () => {
    const form = document.querySelector("form");
    
    if (form) {
        form.addEventListener("submit", (e) => {
            e.preventDefault();
            
            const params = new FormData(form);
            const queryString = new URLSearchParams(params).toString();
            
            // Aynı sayfaya yönlendir (sunucu render yapıp güncelle)
            window.location.href = "/series?" + queryString;
        });
    }
    
    // Enter tuşu ile de arama yapılabilsin
    const searchInput = document.getElementById("series-search");
    if (searchInput) {
        searchInput.addEventListener("keypress", (e) => {
            if (e.key === "Enter") {
                form?.dispatchEvent(new Event("submit"));
            }
        });
    }
});
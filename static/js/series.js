// Search Button
const seriesSearchBtn = document.getElementById("series-search-btn");
const seriesSearchInput = document.getElementById("series-search");

if (seriesSearchBtn && seriesSearchInput) {
    seriesSearchBtn.addEventListener("click", () => {
        console.log("Series search clicked:", seriesSearchInput.value);
        // TODO: backend'den seriesTitle'a göre sonuç çekip #series-results'a yaz
    });
}

// Filter Button
const seriesFilterBtn = document.getElementById("series-filter-btn");

if (seriesFilterBtn) {
    seriesFilterBtn.addEventListener("click", () => {
        console.log("Series filters applied:");
        console.log("titleType:", document.getElementById("title-type").value);
        console.log("startYear:", document.getElementById("start-year").value);
        console.log("endYear:", document.getElementById("end-year").value);
        console.log("runtimeMinutes:", document.getElementById("runtime").value);
        console.log("isAdult:", document.getElementById("is-adult").value);
        console.log("genreId:", document.getElementById("genre").value);
        // TODO: bu değerlerle backend'e istek at ve #series-results'ı güncelle
    });
}

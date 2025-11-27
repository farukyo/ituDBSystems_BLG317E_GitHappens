function fetchSeriesResults(params) {
    const queryString = new URLSearchParams(params).toString();
    fetch("/series?" + queryString, {
        headers: { "X-Requested-With": "XMLHttpRequest" }
    })
        .then(response => response.text())
        .then(html => {
            document.getElementById("series-results").innerHTML = html;
        })
        .catch(err => console.error("Fetch error:", err));
}

// Search button
const seriesSearchBtn = document.getElementById("series-search-btn");
const seriesSearchInput = document.getElementById("series-search");

seriesSearchBtn?.addEventListener("click", () => {
    fetchSeriesResults({ q: seriesSearchInput.value });
});

// Filter button
const seriesFilterBtn = document.getElementById("series-filter-btn");

seriesFilterBtn?.addEventListener("click", () => {
    const params = {
        titleType: document.getElementById("title-type").value,
        startYear: document.getElementById("start-year").value,
        endYear: document.getElementById("end-year").value,
        runtime: document.getElementById("runtime").value,
        isAdult: document.getElementById("is-adult").value
    };
    fetchSeriesResults(params);
});

// Page load - tüm dizileri göster
document.addEventListener("DOMContentLoaded", () => {
    fetchSeriesResults({});
});
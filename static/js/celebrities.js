// Celebrities Page JavaScript

document.addEventListener('DOMContentLoaded', () => {
    const searchBtn = document.getElementById("search-btn");
    const filterBtn = document.getElementById("filter-btn");
    const searchInput = document.getElementById("celebrity-search");

    /* Search Button */
    if (searchBtn) {
        searchBtn.addEventListener("click", () => {
            const query = searchInput ? searchInput.value : '';
            console.log("Search clicked:", query);
            // TODO: Implement actual search functionality
        });
    }

    /* Enter key support for search */
    if (searchInput) {
        searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                searchBtn.click();
            }
        });
    }

    /* Filter Button */
    if (filterBtn) {
        filterBtn.addEventListener("click", () => {
            console.log("Filters applied:");
            console.log("Profession:", document.getElementById("profession").value);
            console.log("Primary Name:", document.getElementById("primary-name").value);
            console.log("Birth Year:", document.getElementById("birth-year").value);
            console.log("Death Year:", document.getElementById("death-year").value);
            console.log("Order By:", document.getElementById("order-by").value);
            // TODO: Implement actual filter functionality
        });
    }
});
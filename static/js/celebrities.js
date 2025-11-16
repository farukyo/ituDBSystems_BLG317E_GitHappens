/* Search Button */

document.getElementById("search-btn").addEventListener("click", () => {
    console.log("Search clicked:", document.getElementById("celebrity-search").value);
});

/* Filter Button */
document.getElementById("filter-btn").addEventListener("click", () => {
    console.log("Filters applied:");
    console.log("Profession:", document.getElementById("profession").value);
    console.log("Primary Name:", document.getElementById("primary-name").value);
    console.log("Birth Year:", document.getElementById("birth-year").value);
    console.log("Death Year:", document.getElementById("death-year").value);
    console.log("Order By:", document.getElementById("order-by").value);
});
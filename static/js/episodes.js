// Episodes page JavaScript
document.addEventListener('DOMContentLoaded', function () {
    console.log('Episodes page loaded');

    const filterForm = document.getElementById('episode-filter-form');

    // Remove empty parameters before form submission
    if (filterForm) {
        filterForm.addEventListener('submit', function (e) {
            const inputs = filterForm.querySelectorAll('input');

            inputs.forEach(input => {
                if (!input.value || input.value.trim() === '') {
                    input.disabled = true;
                }
            });
        });
    }

    // Add keyboard shortcut for search (Enter key in any input)
    const inputs = document.querySelectorAll('.filter-group input');
    inputs.forEach(input => {
        input.addEventListener('keypress', function (e) {
            if (e.key === 'Enter') {
                filterForm.submit();
            }
        });
    });

    // Highlight active filters
    const urlParams = new URLSearchParams(window.location.search);
    inputs.forEach(input => {
        if (urlParams.get(input.name)) {
            input.classList.add('active-filter');
        }
    });

    // Clear single filter on double-click
    inputs.forEach(input => {
        input.addEventListener('dblclick', function () {
            this.value = '';
            this.focus();
        });
    });
});

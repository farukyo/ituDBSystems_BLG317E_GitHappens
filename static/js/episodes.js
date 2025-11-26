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

    // SQL Query Popup functionality
    const showSqlBtn = document.getElementById('showSqlBtn');
    const sqlPopup = document.getElementById('sqlPopup');
    const closeSqlBtn = document.getElementById('closeSqlBtn');

    if (showSqlBtn && sqlPopup) {
        // Open popup
        showSqlBtn.addEventListener('click', function () {
            sqlPopup.classList.add('active');
            document.body.style.overflow = 'hidden';
        });

        // Close popup with X button
        if (closeSqlBtn) {
            closeSqlBtn.addEventListener('click', function () {
                sqlPopup.classList.remove('active');
                document.body.style.overflow = '';
            });
        }

        // Close popup when clicking overlay
        sqlPopup.addEventListener('click', function (e) {
            if (e.target === sqlPopup) {
                sqlPopup.classList.remove('active');
                document.body.style.overflow = '';
            }
        });

        // Close popup with Escape key
        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape' && sqlPopup.classList.contains('active')) {
                sqlPopup.classList.remove('active');
                document.body.style.overflow = '';
            }
        });
    }
});

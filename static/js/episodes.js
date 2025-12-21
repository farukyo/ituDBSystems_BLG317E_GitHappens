document.addEventListener('DOMContentLoaded', function () {
    console.log('Episodes page loaded');

    const filterForm = document.getElementById('episode-filter-form');

    
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

    const inputs = document.querySelectorAll('.filter-group input');
    inputs.forEach(input => {
        input.addEventListener('keypress', function (e) {
            if (e.key === 'Enter') {
                filterForm.submit();
            }
        });
    });


    const urlParams = new URLSearchParams(window.location.search);
    inputs.forEach(input => {
        if (urlParams.get(input.name)) {
            input.classList.add('active-filter');
        }
    });


    inputs.forEach(input => {
        input.addEventListener('dblclick', function () {
            this.value = '';
            this.focus();
        });
    });

 
    const showSqlBtn = document.getElementById('showSqlBtn');
    const sqlPopup = document.getElementById('sqlPopup');
    const closeSqlBtn = document.getElementById('closeSqlBtn');

    if (showSqlBtn && sqlPopup) {
 
        showSqlBtn.addEventListener('click', function () {
            sqlPopup.classList.add('active');
            document.body.style.overflow = 'hidden';
        });


        if (closeSqlBtn) {
            closeSqlBtn.addEventListener('click', function () {
                sqlPopup.classList.remove('active');
                document.body.style.overflow = '';
            });
        }


        sqlPopup.addEventListener('click', function (e) {
            if (e.target === sqlPopup) {
                sqlPopup.classList.remove('active');
                document.body.style.overflow = '';
            }
        });

 
        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape' && sqlPopup.classList.contains('active')) {
                sqlPopup.classList.remove('active');
                document.body.style.overflow = '';
            }
        });
    }
});

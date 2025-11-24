// Episodes page JavaScript
document.addEventListener('DOMContentLoaded', function () {
    console.log('Episodes page loaded');

    // Optional: Add any client-side filtering or interactive features here
    const episodeCards = document.querySelectorAll('.episode-card');

    episodeCards.forEach(card => {
        card.addEventListener('click', function () {
            // You can add click behavior for featured episodes
            console.log('Episode card clicked:', this.querySelector('h3').textContent);
        });
    });

    // Optional: Form validation
    const filterForm = document.querySelector('form');
    if (filterForm) {
        filterForm.addEventListener('submit', function (e) {
            // You can add custom validation here if needed
            console.log('Filter form submitted');
        });
    }
});

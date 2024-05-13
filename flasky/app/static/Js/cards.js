document.addEventListener('DOMContentLoaded', function() {
    const cameraCards = document.querySelectorAll('.camera-card');

    cameraCards.forEach(card => {
        card.addEventListener('click', function() {
            this.classList.toggle('active');
        });
    });
});       
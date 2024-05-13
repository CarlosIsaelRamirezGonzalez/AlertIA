document.addEventListener('DOMContentLoaded', function() {
    console.log("Google Map Popup working");

    const locationInput = document.querySelector('.add-camera-input[placeholder="Location Camera"]');
    const popup = document.querySelector('.add-camera-popup');
    const closeButton = popup.querySelector('.add-camera-popup-icon');
    const mapInput = popup.querySelector('.add-camera-popup-map-input');
    const confirmButton = popup.querySelector('.add-camera-popup-map-buttton');
    
    popup.style.display = 'none';
    
    // Mostrar popup cuando se hace clic en el input de ubicación
    locationInput.addEventListener('click', function() {
        popup.style.display = 'flex';
    });
    // Ocultar popup cuando se hace clic en el botón de cierre
    closeButton.addEventListener('click', function() {
        popup.style.display = 'none';
    });
    // Ocultar popup cuando se hace clic fuera de él
    window.addEventListener('click', function(event) {
        if (event.target !== popup && !popup.contains(event.target) && event.target !== locationInput) {
            popup.style.display = 'none';
        }
    });
    // Poner la informacion de el input del mapa en el input de register camera
    confirmButton.addEventListener("click", function() {
        locationInput.value = mapInput.value;
        popup.style.display = 'none';
    });
});


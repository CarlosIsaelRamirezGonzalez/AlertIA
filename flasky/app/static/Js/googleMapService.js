document.addEventListener('DOMContentLoaded', function() {
    console.log("Google Map Popup working");

    const locationInput = document.querySelector('.add-camera-input[placeholder="Location Camera"]');
    const latitudeInput = document.getElementById('latitude');
    const longitudeInput = document.getElementById('longitude');
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
        latitudeInput.value = marker.getPosition().lat();
        longitudeInput.value = marker.getPosition().lng();
        popup.style.display = 'none';
    });
});

const argCoords = {lat:  19.42847, lng: -99.12766}
const mapDiv = document.getElementById("map");
const input = document.getElementById("place_input")
let map;
let marker;
let autoComplete;

console.log("Google Map Service working");

function initMap() {
    map = new google.maps.Map(mapDiv, {
        center: argCoords,
        zoom: 10,
    });

    marker = new google.maps.Marker({
        map: map,
    });

    map.addListener('click', function(event) {
        const newLocation = event.latLng;
        marker.setPosition(newLocation)

        const geoCoder = new google.maps.Geocoder();
        geoCoder.geocode({ location: newLocation }, function(results, status) {
            if (status == "OK") {
                if (results[0]) {
                    const newAddress = results[0].formatted_address;
                    input.value = newAddress
                }
            }
        });
    });

    initAutoComplete();
}

function initAutoComplete() {
    autoComplete = new google.maps.places.Autocomplete(input);

    autoComplete.addListener("place_changed", function() {
        const place = autoComplete.getPlace();
        map.setCenter(place.geometry.location);
        marker.setPosition(place.geometry.location)
    });
}

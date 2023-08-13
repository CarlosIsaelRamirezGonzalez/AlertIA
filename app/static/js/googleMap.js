const mapDiv = document.getElementById("map");
const initCord = {lat: 20.7058091, lng: -103.3406015 };
const input = document.getElementById("address_input")
let map;
let marker;
let autocomplete;

function initMap() {
    // Objeto google maps
    map = new google.maps.Map(mapDiv, {
        center: initCord,
        zoom: 18
    });
    // Objeto para usar marker
    marker = new google.maps.Marker({
        map: map
    });
    // Cuando el usuario presione  
    map.addListener('click', function(event){
        // Cambiamos el marker
        const newLocation = event.latLng;
        marker.setPosition(newLocation);

        // Con geocoder (API google) obtenemos la direccion donde se posiciono el marker
        const geocoder = new google.maps.Geocoder();
        geocoder.geocode({ location: newLocation }, function(results, status) {
            if (status == "OK") {
                if (results[0]) {
                    const newAddress = results[0].formatted_address;
                    input.value = newAddress;
                } else {
                    console.log("No se encontro nada");
                }
            } else {
                console.log("Error en la codificacion inversa");
            }
        });
    });
    initAutoComplete();
}

function initAutoComplete() {
    autocomplete = new google.maps.places.Autocomplete(input);
    autocomplete.addListener("place_changed", function() {
        const place = autocomplete.getPlace();
        map.setCenter(place.geometry.location);
        marker.setPosition(place.geometry.location);
    });
}
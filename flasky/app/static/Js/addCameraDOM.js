document.addEventListener('DOMContentLoaded', function() {
    const ipInput =  document.querySelector('.add-camera-input[placeholder="IP Address"]');
    const securityCameraOption = document.getElementById("SecurityCamera");
    const webCameraOption = document.getElementById("WebCamera");
    const placeSelect = document.getElementById('place-select');
    const personalizedAlert = document.getElementById('personalized-alert');
    const personalizedAlertTitle = document.getElementById('personalized-alert-title');
    console.log("Google Map DOM working");

    ipInput.style.display = 'none';

    // Alerts
    placeSelect.addEventListener('change', function() {
        if (this.value == "Personalized") {
            personalizedAlert.style.display = "flex";
            personalizedAlertTitle.style.display = "flex"
        } else {
            personalizedAlert.style.display = "none";
            personalizedAlertTitle.style.display = "none"
        }
    }); 

    // Mostrar campo de IP y icono cuando se selecciona la opción "SecurityCamera"
    securityCameraOption.addEventListener('change', function() {
        ipInput.style.display = 'flex';
    });

    webCameraOption.addEventListener('change', function() {
        ipInput.style.display = 'none';
        ipInput.value = "";
    });
});
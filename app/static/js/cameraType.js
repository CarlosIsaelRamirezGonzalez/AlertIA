const images = document.querySelectorAll('.camera-image');

images.forEach(image => {
    image.addEventListener('click', function() {
        const cameraType = this.getAttribute('data-camera-type') 
        // Codificar el valor de cameraType para asegurar que sea seguro para usar en una URL
        const encodedCameraType = encodeURIComponent(cameraType);
        // Redirigir al usuario incluyendo el parámetro de consulta en la URL
        window.location.href = `/registerCamera?cameraType=${encodedCameraType}`;

    });
});
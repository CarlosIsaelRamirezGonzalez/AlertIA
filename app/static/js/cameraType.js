const images = document.querySelectorAll('.camera-image');

images.forEach(image => {
    image.addEventListener('click', function() {

        const value = this.getAttribute('data-camera-type');

        const formData = new FormData();
        formData.append('value', value);

        // Peticion HTTP POST al backend
        fetch('WelcomePage', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            console.log(data)
        })
        .catch(error => {
            // errores en la peticion (error)
        });
    });
});
document.addEventListener('DOMContentLoaded', function() {
    const deleteButtons = document.querySelectorAll('.fa-trash');
    const editButtons = document.querySelectorAll('.fa-pen-to-square');

    deleteButtons.forEach(button => {
        button.addEventListener('click', function() {
            const cameraId = getCameraId(this);
            console.log(cameraId)
            deleteCamera(cameraId);
        }); 
    });

    editButtons.forEach(button => {
        button.addEventListener('click', function() {
            const cameraId = getCameraId(this);
            editCamera(cameraId);
        });
    });

    function getCameraId(button) {
        const cameraFolder = button.closest('.camera-folder');
        const cameraId = cameraFolder.getAttribute('data-camera-id');
        return cameraId;
    }

    function deleteCamera(cameraId) {
        // Ajax request
        fetch('/deleteCamera' , {
            method: 'POST',
            body: new URLSearchParams({ camera_id : cameraId}),
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        })
        .then(response => response.json())
        .then(data => {
            setTimeout(() => {
                location.reload();
            }, 10);
        })
        .catch(error => console.error(error));
    }


})
function deleteCamera(cameraId) {
    var confirmDelete = confirm("¿Estas seguro de que deseas eliminar la camara?");
    if (confirmDelete) {
        $.ajax({
            url: '/deleteCameras',
            type: 'POST',
            data: {cameraId: cameraId},
            success: function(data) {
                if (data.success) {
                    alert("Ingreso");
                } else {
                    alert("Hubo un error en la eliminacion de la camara.");
                }
            }
        });
        location.reload()

    }
}
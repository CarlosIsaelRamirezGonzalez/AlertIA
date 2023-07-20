// Funcion para abrir la ventana emergente
function opentTokenModal() {
    const tokenModal = document.getElementById("tokenModal");
    tokenModal.style.display = "block";
}

// Funcion para crear la ventana emergente
function closeTokenModal() {
    const tokenModal = document.getElementById("tokenModal");
    tokenModal.style.display = "none";
}

// Verificar que el token 
function verifyToken() {
    const token = document.getElementById("tokenInput").value;
    const generatedToken = "{{ token }}";

    if ( token == generatedToken ) {
        const botonCrear = document.querySelector('.boton-crear');
        botonCrear.classList.add('token-verified');
        closeTokenModal();
    } else {
        alert("Token invalido, intentalo nuevamente");
    }
}
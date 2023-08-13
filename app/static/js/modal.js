let openModal = document.getElementById('openModal');
let modalCamera = document.getElementById('modal');
let closeModal = document.getElementById('close');

openModal.addEventListener ('click',function() {
    modalCamera.classList.add("visible");
});

modalCamera.addEventListener ('click',function(event) {
    if (event.target == modalCamera) {
        modalCamera.classList.remove("visible");
    }
});

closeModal.addEventListener ('click',function() {

    modalCamera.classList.remove("visible");

});
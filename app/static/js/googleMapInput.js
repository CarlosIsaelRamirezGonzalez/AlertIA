document.addEventListener('DOMContentLoaded', function() {
    const confirmButton = document.getElementById("close");
    const inputAddress = document.getElementById("address_input");
    const inputFormAddress = document.getElementById("form_input_address");

    confirmButton.addEventListener("click", function() {
        const addressValue = inputAddress.value;
        inputFormAddress.value = addressValue;
    });
});
function togglePasswordVisibility(fieldId) {
    const passwordInput = document.querySelector(`#${fieldId}`);
    const passwordIcon = document.getElementById(`${fieldId}-icon`);
    if (passwordInput.type == "password") {
        passwordInput.type = 'text';
        passwordIcon.classList.remove('fa-eye');
        passwordIcon.classList.add('fa-eye-slash');
    } else {
        passwordInput.type = 'password';
        passwordIcon.classList.remove('fa-eye-slash');
        passwordIcon.classList.add('fa-eye');
    }
}
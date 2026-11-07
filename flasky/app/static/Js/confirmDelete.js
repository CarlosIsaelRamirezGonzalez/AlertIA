// Pide confirmación y manda la acción por POST con el token CSRF; borrar ya no se hace con un enlace.
function confirmDeletion(url, advice) {
    if (!confirm(advice)) {
        return;
    }
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = url;
    const token = document.createElement('input');
    token.type = 'hidden';
    token.name = 'csrf_token';
    token.value = document.querySelector('meta[name="csrf-token"]').content;
    form.appendChild(token);
    document.body.appendChild(form);
    form.submit();
}

document.addEventListener("DOMContentLoaded", function() {
    document.getElementById("loader").classList.toggle("loader2");
});

window.addEventListener("beforeunload", function () {
    document.getElementById("loader").classList.toggle("loader2");
});


function confirmDeletion(url, advice) {
    if (confirm(advice)) {
        window.location.href = url;
    }
}
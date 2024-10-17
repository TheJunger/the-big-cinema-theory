document.addEventListener('DOMContentLoaded', ()=> {
    const searchInput = document.querySelector('.searchnavitem');
    const searchButton = document.querySelector('.searchnavitembutton');

    searchButton.addEventListener('click', ()=> {
        const query = searchInput.value.trim()
        if (query) {
            alert('click')
            window.location.href = `http://127.0.0.1:5000/busqueda?query=${encodeURIComponent(query)}`;
        }
    });

    searchInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            const query = searchInput.value.trim();
            if (query) {
                window.location.href = `http://127.0.0.1:5000/busqueda?query=${encodeURIComponent(query)}`;
            }
        }
    });
});
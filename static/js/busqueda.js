

document.addEventListener('DOMContentLoaded', ()=> {
    try {
        const searchInput = document.querySelector('.searchnavitem');
        const searchButton = document.querySelector('.searchnavitembutton');
    
        searchButton.addEventListener('click', ()=> {
            const query = searchInput.value.trim()
            if (query) {
                alert('click')
                window.location.href = `https://deyanger.pythonanywhere.com/busqueda?query=${encodeURIComponent(query)}`;
            }
        });
    
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                const query = searchInput.value.trim();
                if (query) {
                    window.location.href = `https://deyanger.pythonanywhere.com/busqueda?query=${encodeURIComponent(query)}`;
                }
            }
        });
    } catch (error) {
        console.warn('Busqueda deshabilitada: ', error)
    }
});
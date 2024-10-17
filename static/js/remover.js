document.addEventListener('DOMContentLoaded', () => {
    const deleteButtons = document.querySelectorAll('.delete-btn');
    
    deleteButtons.forEach(button => {
        button.addEventListener('click', () => {
            const artId = button.getAttribute('data-art-id');
            const token = document.cookie.split('; ').find(row => row.startsWith('token=')).split('=')[1];

            if (confirm('¿Estás seguro de que quieres eliminar este artículo?')) {
                fetch(`/api/eliminar-articulo/${artId}`, {
                    method: 'DELETE',
                    credentials: "include",
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                })
                .then(data => data.json())
                .then(data => {if(data.message){
                    alert(data.message)
                    window.location.href = '/perfil/1'
                    articulo.style.display = 'flex'
                }})
            }
        });
    });
});

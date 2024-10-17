document.addEventListener('DOMContentLoaded', () => {
    const destacarButton = document.querySelectorAll('.destacar');
    
    destacarButton.forEach(button => {
        button.addEventListener('click', () => {
            const artId = button.getAttribute('data-art-id');
            const token = document.cookie.split('; ').find(row => row.startsWith('token=')).split('=')[1];

            if (confirm('¿Estás seguro de que quieres destacar este artículo?')) {
                fetch(`/api/destacar-articulo/${artId}`, {
                    method: 'POST',
                    credentials: "include",
                    headers: {
                        'Authorization': `Bearer ${token}`
                    },
                    body: JSON.stringify({'destacar':true})
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

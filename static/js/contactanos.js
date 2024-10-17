document.querySelector('#contact-form').addEventListener('submit', (e)=>{
    e.preventDefault()
    const formData = new FormData(document.getElementById('contact-form'))
    

    fetch('http://localhost:5000/api/enviar-contacto', {
      method: "POST",
      body: formData,
    })
    .then(response => response.json())
    .then(data =>{
      if (data.message){
        alert(data.message)
        window.location.href ='/'
      }
    })
    .catch(e => console.error('Error: ', e))

})
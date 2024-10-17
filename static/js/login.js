document.querySelector('#loginForm').addEventListener('submit', e =>{
    e.preventDefault()
    const formData = new FormData(document.getElementById('loginForm'))
    fetch('http://localhost:5000/login', {
        method: "POST",
        body: formData,
        credentials: 'include',
        redirect: 'follow'
      })
      .then(response => response.json())
      .then(data =>{
        if (data.token){
          document.cookie = `token=${data.token}`;
          window.location.href ='/'
        }
      })
      .catch(e => console.error('Error: ', e))
  

})
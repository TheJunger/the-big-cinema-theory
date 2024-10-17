tinymce.init({
    selector: 'textarea',
    plugins: [
      // Core editing features
      'anchor', 'autolink', 'charmap', 'codesample', 'emoticons', 'image', 'link', 'lists', 'media', 'searchreplace', 'table', 'visualblocks', 'wordcount'
    ],
    toolbar: 'undo redo | blocks fontfamily fontsize | bold italic underline strikethrough | link image media table mergetags | addcomment showcomments | spellcheckdialog a11ycheck typography | align lineheight | checklist numlist bullist indent outdent | emoticons charmap | removeformat',
    tinycomments_mode: 'embedded',
    tinycomments_author: 'Author name',
    mergetags_list: [
      { value: 'First.Name', title: 'First Name' },
      { value: 'Email', title: 'Email' },
    ],
    ai_request: (request, respondWith) => respondWith.string(() => Promise.reject('See docs to implement AI Assistant')),
  });


document.querySelector('#formArticulo').addEventListener('submit', (e)=>{
    e.preventDefault()
    tinymce.triggerSave();
    const token = document.cookie.split('; ').find(row => row.startsWith('token=')).split('=')[1];
    const id_articulo = document.querySelector('.artid').value
    console.log(id_articulo)
    const formData = new FormData(document.getElementById('formArticulo'))

    fetch(`http://localhost:5000/api/editar-articulo/${id_articulo}`, {
      method: "POST",
      body: formData,
      credentials: "include",
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    .then(response => response.json())
    .then(data =>{
      if (data.message){
        alert(data.message)
        window.location.href ='/api/test/perfil'
      }
    })
    .catch(e => console.error('Error: ', e))

})
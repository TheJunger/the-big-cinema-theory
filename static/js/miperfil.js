document.querySelector(".comprobarUsuario").addEventListener("click", (e) => {
    e.preventDefault();
    const token = document.cookie
      .split("; ")
      .find((row) => row.startsWith("token="))
      .split("=")[1];
    fetch("https://deyanger.pythonanywhere.com/perfil/1", {
      method: "POST",
      credentials: "include",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
      .then((data) => data.json())
      .then((data) => {
        console.log(data);
        if (data.Auth === true) {
          let accionesarticulo = document.querySelectorAll(".accionesarticulo");
          accionesarticulo.forEach((articulo) => {
            articulo.style.display = 'flex'

          });
        }
      });
  });
  
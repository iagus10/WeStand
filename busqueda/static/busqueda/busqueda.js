document.addEventListener("DOMContentLoaded", function () {
    const input = document.getElementById("inputBusqueda");
    const resultados = document.getElementById("resultadosBusqueda");
    const dropdownBusqueda = document.getElementById('dropdownBusqueda');

    function renderResultados(data) {
        resultados.innerHTML = "";

        // Búsquedas recientes
        if (data.busquedas_recientes && data.busquedas_recientes.length) {
            resultados.innerHTML += `<h6 class="mb-1 text-primary">🔎 Búsquedas recientes</h6>`;
            data.busquedas_recientes.forEach(b => {
                resultados.innerHTML += `<div class="resultado-item py-1 px-2 mb-1 rounded bg-light text-muted" style="cursor: default;">${b}</div>`;
            });
        }

        // Usuarios
        if (data.usuarios.length) {
            resultados.innerHTML += `<h6 class="mt-3 mb-1 text-primary">👤 Perfiles</h6>`;
            data.usuarios.forEach(u => {
                const fotoHtml = u.foto_perfil
                    ? `<img src="${u.foto_perfil.startsWith('/media/') ? u.foto_perfil : '/media/' + u.foto_perfil}" class="rounded-circle me-2" style="width: 30px; height: 30px; object-fit: cover;">`
                    : `<div class="d-flex justify-content-center align-items-center rounded-circle bg-secondary text-white me-2" style="width: 30px; height: 30px;">
                            <i class="bi bi-person-fill"></i>
                       </div>`;

                resultados.innerHTML += `
                    <div class="resultado-item py-1 px-2 mb-1 rounded bg-light d-flex align-items-center">
                        ${fotoHtml}
                        <a href="/perfil/${u.username}/" class="text-decoration-none text-dark">${u.username}</a>
                    </div>`;
            });
        }
        
        // Voluntariados
        if (data.voluntariados.length) {
            resultados.innerHTML += `<h6 class="mt-3 mb-1 text-danger">🤝 Ofertas de voluntariado</h6>`;
            data.voluntariados.forEach(v => {
                resultados.innerHTML += `
                    <div class="resultado-item py-1 px-2 mb-1 rounded bg-light">
                        <a href="/voluntariados/inscripcion/${v.id}/" class="text-decoration-none text-dark d-block">
                            <strong>${v.nombre}</strong> - ${v.entidad__username}
                        </a>
                    </div>`;
            });
        }

        // Publicaciones
        if (data.publicaciones.length) {
            resultados.innerHTML += `<h6 class="mt-3 mb-1 text-success">📝 Publicaciones</h6>`;
            data.publicaciones.forEach(p => {
                resultados.innerHTML += `
                    <div class="resultado-item py-1 px-2 mb-1 rounded bg-light">
                        <a href="/perfil/${p.usuario}/?publicacion_id=${p.id}" class="text-decoration-none text-dark">
                            ${p.contenido.slice(0, 50)}...
                        </a>
                    </div>`;
            });
        }

        if (!data.usuarios.length && !data.publicaciones.length && !data.voluntariados.length && !data.busquedas_recientes.length) {
            resultados.innerHTML = `<div class="text-muted text-center">No se encontraron resultados.</div>`;
        }
    }

    function buscar(query, confirmarBusqueda = false) {
        fetch(`/busqueda/resultados/?q=${encodeURIComponent(query)}${confirmarBusqueda ? '&confirmar=1' : ''}`)
            .then(response => response.json())
            .then(data => {
   
                renderResultados(data);
            })
            .catch(err => {
                console.error("Error en búsqueda:", err);
                resultados.innerHTML = `<div class="text-danger">Error al cargar los resultados.</div>`;
            });
    }

    input.addEventListener("input", function () {
        buscar(input.value.trim(), false);
    });

    input.addEventListener("keydown", function (event) {
        if (event.key === "Enter") {
            event.preventDefault();
            buscar(input.value.trim(), true);
        }
    });

    document.addEventListener("click", function(event) {
        if (event.target.closest('#dropdownBusqueda')) {
            event.stopPropagation();
        }
    });

    // Cargar resultados iniciales
    buscar('', false);
});

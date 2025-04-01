document.addEventListener("DOMContentLoaded", function () {
    let backdrop = document.getElementById("modal-backdrop");
    let modal = document.getElementById("crud-modal");

    function mostrarFondo() {
        backdrop.classList.remove("hidden");
    }

    function ocultarFondo() {
        backdrop.classList.add("hidden");
    }

    // Si hay errores en la validación, mostrar el modal automáticamente
    if (modal.classList.contains("modal-error")) {
        modal.classList.remove("hidden");
        mostrarFondo();
    }

    // Asegurar que el botón de "Agregar" abre el modal correctamente
    document.querySelectorAll("[data-modal-toggle='crud-modal']").forEach(btn => {
        btn.addEventListener("click", function () {
            modal.classList.remove("hidden");
            mostrarFondo();
        });
    });

    // Evento para cerrar el modal de agregar
    document.querySelectorAll("[data-modal-hide='crud-modal']").forEach(btn => {
        btn.addEventListener("click", function () {
            modal.classList.add("hidden");
            ocultarFondo();
        });
    });

    // Evento para cerrar el modal con cualquier botón de cancelar
    document.querySelectorAll(".btn-cancelar").forEach(btn => {
        btn.addEventListener("click", function () {
            modal.classList.add("hidden");
            ocultarFondo();
        });
    });

    // Evento para abrir el modal de modificar (detecta múltiples botones)
    document.querySelectorAll(".btn-modificar").forEach(btn => {
        btn.addEventListener("click", function () {
            let modalModificar = document.getElementById("modificar-modal");
            modalModificar.classList.remove("hidden");
            mostrarFondo();

            // Llenar los campos del modal con los datos del proveedor
            document.querySelector("#modificar-modal input[name='id']").value = this.dataset.id;
            document.querySelector("#modificar-modal input[name='nombre']").value = this.dataset.nombre;
            document.querySelector("#modificar-modal input[name='telefono']").value = this.dataset.telefono;
            document.querySelector("#modificar-modal input[name='email']").value = this.dataset.email;
        });
    });

    // Evento para cerrar el modal de modificar con el botón "Cancelar"
    let btnCerrarModificar = document.querySelector('[data-modal-hide="modificar-modal"]');
    if (btnCerrarModificar) {
        btnCerrarModificar.addEventListener("click", function () {
            document.getElementById("modificar-modal").classList.add("hidden");
            ocultarFondo();
        });
    }

    // Evento para cerrar el modal con cualquier botón de cancelar
    document.querySelectorAll(".btn-cancelar").forEach(btn => {
        btn.addEventListener("click", function () {
            modal.classList.add("hidden");
            ocultarFondo();
        });
    });
});

 

        document.addEventListener("DOMContentLoaded", function () {
            const searchInput = document.getElementById("search-input");
            const table = document.getElementById("proveedores-table");
            const rows = table.getElementsByTagName("tr");
    
            searchInput.addEventListener("input", function () {
                const searchText = this.value.toLowerCase(); // Texto de búsqueda en minúsculas
    
                // Recorre todas las filas de la tabla (excepto la primera, que es el encabezado)
                for (let i = 1; i < rows.length; i++) {
                    const row = rows[i];
                    const cells = row.getElementsByTagName("td");
                    let found = false;
    
                    // Recorre todas las celdas de la fila
                    for (let j = 0; j < cells.length; j++) {
                        const cellText = cells[j].textContent.toLowerCase();
    
                        // Si el texto de la celda coincide con el texto de búsqueda, muestra la fila
                        if (cellText.includes(searchText)) {
                            found = true;
                            break; // No es necesario seguir buscando en esta fila
                        }
                    }
    
                    // Muestra u oculta la fila según si se encontró una coincidencia
                    row.style.display = found ? "" : "none";
                }
            });
        });
       


     
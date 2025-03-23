document.addEventListener("DOMContentLoaded", function () {
    let backdrop = document.getElementById("modal-backdrop");

    function mostrarFondo() {
        backdrop.classList.remove("hidden");
    }

    function ocultarFondo() {
        backdrop.classList.add("hidden");
    }

    // Evento para abrir el modal de agregar
    document.querySelector('[data-modal-toggle="crud-modal"]').addEventListener("click", function () {
        document.getElementById("crud-modal").classList.remove("hidden");
        mostrarFondo();
    });

    // Evento para cerrar el modal de agregar
    document.querySelector('[data-modal-hide="crud-modal"]').addEventListener("click", function () {
        document.getElementById("crud-modal").classList.add("hidden");
        ocultarFondo();
    });

    // Evento para abrir el modal de modificar (detecta múltiples botones)
    document.querySelectorAll(".btn-modificar").forEach(btn => {
        btn.addEventListener("click", function () {
            let modal = document.getElementById("modificar-modal");
            modal.classList.remove("hidden");
            mostrarFondo();

            // Llenar los campos del modal con los datos del proveedor
            document.querySelector("#modificar-modal input[name='id']").value = this.dataset.id;
            document.querySelector("#modificar-modal input[name='nombre']").value = this.dataset.nombre;
            document.querySelector("#modificar-modal input[name='telefono']").value = this.dataset.telefono;
            document.querySelector("#modificar-modal input[name='email']").value = this.dataset.email;
        });
    });

    // Evento para cerrar el modal de modificar con el botón "Cancelar"
    document.querySelector('[data-modal-hide="modificar-modal"]').addEventListener("click", function () {
        document.getElementById("modificar-modal").classList.add("hidden");
        ocultarFondo();
    });

    // Evento adicional: Si tienes otro botón de "Cancelar", también lo detectará
    document.querySelectorAll(".btn-cancelar").forEach(btn => {
        btn.addEventListener("click", function () {
            document.getElementById("modificar-modal").classList.add("hidden");
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
       
document.addEventListener("DOMContentLoaded", function () {
    // Verifica si el backdrop existe
    let backdrop = document.getElementById("modal-backdrop");
    if (!backdrop) {
        console.error("No se encontró el elemento con ID 'modal-backdrop'");
        return;
    }

    function mostrarFondo() {
        backdrop.classList.remove("hidden");
    }

    function ocultarFondo() {
        backdrop.classList.add("hidden");
    }

    // Abrir y cerrar el modal
    const abrirModalAgregar = document.querySelector('[data-modal-toggle="crud-modal"]');
    if (abrirModalAgregar) {
        abrirModalAgregar.addEventListener("click", function () {
            document.getElementById("crud-modal").classList.remove("hidden");
            mostrarFondo();
        });
    }

    const cerrarModalAgregar = document.querySelector('[data-modal-hide="crud-modal"]');
    if (cerrarModalAgregar) {
        cerrarModalAgregar.addEventListener("click", function () {
            document.getElementById("crud-modal").classList.add("hidden");
            ocultarFondo();
        });
    }

    // Agregar insumo a la tabla
    document.addEventListener("DOMContentLoaded", function () {
        // Agregar insumo a la tabla
        const agregarInsumoBtn = document.getElementById("agregar-insumo");
        if (agregarInsumoBtn) {
            agregarInsumoBtn.addEventListener("click", function () {
                const insumoSelect = document.querySelector('[name="insumos[]"]');
                const insumoCantidad = document.querySelector('[name="cantidades[]"]');
                const tablaInsumos = document.getElementById("tabla-insumos").querySelector("tbody");
    
                if (!insumoSelect || !insumoCantidad || !tablaInsumos) {
                    console.error("No se encontraron los elementos necesarios para agregar insumos");
                    return;
                }
    
                // Validar que se haya seleccionado un insumo y que la cantidad sea válida
                if (insumoSelect.value && insumoCantidad.value && insumoCantidad.value > 0) {
                    const nombreInsumo = insumoSelect.options[insumoSelect.selectedIndex].text;
                    const cantidad = insumoCantidad.value;
    
                    // Crear nueva fila
                    const newRow = tablaInsumos.insertRow();
                    newRow.innerHTML = `
                        <td>${nombreInsumo} <input type="hidden" name="insumos_seleccionados[]" value="${insumoSelect.value}"></td>
                        <td>${cantidad} <input type="hidden" name="cantidades_seleccionadas[]" value="${cantidad}"></td>
                        <td class="text-center">
                            <button type="button" class="text-red-500 hover:text-red-700 eliminar-insumo">Eliminar</button>
                        </td>
                    `;
    
                    // Limpiar campos después de agregar
                    insumoSelect.value = "";
                    insumoCantidad.value = "";
    
                    // Agregar evento para eliminar la fila
                    newRow.querySelector(".eliminar-insumo").addEventListener("click", function () {
                        tablaInsumos.deleteRow(newRow.rowIndex - 1);
                    });
    
                } else {
                    alert("Selecciona un insumo y una cantidad válida.");
                }
            });
        }
    });

    
    // Buscar en la tabla de recetas
    const searchInput = document.getElementById("search-input");
    if (searchInput) {
        searchInput.addEventListener("input", function () {
            const searchText = this.value.toLowerCase();
            const rows = document.getElementById("recetas-table").getElementsByTagName("tr");

            for (let i = 1; i < rows.length; i++) {
                const row = rows[i];
                const cells = row.getElementsByTagName("td");
                let found = false;

                for (let j = 0; j < cells.length; j++) {
                    if (cells[j].textContent.toLowerCase().includes(searchText)) {
                        found = true;
                        break;
                    }
                }

                row.style.display = found ? "" : "none";
            }
        });
    }
});

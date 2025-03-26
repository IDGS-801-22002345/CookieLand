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

    // Función para agregar insumos en el modal de modificar
    function agregarInsumoModal(recetaId) {
        const select = document.getElementById(`insumo-select-${recetaId}`);
        const cantidadInput = document.getElementById(`cantidad-input-${recetaId}`);
        const insumosContainer = document.getElementById(`insumos-actuales-${recetaId}`);
        const hiddenContainer = document.getElementById(`insumos-seleccionados-container-${recetaId}`);
        
        if (!select.value || !cantidadInput.value) {
            alert('Por favor selecciona un insumo y especifica la cantidad');
            return;
        }
        
        const insumoId = select.value;
        const insumoNombre = select.options[select.selectedIndex].getAttribute('data-nombre');
        const cantidad = cantidadInput.value;
        
        // Agregar a la lista visible
        const nuevoInsumo = document.createElement('li');
        nuevoInsumo.className = 'flex justify-between items-center mb-2 p-2 bg-gray-100 rounded';
        nuevoInsumo.innerHTML = `
            <span>${insumoNombre} - ${cantidad}</span>
            <button type="button" class="text-red-500 hover:text-red-700" onclick="eliminarInsumoLista(this)">
                <i class="fas fa-trash"></i>
            </button>
        `;
        insumosContainer.appendChild(nuevoInsumo);
        
        // Agregar campos ocultos al formulario
        const hiddenInsumo = document.createElement('input');
        hiddenInsumo.type = 'hidden';
        hiddenInsumo.name = 'insumos_seleccionados[]';
        hiddenInsumo.value = insumoId;
        
        const hiddenCantidad = document.createElement('input');
        hiddenCantidad.type = 'hidden';
        hiddenCantidad.name = 'cantidades_seleccionadas[]';
        hiddenCantidad.value = cantidad;
        
        hiddenContainer.appendChild(hiddenInsumo);
        hiddenContainer.appendChild(hiddenCantidad);
        
        // Resetear los campos
        select.value = '';
        cantidadInput.value = '1';
    }

    // Función para eliminar insumos de la lista
    function eliminarInsumoLista(button) {
        const item = button.closest('li');
        const container = item.parentElement;
        const index = Array.from(container.children).indexOf(item);
        
        // Eliminar los campos ocultos correspondientes
        const hiddenContainer = document.getElementById(`insumos-seleccionados-container-${container.id.split('-')[2]}`);
        const hiddenInputs = hiddenContainer.querySelectorAll('input');
        
        hiddenInputs[index*2].remove(); // Eliminar el input del insumo
        hiddenInputs[index*2].remove(); // Eliminar el input de la cantidad
        
        // Eliminar el elemento de la lista
        item.remove();
    }

    // Función para agregar insumos en el formulario principal
    document.getElementById('agregar-insumo')?.addEventListener('click', function() {
        const insumoSelect = document.querySelector('select[name="insumo_id"]');
        const cantidadInput = document.querySelector('input[name="cantidad"]');
        
        if (insumoSelect.value && cantidadInput.value) {
            const insumoId = insumoSelect.value;
            const insumoNombre = insumoSelect.options[insumoSelect.selectedIndex].text;
            const cantidad = cantidadInput.value;
            
            const row = document.createElement('tr');
            row.className = 'bg-white border-b dark:bg-gray-800 dark:border-gray-700';
            row.innerHTML = `
                <td class="px-6 py-4">${insumoNombre}</td>
                <td class="px-6 py-4">${cantidad}</td>
                <td class="px-6 py-4">
                    <button type="button" class="text-red-600 hover:text-red-900" onclick="this.parentNode.parentNode.remove()">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
                <input type="hidden" name="insumos_seleccionados[]" value="${insumoId}">
                <input type="hidden" name="cantidades_seleccionadas[]" value="${cantidad}">
            `;
            
            document.getElementById('insumos-agregados').appendChild(row);
            
            insumoSelect.value = '';
            cantidadInput.value = '1';
        }
    });

    // Hacer las funciones accesibles globalmente
    window.agregarInsumoModal = agregarInsumoModal;
    window.eliminarInsumoLista = eliminarInsumoLista;
});
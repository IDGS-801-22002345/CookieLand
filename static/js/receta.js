document.addEventListener("DOMContentLoaded", function() {
    // 1. Configuración del backdrop
    const backdrop = document.getElementById('modal-backdrop');
    if (!backdrop) {
        console.error('No se encontró el modal backdrop');
        return;
    }

    // 2. Funciones básicas para manejar modales
    const mostrarFondo = () => backdrop.classList.remove("hidden");
    const ocultarFondo = () => backdrop.classList.add("hidden");

    const abrirModal = (modalId) => {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.remove("hidden");
            mostrarFondo();
            document.body.classList.add('overflow-hidden');
        }
    };

    const cerrarModal = (modalId) => {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.add("hidden");
            ocultarFondo();
            document.body.classList.remove('overflow-hidden');
        }
    };

    // 3. Configurar eventos para todos los modales
    const configurarModales = () => {
        // Abrir modales
        document.querySelectorAll('[data-modal-toggle]').forEach(btn => {
            btn.addEventListener('click', () => {
                const modalId = btn.getAttribute('data-modal-toggle');
                abrirModal(modalId);
            });
        });

        // Cerrar modales
        document.querySelectorAll('[data-modal-hide]').forEach(btn => {
            btn.addEventListener('click', () => {
                const modalId = btn.getAttribute('data-modal-hide');
                cerrarModal(modalId);
            });
        });

        // Cerrar al hacer click en el backdrop
        backdrop.addEventListener('click', () => {
            document.querySelectorAll('.modal').forEach(modal => {
                if (!modal.classList.contains('hidden')) {
                    cerrarModal(modal.id);
                }
            });
        });

        // Cerrar al presionar Escape
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                document.querySelectorAll('.modal').forEach(modal => {
                    if (!modal.classList.contains('hidden')) {
                        cerrarModal(modal.id);
                    }
                });
            }
        });
    };

    // 4. Funciones específicas para formularios
    const configurarFormularios = () => {
        // Vista previa de imagen (para modal de agregar)
        document.getElementById('foto')?.addEventListener('change', function(e) {
            const file = e.target.files[0];
            const previewContainer = document.getElementById('image-preview');
            const previewImage = document.getElementById('preview-image');
            
            if (file) {
                const reader = new FileReader();
                reader.onload = function(event) {
                    previewImage.src = event.target.result;
                    previewContainer.classList.remove('hidden');
                }
                reader.readAsDataURL(file);
            } else {
                previewContainer.classList.add('hidden');
                previewImage.src = '';
            }
        });

        // Agregar insumo (modal de agregar)
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

        // Manejar envío de formularios para recargar la página
        document.querySelectorAll('form[data-reload-on-submit]').forEach(form => {
            form.addEventListener('submit', () => {
                setTimeout(() => location.reload(), 1000);
            });
        });
    };

    // Inicializar
    configurarModales();
    configurarFormularios();
});

// ==============================================
// Funciones globales para modales de modificación
// ==============================================

/**
 * Muestra una vista previa de la nueva imagen seleccionada
 * @param {Event} event - Evento change del input file
 * @param {string} recetaId - ID de la receta
 */
window.previewNuevaImagen = function(event, recetaId) {
    const file = event.target.files[0];
    const previewContainer = document.querySelector(`#modificar-modal-${recetaId} .image-preview-container`);
    const previewImage = document.querySelector(`#modificar-modal-${recetaId} .preview-image`);
    
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            previewImage.src = e.target.result;
            previewContainer?.classList.remove('hidden');
        }
        reader.readAsDataURL(file);
    } else {
        previewContainer?.classList.add('hidden');
    }
};

/**
 * Agrega un nuevo insumo al modal de edición
 * @param {string} recetaId - ID de la receta
 */
window.agregarInsumoModal = function(recetaId) {
    const select = document.getElementById(`insumo-select-${recetaId}`);
    const cantidadInput = document.getElementById(`cantidad-input-${recetaId}`);
    const listaInsumos = document.getElementById(`insumos-actuales-${recetaId}`);
    const hiddenContainer = document.getElementById(`insumos-seleccionados-container-${recetaId}`);
    
    if (!select.value || !cantidadInput.value || cantidadInput.value <= 0) {
        alert('Seleccione un insumo y especifique una cantidad válida');
        return;
    }
    
    const insumoId = select.value;
    const insumoNombre = select.options[select.selectedIndex].getAttribute('data-nombre');
    const cantidad = cantidadInput.value;
    
    // Verificar si el insumo ya fue agregado
    const inputsExistentes = hiddenContainer.querySelectorAll(`input[name="insumos_seleccionados[]"][value="${insumoId}"]`);
    if (inputsExistentes.length > 0) {
        alert('Este insumo ya ha sido agregado a la receta');
        return;
    }
    
    // Crear elemento de lista
    const listItem = document.createElement('li');
    listItem.className = 'flex justify-between items-center mb-2 p-2 bg-gray-100 rounded';
    listItem.innerHTML = `
        <span>${insumoNombre} - ${cantidad}</span>
        <button type="button" class="text-red-500 hover:text-red-700" 
            onclick="eliminarInsumoLista(this, '${recetaId}', '${insumoId}')">
            <i class="fas fa-trash"></i>
        </button>
    `;
    
    // Agregar campos ocultos
    const hiddenInsumo = document.createElement('input');
    hiddenInsumo.type = 'hidden';
    hiddenInsumo.name = 'insumos_seleccionados[]';
    hiddenInsumo.value = insumoId;
    
    const hiddenCantidad = document.createElement('input');
    hiddenCantidad.type = 'hidden';
    hiddenCantidad.name = 'cantidades_seleccionadas[]';
    hiddenCantidad.value = cantidad;
    
    // Agregar al DOM
    listaInsumos.appendChild(listItem);
    hiddenContainer.appendChild(hiddenInsumo);
    hiddenContainer.appendChild(hiddenCantidad);
    
    // Resetear campos
    select.value = '';
    cantidadInput.value = '1';
};



/**
 * Elimina un insumo de la lista de edición
 * @param {HTMLElement} button - Botón que disparó el evento
 * @param {string} recetaId - ID de la receta
 * @param {string} insumoId - ID del insumo a eliminar
 */
window.eliminarInsumoLista = function(button, recetaId, insumoId) {
    const listItem = button.closest('li');
    const hiddenContainer = document.getElementById(`insumos-seleccionados-container-${recetaId}`);
    
    // Eliminar campos ocultos correspondientes
    const inputs = hiddenContainer.querySelectorAll(`input[value="${insumoId}"]`);
    inputs.forEach(input => input.remove());
    
    // Eliminar elemento de la lista
    listItem.remove();
    
    // Mostrar mensaje si no hay insumos
    if (hiddenContainer.querySelectorAll('input[name="insumos_seleccionados[]"]').length === 0) {
        const emptyMessage = document.createElement('li');
        emptyMessage.className = 'text-gray-500 italic';
        emptyMessage.textContent = 'No hay insumos agregados';
        document.getElementById(`insumos-actuales-${recetaId}`).appendChild(emptyMessage);
    }
};

/**
 * Muestra una vista previa de imagen genérica
 * @param {Event} event - Evento change del input file
 * @param {string} previewId - ID del elemento img para la vista previa
 */
window.previewImage = function(event, previewId) {
    const file = event.target.files[0];
    const previewImage = document.getElementById(previewId);
    
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            previewImage.src = e.target.result;
        }
        reader.readAsDataURL(file);
    } else {
        previewImage.src = "{{ url_for('static', filename='img/default-receta.jpg') }}";
    }
};

/**
 * Cierra un modal específico
 * @param {string} modalId - ID del modal a cerrar
 */
window.cerrarModal = function(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add("hidden");
        document.getElementById('modal-backdrop').classList.add("hidden");
        document.body.classList.remove('overflow-hidden');
    }
};
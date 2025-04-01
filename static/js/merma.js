document.addEventListener("DOMContentLoaded", function () {
    let backdrop = document.getElementById("modal-backdrop");

    function mostrarFondo() {
        backdrop.classList.remove("hidden");
    }

    function ocultarFondo() {
        backdrop.classList.add("hidden");
    }

    // Evento para abrir el modal
    document.querySelector('[data-modal-toggle="crud-modal"]').addEventListener("click", function () {
        document.getElementById("crud-modal").classList.remove("hidden");
        mostrarFondo();
    });

    // Evento para cerrar el modal 
    document.querySelector('[data-modal-hide="crud-modal"]').addEventListener("click", function () {
        document.getElementById("crud-modal").classList.add("hidden");
        ocultarFondo();
    }); 
}); 

document.getElementById('search-input').addEventListener('input', function() {
    const searchTerm = this.value.toLowerCase();
    const rows = document.querySelectorAll('#mermas-table tbody tr');
    
    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(searchTerm) ? '' : 'none';
    });
});

function toggleMermaFields(selectedType) {
    const insumoField = document.getElementById('insumo-field');
    const galletaField = document.getElementById('galleta-field');
    
    // Ocultar ambos campos primero
    insumoField.classList.add('hidden');
    galletaField.classList.add('hidden');
    
    // Mostrar el campo correspondiente
    if (selectedType === 'insumo') {
        insumoField.classList.remove('hidden');
    } else if (selectedType === 'galleta') {
        galletaField.classList.remove('hidden');
    }
}

// Inicializar al cargar la página
document.addEventListener('DOMContentLoaded', function() {
    // Establecer el valor inicial según lo que tenga el formulario
    const tipoMermaSelect = document.querySelector('#tipo_merma');
    if (tipoMermaSelect) {
        toggleMermaFields(tipoMermaSelect.value);
        
        // Escuchar cambios
        tipoMermaSelect.addEventListener('change', function() {
            toggleMermaFields(this.value);
        });
    }
});

// Función para inicializar modales de edición
function initEditModals() {
    document.querySelectorAll('[data-modal-toggle^="modificar-modal-"]').forEach(button => {
        button.addEventListener('click', function() {
            const modalId = this.getAttribute('data-modal-target');
            const modal = document.querySelector(modalId);
            const tipoMerma = modal.querySelector('#tipo_merma').value;
            toggleMermaFields(tipoMerma);
        });
    });
}

document.addEventListener('DOMContentLoaded', initEditModals);

function toggleMermaFields(selectedType) {
    const insumoField = document.getElementById('insumo-field');
    const galletaField = document.getElementById('galleta-field');
    
    insumoField.classList.toggle('hidden', selectedType !== 'insumo');
    galletaField.classList.toggle('hidden', selectedType !== 'galleta');
}

document.addEventListener('DOMContentLoaded', function() {
    const tipoMermaSelect = document.querySelector('#tipo_merma');
    if (tipoMermaSelect) {
        toggleMermaFields(tipoMermaSelect.value);
    }
});
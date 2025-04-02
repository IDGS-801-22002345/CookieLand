// Función para alternar campos de merma (ámbito global)
function toggleMermaFields(selectedType) {
    const insumoField = document.getElementById('insumo-field');
    const galletaField = document.getElementById('galleta-field');
    
    if (insumoField && galletaField) {
        insumoField.classList.toggle('hidden', selectedType !== 'insumo');
        galletaField.classList.toggle('hidden', selectedType !== 'galleta');
    }
}

document.addEventListener("DOMContentLoaded", function() {
    // Manejo del modal y backdrop
    const backdrop = document.getElementById("modal-backdrop");
    
    function mostrarFondo() {
        if (backdrop) backdrop.classList.remove("hidden");
    }
    
    function ocultarFondo() {
        if (backdrop) backdrop.classList.add("hidden");
    }

    // Abrir modal
    const modalToggle = document.querySelector('[data-modal-toggle="crud-modal"]');
    if (modalToggle) {
        modalToggle.addEventListener("click", function() {
            const modal = document.getElementById("crud-modal");
            if (modal) {
                modal.classList.remove("hidden");
                mostrarFondo();
            }
        });
    }

    // Cerrar modal
    const modalHide = document.querySelector('[data-modal-hide="crud-modal"]');
    if (modalHide) {
        modalHide.addEventListener("click", function() {
            const modal = document.getElementById("crud-modal");
            if (modal) {
                modal.classList.add("hidden");
                ocultarFondo();
            }
        });
    }

    // Inicializar campos de merma
    const tipoMermaSelect = document.querySelector('#tipo_merma');
    if (tipoMermaSelect) {
        tipoMermaSelect.addEventListener('change', function() {
            toggleMermaFields(this.value);
        });
        
        toggleMermaFields(tipoMermaSelect.value);
    }

    // Manejo del botón Cancelar
    const btnCancelar = document.querySelector('[data-modal-hide="crud-modal"].btn-cancelar');
    if (btnCancelar) {
        btnCancelar.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Cerrar modal
            document.getElementById("crud-modal").classList.add("hidden");
            ocultarFondo();
            
            const form = document.getElementById('merma-form');
            if (form) {
                form.reset();
                const errors = form.querySelectorAll('.border-red-500');
                errors.forEach(el => el.classList.remove('border-red-500'));
            }
        });
    }

    // Manejo del formulario
    const mermaForm = document.getElementById('merma-form');
    if (mermaForm) {
        mermaForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            let isValid = true;
            const requiredFields = this.querySelectorAll('[required]');
            const cantidadField = document.getElementById('cantidad');
            const descripcionField = document.getElementById('descripcion');
            
            requiredFields.forEach(field => {
                field.classList.remove('border-red-500');
                const errorDiv = field.closest('.mb-4')?.querySelector('.invalid-feedback');
                if (errorDiv) errorDiv.style.display = 'none';
            });
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    isValid = false;
                    field.classList.add('border-red-500');
                    const errorDiv = field.closest('.mb-4')?.querySelector('.invalid-feedback');
                    if (errorDiv) errorDiv.style.display = 'block';
                }
            });
            
            if (cantidadField && cantidadField.value && parseInt(cantidadField.value) <= 0) {
                isValid = false;
                cantidadField.classList.add('border-red-500');
            }
            
            if (!isValid) {
                const firstError = this.querySelector('.border-red-500');
                if (firstError) firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
                return;
            }

            Swal.fire({
                title: '¿Confirmar registro de merma?',
                html: `
                    <div class="text-left">
                        <p><strong>Descripción:</strong> ${descripcionField?.value || ''}</p>
                        <p><strong>Cantidad:</strong> ${cantidadField?.value || ''}</p>
                        <p><strong>Tipo:</strong> ${tipoMermaSelect?.value?.charAt(0).toUpperCase() + tipoMermaSelect?.value?.slice(1) || ''}</p>
                    </div>
                `,
                icon: 'question',
                showCancelButton: true,
                confirmButtonColor: '#24985a',
                cancelButtonColor: '#d33',
                confirmButtonText: 'Sí, registrar',
                cancelButtonText: 'Cancelar',
                customClass: {
                    popup: 'text-sm'
                }
            }).then((result) => {
                if (result.isConfirmed) {
                    this.submit();
                }
            });
        });
    }
});
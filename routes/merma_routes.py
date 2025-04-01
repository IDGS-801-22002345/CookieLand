from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.models import Merma, db, InventarioMateria, Galleta, MateriaPrima, InventarioGalletas
from forms.merma_forms import MermaForm

merma_bp = Blueprint('merma_bp', __name__, url_prefix='/merma')

@merma_bp.route("/")
def index():
    create_form = MermaForm(request.form)
    
    materias = db.session.query(InventarioMateria.id, MateriaPrima.nombre).join(MateriaPrima).all()
    create_form.inventario_materia_id.choices = [(m.id, m.nombre) for m in materias]
    
    galletas = Galleta.query.all()
    create_form.inventario_galletas_id.choices = [(g.id, g.nombre) for g in galletas]

    mermas = Merma.query.all()
    return render_template("merma/merma.html", form=create_form, mermas=mermas)


from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.models import Merma, db, InventarioMateria, Galleta, MateriaPrima, InventarioGalletas
from forms.merma_forms import MermaForm
import traceback  # Importamos traceback para mejor manejo de errores

merma_bp = Blueprint('merma_bp', __name__, url_prefix='/merma')

@merma_bp.route("/")
def index():
    print("\n=== INICIO DE INDEX ===")
    create_form = MermaForm(request.form)
    
    print("\nObteniendo materias primas...")
    materias = db.session.query(InventarioMateria.id, MateriaPrima.nombre).join(MateriaPrima).all()
    print(f"Encontradas {len(materias)} materias primas")
    create_form.inventario_materia_id.choices = [(m.id, m.nombre) for m in materias]
    
    print("\nObteniendo galletas...")
    galletas = Galleta.query.all()
    print(f"Encontradas {len(galletas)} galletas")
    create_form.inventario_galletas_id.choices = [(g.id, g.nombre) for g in galletas]

    print("\nObteniendo mermas existentes...")
    mermas = Merma.query.all()
    print(f"Existen {len(mermas)} mermas registradas")
    
    print("\n=== FIN DE INDEX ===")
    return render_template("merma/merma.html", form=create_form, mermas=mermas)

@merma_bp.route("/crear", methods=['POST'])
def crear():
    print("\n=== INICIO DE CREAR ===")
    print(f"Datos del formulario recibidos: {request.form}")
    
    create_form = MermaForm(request.form)
    
    print("\nConfigurando opciones de materias primas...")
    materias = db.session.query(InventarioMateria.id, MateriaPrima.nombre).join(MateriaPrima).all()
    create_form.inventario_materia_id.choices = [(m.id, m.nombre) for m in materias]
    print(f"Opciones de materias: {create_form.inventario_materia_id.choices}")
    
    print("\nConfigurando opciones de galletas...")
    galletas = Galleta.query.all()
    create_form.inventario_galletas_id.choices = [(g.id, g.nombre) for g in galletas]
    print(f"Opciones de galletas: {create_form.inventario_galletas_id.choices}")

    if create_form.validate():
        print("\nFormulario validado correctamente")
        print(f"Datos del formulario: {create_form.data}")
        
        tipo_merma = create_form.tipo_merma.data
        cantidad = create_form.cantidad.data
        inventario_materia_id = create_form.inventario_materia_id.data if tipo_merma == 'insumo' else None
        inventario_galletas_id = create_form.inventario_galletas_id.data if tipo_merma == 'galleta' else None

        print(f"\nDatos extraídos:")
        print(f"Tipo merma: {tipo_merma}")
        print(f"Cantidad: {cantidad}")
        print(f"ID Materia Prima: {inventario_materia_id}")
        print(f"ID Galletas: {inventario_galletas_id}")

        if inventario_galletas_id:
            print("\nValidando inventario de galletas...")
            inventario_galletas = InventarioGalletas.query.get(inventario_galletas_id)
            print(f"Inventario encontrado: {inventario_galletas}")
            if not inventario_galletas:
                print("Error: Inventario de galletas no encontrado")
                flash('Error: Inventario de galletas no encontrado.', 'danger')
                return redirect(url_for('merma_bp.index'))

        if inventario_materia_id:
            print("\nValidando inventario de materias...")
            inventario_materia = InventarioMateria.query.get(inventario_materia_id)
            print(f"Inventario encontrado: {inventario_materia}")
            if not inventario_materia:
                print("Error: Inventario de insumos no encontrado")
                flash('Error: Inventario de insumos no encontrado.', 'danger')
                return redirect(url_for('merma_bp.index'))

        print("\nCreando objeto merma...")
        merma = Merma(
            descripcion=create_form.descripcion.data,
            cantidad=cantidad,
            tipo_merma=tipo_merma,
            inventario_materia_id=inventario_materia_id,
            inventario_galletas_id=inventario_galletas_id
        )
        print(f"Objeto merma creado: {merma}")
        db.session.add(merma)

        if tipo_merma == 'insumo' and inventario_materia_id:
            print("\nActualizando inventario de materias...")
            print(f"Cantidad actual: {inventario_materia.cantidad}")
            print(f"Cantidad a restar: {cantidad}")
            if inventario_materia and inventario_materia.cantidad >= cantidad:
                inventario_materia.cantidad -= cantidad
                print(f"Nueva cantidad: {inventario_materia.cantidad}")
            else:
                print("Error: Cantidad insuficiente")
                flash('Error: Cantidad insuficiente en inventario de insumos.', 'danger')
                db.session.rollback()
                return redirect(url_for('merma_bp.index'))
        
        if tipo_merma == 'galleta' and inventario_galletas_id:
            print("\nActualizando inventario de galletas...")
            print(f"Cantidad actual: {inventario_galletas.cantidad}")
            print(f"Cantidad a restar: {cantidad}")
            if inventario_galletas and inventario_galletas.cantidad >= cantidad:
                inventario_galletas.cantidad -= cantidad
                print(f"Nueva cantidad: {inventario_galletas.cantidad}")
            else:
                print("Error: Cantidad insuficiente")
                flash('Error: Cantidad insuficiente en inventario de galletas.', 'danger')
                db.session.rollback()
                return redirect(url_for('merma_bp.index'))
        
        print("\nIntentando commit...")
        db.session.commit()
        print("Commit realizado con éxito")
        flash('Merma creada correctamente', 'success')
    else:
        print("\nError en validación del formulario")
        print(f"Errores: {create_form.errors}")
        flash('Error al crear la merma', 'danger')
    
    print("=== FIN DE CREAR ===")
    return redirect(url_for('merma_bp.index'))


@merma_bp.route("/modificar/<int:id>", methods=['GET', 'POST'])
def modificar(id):
    print(f"\n=== INICIO DE MODIFICAR (ID: {id}) ===")
    merma = Merma.query.get(id)
    if not merma:
        print("Merma no encontrada")
        flash("Merma no encontrada", "error")
        return redirect(url_for('merma_bp.index'))

    create_form = MermaForm(request.form)
    
    print("\nObteniendo listas de insumos y galletas...")
    insumos = InventarioMateria.query.all()
    galletas = InventarioGalletas.query.all()
    print(f"Encontrados {len(insumos)} insumos y {len(galletas)} galletas")

    if request.method == 'GET':
        print("\nMétodo GET - Mostrando formulario")
        create_form.descripcion.data = merma.descripcion
        create_form.cantidad.data = merma.cantidad
        create_form.tipo_merma.data = merma.tipo_merma
        create_form.inventario_materia_id.data = merma.inventario_materia_id
        create_form.inventario_galletas_id.data = merma.inventario_galletas_id
        
        print("Datos cargados en formulario:")
        print(f"Descripción: {create_form.descripcion.data}")
        print(f"Cantidad: {create_form.cantidad.data}")
        print(f"Tipo merma: {create_form.tipo_merma.data}")
        print(f"ID Materia: {create_form.inventario_materia_id.data}")
        print(f"ID Galletas: {create_form.inventario_galletas_id.data}")
        
        return render_template('merma/modificar.html', 
                            form=create_form,
                            merma=merma,
                            insumos=insumos,
                            galletas=galletas)

    if request.method == 'POST':
        print("\nMétodo POST - Procesando formulario")
        print(f"Datos recibidos: {request.form}")
        
        if create_form.validate():
            print("\nFormulario validado correctamente")
            merma.descripcion = create_form.descripcion.data
            merma.cantidad = create_form.cantidad.data
            merma.tipo_merma = create_form.tipo_merma.data
            merma.inventario_materia_id = create_form.inventario_materia_id.data
            merma.inventario_galletas_id = create_form.inventario_galletas_id.data
            
            print("\nDatos actualizados:")
            print(f"Descripción: {merma.descripcion}")
            print(f"Cantidad: {merma.cantidad}")
            print(f"Tipo: {merma.tipo_merma}")
            print(f"ID Materia: {merma.inventario_materia_id}")
            print(f"ID Galletas: {merma.inventario_galletas_id}")
            
            db.session.commit()
            print("Cambios guardados en base de datos")
            flash('Merma modificada correctamente', 'success')
        else:
            print("\nError en validación del formulario")
            print(f"Errores: {create_form.errors}")
            flash('Error al modificar la merma', 'danger')
    
    print("=== FIN DE MODIFICAR ===")
    return redirect(url_for('merma_bp.index')) 
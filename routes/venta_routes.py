from flask import Blueprint, Response, render_template, request, redirect, send_from_directory, url_for, flash, jsonify
from models.models import Galleta, db, Venta, DetalleVenta
from forms.venta_forms import VentaForm
from utils.decoradores import login_required, log_excepciones, role_required
from functools import wraps

ventas_bp = Blueprint('ventas_bp', __name__, url_prefix='/ventas')

class VentaActual:
    def __init__(self):
        self.detalles = []
        self.total = 0.0
        self.productos= 0
    
    def agregar_producto(self, galleta_id, nombre, cantidad, precio):
        for item in self.detalles:
            if item['id'] == galleta_id:
                item['cantidad'] += cantidad
                item['subtotal'] = item['cantidad'] * item['precio']
                self.calcular_total()
                return False  
        
        nuevo_item = {
            'id': galleta_id,
            'galleta': nombre,
            'cantidad': cantidad,
            'precio': precio,
            'subtotal': cantidad * precio
        }
        self.detalles.append(nuevo_item)
        self.calcular_total()
        self.totalProductos()
        return True  
    
    def calcular_total(self):
        self.total = sum(item['subtotal'] for item in self.detalles)
    def totalProductos(self):
        self.productos = sum(item['cantidad'] for item in self.detalles)
    
    def limpiar_venta(self):
        self.detalles = []
        self.total = 0.0
        self.productos = 0

venta_actual = VentaActual()

@ventas_bp.route("/")
@login_required
@log_excepciones
@role_required('admin', 'vendedor')
def index():
    ventaForm = VentaForm()
    galletas = Galleta.query.options(
        db.joinedload(Galleta.receta)
    ).filter(
        Galleta.estatus == 1  
    ).order_by(
        Galleta.nombre.asc()  
    ).all()
    return render_template(
        "venta/venta.html", 
        galletas=galletas, 
        form=ventaForm, 
        detalles_venta=venta_actual.detalles,
        total=venta_actual.total,
        productos=venta_actual.productos
    )

@ventas_bp.route('/imagen/<int:galleta_id>')
def mostrar_imagen(galleta_id):
    galleta = Galleta.query.get_or_404(galleta_id)
    if not galleta.foto:
        return send_from_directory('static', 'images/default-cookie.png')
    return Response(galleta.foto, mimetype='image/jpeg')


@ventas_bp.route("/eliminar_galleta", methods=["POST"])
@login_required
@log_excepciones
@role_required('admin', 'vendedor')
def eliminar_galleta():
    try:
        galleta_id = int(request.form.get('galleta_id'))
        
        for i, item in enumerate(venta_actual.detalles):
            if item['id'] == galleta_id:
                venta_actual.detalles.pop(i)
                venta_actual.calcular_total()
                flash('Producto eliminado de la venta', 'success')
                return redirect(url_for('ventas_bp.index'))
        
        flash('Producto no encontrado en la venta', 'error')
    
    except ValueError:
        flash('ID de producto no válido', 'error')
    except Exception as e:
        flash(f'Error al eliminar el producto: {str(e)}', 'error')
    
    return redirect(url_for('ventas_bp.index'))

@ventas_bp.route("/add_galleta", methods=["POST"])
@login_required
@log_excepciones
@role_required('admin', 'vendedor')
def add_galleta():
    ventaForm = VentaForm(request.form)
    if not ventaForm.validate():
        for field, errors in ventaForm.errors.items():
            for error in errors:
                flash(f"Error en {field}: {error}", 'error')
        return redirect(url_for('ventas_bp.index'))
    
    try:
        galleta_id = int(request.form.get('galleta_id'))
        presentacion = int(ventaForm.presentacion.data)
        cantidad = int(ventaForm.cantidad.data)
        
        galleta = Galleta.query.get_or_404(galleta_id)
        
        if presentacion == 1:  
            unidades_a_agregar  = cantidad
        elif presentacion == 2:  
            unidades_a_agregar  = cantidad * 30
        elif presentacion == 3: 
            unidades_a_agregar  = cantidad * 24
        else:
            flash('Presentación no válida', 'error')
            return redirect(url_for('ventas_bp.index'))
        
        if galleta.stock < unidades_a_agregar:
            flash(f'No hay suficiente stock. Disponible: {galleta.stock} unidades', 'error')
            return redirect(url_for('ventas_bp.index'))

        item_existente = next((item for item in venta_actual.detalles if item['id'] == galleta_id), None)
        total_en_carrito = unidades_a_agregar + (item_existente['cantidad'] if item_existente else 0)

        if total_en_carrito > galleta.stock:
            disponible = galleta.stock - (item_existente['cantidad'] if item_existente else 0)
            flash(f'No hay suficiente stock. Puedes agregar hasta {disponible} unidades más', 'error')
            return redirect(url_for('ventas_bp.index'))
        
        fue_nuevo = venta_actual.agregar_producto(
            galleta_id=galleta_id,
            nombre=galleta.nombre,
            cantidad=unidades_a_agregar ,
            precio=float(galleta.precio)
        )  
    
        mensaje = 'Producto agregado correctamente' if fue_nuevo else 'Cantidad actualizada correctamente'
        flash(mensaje, 'success')
        
    except ValueError as e:
        flash('Error en los datos proporcionados: valores no válidos', 'error')
    except Exception as e:
        flash(f'Error al procesar la venta: {str(e)}', 'error')
    
    return redirect(url_for('ventas_bp.index'))


@ventas_bp.route("/limpiar_venta", methods=["POST"])
@login_required
@log_excepciones
@role_required('admin', 'vendedor')
def limpiar_venta():
    try:
        venta_actual.limpiar_venta()
        flash('Venta limpiada correctamente', 'success')
    except Exception as e:
        flash(f'Error al limpiar la venta: {str(e)}', 'error')
    
    return redirect(url_for('ventas_bp.index'))


@ventas_bp.route("/realizar_venta", methods=["POST"])
@login_required
@log_excepciones
@role_required('admin', 'vendedor')
def realizar_venta():
    try:
        if not venta_actual.detalles:
            flash('No hay productos en la venta', 'error')
            return redirect(url_for('ventas_bp.index'))
        nueva_venta = Venta(
            total=venta_actual.total,
        )

        for item in venta_actual.detalles:
            detalle = DetalleVenta(
                galleta_id=item['id'],
                cantidad=item['cantidad'],
                precio_unitario=item['precio']
            )
            nueva_venta.detalles.append(detalle)

            galleta = Galleta.query.get(item['id'])
            galleta.stock -= item['cantidad']
            if galleta.stock < 0:  
                galleta.stock = 0
            db.session.add(galleta)

        db.session.add(nueva_venta)
        db.session.commit()

        venta_actual.limpiar_venta()

        flash('Venta registrada exitosamente', 'success')
        return redirect(url_for('ventas_bp.index'))

    except Exception as e:
        db.session.rollback()
        flash(f'Error al procesar la venta: {str(e)}', 'error')
        return redirect(url_for('ventas_bp.index'))
import datetime
from sqlite3 import IntegrityError
from flask import Blueprint, Response, render_template, request, redirect, send_from_directory, url_for, flash
from models.models import Produccion, Galleta
from models.models import db, Produccion
from utils.decoradores import *
from forms.produccion_forms import ProduccionForm

produccion_bp = Blueprint('produccion_bp', __name__, url_prefix='/produccion')


# Pagina de Produccion

@produccion_bp.route("/")
@login_required
@log_excepciones
@role_required('admin', 'produccion')
def index():
    galletas = Galleta.query.options(
        db.joinedload(Galleta.receta)
    ).filter(
        Galleta.estatus == 1  
    ).order_by(
        Galleta.nombre.asc()  
    )
    return render_template("produccion/produccion.html", galletas=galletas)

@produccion_bp.route('/imagen/<int:galleta_id>')
@login_required
@log_excepciones
@role_required('admin', 'produccion')
def mostrar_imagen(galleta_id):
    galleta = Galleta.query.get_or_404(galleta_id)
    if not galleta.foto:
        return send_from_directory('static', 'images/default-cookie.png')
    return Response(galleta.foto, mimetype='image/jpeg')  

# Pagina de Produccion-prod

@produccion_bp.route("/abrirmodal", methods=["POST"])
@login_required
@log_excepciones
@role_required('admin')
def abrir_modal():
    form = ProduccionForm()
    galletas = Galleta.query.options(
        db.joinedload(Galleta.receta)
    ).filter(
        Galleta.estatus == 1  
    ).order_by(
        Galleta.nombre.asc()  
    )
    pedidos_pendientes = Pedido.query.options(
        db.joinedload(Pedido.usuario),
        db.joinedload(Pedido.detalles).joinedload(DetallePedido.galleta)
    ).filter(
        Pedido.estatus == 'En proceso'
    ).order_by(
        Pedido.fecha_recoleccion.asc(),
        Pedido.hora_recoleccion.asc()
    ).all()
    producciones = Produccion.query.options(
        db.joinedload(Produccion.galleta)
    ).filter(
        Produccion.estadoProduccion.in_(["Proceso", "Horneado"])
    ).all()
    
    return render_template("produccion/produccionProd.html", 
                         galletas=galletas, 
                         form=form,
                         modalPedido = False,
                         pedidos_pendientes=pedidos_pendientes,
                         modal=True, 
                         producciones=producciones)


from collections import defaultdict

@produccion_bp.route("/abrirmodalPedido", methods=["POST"])
@login_required
@log_excepciones
@role_required('admin')
def abrir_modalPedido():
    form = ProduccionForm()
    pedido_id = int(request.form.get('pedido_id'))

    galletas = Galleta.query.options(
        db.joinedload(Galleta.receta)
    ).filter(
        Galleta.estatus == 1  
    ).order_by(
        Galleta.nombre.asc()
    )

    pedidos_pendientes = Pedido.query.options(
        db.joinedload(Pedido.usuario),
        db.joinedload(Pedido.detalles).joinedload(DetallePedido.galleta)
    ).filter(
        Pedido.estatus == 'En proceso'
    ).order_by(
        Pedido.fecha_recoleccion.asc(),
        Pedido.hora_recoleccion.asc()
    ).all()

    pedido_especifico = Pedido.query.options(
        db.joinedload(Pedido.usuario),
        db.joinedload(Pedido.detalles).joinedload(DetallePedido.galleta)
    ).get(pedido_id)

    galletas_agrupadas = {}
    for detalle in pedido_especifico.detalles:
        galleta = detalle.galleta
        galleta_id = galleta.id

        if galleta_id not in galletas_agrupadas:
            galletas_agrupadas[galleta_id] = {
                "galleta": galleta,
                "cantidad": detalle.cantidad,
                "subtotal": detalle.cantidad * galleta.precio
            }
        else:
            galletas_agrupadas[galleta_id]["cantidad"] += detalle.cantidad
            galletas_agrupadas[galleta_id]["subtotal"] += detalle.cantidad * galleta.precio

    return render_template("produccion/produccionProd.html",
                           galletas=galletas,
                           form=form,
                           modalPedido=True,
                           pedidos_pendientes=pedidos_pendientes,
                           modal=False,
                           pedido_especifico=pedido_especifico,
                           galletas_agrupadas=list(galletas_agrupadas.values()))


@produccion_bp.route("/cerrarmodal", methods=["POST"])
@login_required
@log_excepciones
@role_required('admin')
def cerrar_modal():
 return redirect(url_for('produccion_bp.prod'))

@produccion_bp.route("/produccion-prod")
@login_required
@log_excepciones
@role_required('admin', 'produccion')
def prod():
    form = ProduccionForm()
    galletas = Galleta.query.options(
        db.joinedload(Galleta.receta)
    ).filter(
        Galleta.estatus == 1  
    ).order_by(
        Galleta.nombre.asc()  
    )
    pedidos_pendientes = Pedido.query.options(
        db.joinedload(Pedido.usuario),
        db.joinedload(Pedido.detalles).joinedload(DetallePedido.galleta)
    ).filter(
        Pedido.estatus == 'En proceso'
    ).order_by(
        Pedido.fecha_recoleccion.asc(),
        Pedido.hora_recoleccion.asc()
    ).all()
    producciones = Produccion.query.options(
        db.joinedload(Produccion.galleta)
    ).all()
    return render_template("produccion/produccionProd.html",
                           galletas=galletas,
                           modalPedido=False,
                            form=form, modal=False,
                            producciones=producciones, pedidos_pendientes=pedidos_pendientes)


@produccion_bp.route("/producir", methods=["POST"])
@login_required
@log_excepciones
@role_required('admin', 'produccion')
def producir():
    form = ProduccionForm()
    if not form.validate_on_submit():
        flash("Error en el formulario de producción", "error")
        return redirect(url_for('produccion_bp.prod'))
    
    galleta_id = request.form.get("galleta_id")
    cantidad = form.cantidad.data
    galleta = Galleta.query.get(galleta_id)
    
    if not galleta:
        flash("Galleta no encontrada", "error")
        return redirect(url_for('produccion_bp.prod'))
    
    insuficientes = []
    for detalle in galleta.receta.detalles:
        cantidad_necesaria = detalle.cantidad * cantidad
        inventario = detalle.insumo.inventario
        
        if not inventario or inventario.cantidad < cantidad_necesaria:
            insuficientes.append({
                'insumo': detalle.insumo.nombre,
                'necesario': cantidad_necesaria,
                'disponible': inventario.cantidad if inventario else 0
            })
    
    if insuficientes:
        mensaje = "Insumos insuficientes: "
        for item in insuficientes:
            mensaje += f"- {item['insumo']}: Necesario {item['necesario']}, Disponible {item['disponible']}\n"
        flash(mensaje, "error")
        return redirect(url_for('produccion_bp.prod'))
    
    try:
        
        for detalle in galleta.receta.detalles:
            cantidad_necesaria = detalle.cantidad * cantidad
            detalle.insumo.inventario.cantidad -= cantidad_necesaria

            if inventario.cantidad <= 0:
                inventario.estado_stock = "Agotado"
            elif inventario.cantidad < inventario.cantidad_minima:
                inventario.estado_stock = "Bajo"
            else:
                inventario.estado_stock = "Completo"
            
            detalle.insumo.inventario.update_date = datetime.datetime.now()
        
        for i in range(cantidad):
            nueva_produccion = Produccion(
                galleta_id=galleta.id,
                estadoProduccion="Proceso",
                fechaDeProduccion=datetime.datetime.now()
            )
            db.session.add(nueva_produccion)
                
        
        db.session.commit()
        flash(f"Producción de {cantidad} {galleta.nombre} iniciada con éxito", "success")
        
    except Exception as e:
        db.session.rollback()
        flash(f"Error al iniciar la producción: {str(e)}", "error")
    
    return redirect(url_for('produccion_bp.prod'))

@produccion_bp.route("/horneado", methods=["POST"])
@login_required
@log_excepciones
@role_required('admin', 'produccion')
def horneado():
    form = ProduccionForm()
    
    if not form.validate_on_submit():
        flash("Error en el formulario de producción", "error")
        return redirect(url_for('produccion_bp.prod'))
    
    produccion_id = request.form.get("produccion_id")   
    produccion = Produccion.query.get(produccion_id)
    if not produccion:
        flash("Producción no encontrada", "error")
        return redirect(url_for('produccion_bp.prod'))
    
    try:
        produccion.estadoProduccion = "Horneado"
        produccion.fechaDeHorneado = datetime.datetime.now()
        
        db.session.commit()
        flash(f"Producción {produccion.id}ID actualizada a 'Horneado'", "success")
        
    except IntegrityError as e:
        db.session.rollback()
        flash("Error de base de datos al actualizar la producción", "error")
    except Exception as e:
        db.session.rollback()
        flash(f"Error al cambiar la producción: {str(e)}", "error")
    
    return redirect(url_for('produccion_bp.prod'))


@produccion_bp.route("/finalizar", methods=["POST"])
@login_required
@log_excepciones
@role_required('admin', 'produccion')
def finalizar():

    form = ProduccionForm()
    
    if not form.validate_on_submit():
        flash("Error en el formulario de producción", "error")
        return redirect(url_for('produccion_bp.prod'))
    
    produccion_id = request.form.get("produccion_id")   
    produccion = Produccion.query.get(produccion_id)
    if not produccion:
        flash("Producción no encontrada", "error")
        return redirect(url_for('produccion_bp.prod'))
    
    try:
        produccion.estadoProduccion = "Finalizado"
        produccion.fechaFinalizacion = datetime.datetime.now()

        galleta= Galleta.query.get(produccion.galleta_id)
        galleta.stock += 30 
        galleta.estadoStock = "Completo" 
        db.session.commit()
        flash(f"Producción {produccion.id} finalizada exitosamente. Stock de {galleta.nombre} actualizado", "success")
        
    except IntegrityError as e:
        db.session.rollback()
        flash("Error de base de datos al finalizar la producción", "error")
    except Exception as e:
        db.session.rollback()
        flash(f"Error al finalizar la producción: {str(e)}", "error")
    
    return redirect(url_for('produccion_bp.prod'))



@produccion_bp.route("/pedidoListo", methods=["POST"])
@login_required
@log_excepciones
@role_required('admin')
def pedidoListo():
    pedido_id = int(request.form.get('pedido_id'))
    
    pedido = Pedido.query.get(pedido_id)
    if pedido:
        pedido.estatus = 'Listo para recoger' 
        db.session.commit()
        flash('El estado del pedido esta Listo para recoger', 'success')
    else:
        flash('Pedido no encontrado', 'error')
    
    return redirect(url_for('produccion_bp.prod'))

from flask import Blueprint, Response, json, jsonify, render_template, render_template_string, send_from_directory, session
from utils.decoradores import *
from datetime import datetime
from sqlalchemy.orm import joinedload

cliente_bp = Blueprint('cliente_bp', __name__, url_prefix='/')


# Ruta de layout
@cliente_bp.route('/layout')
@log_excepciones
@login_required
def layout():
    return render_template('cliente/layout.html')


@cliente_bp.route('/')
@log_excepciones
def index():
    # Verificar si el usuario está autenticado
    if 'user_id' in session:
        username = session['username']
        email = session['email']
        return render_template('cliente/index.html',
                               username=username,
                               correo=email)
    else:
        return render_template('cliente/index.html')


# Ruta de nosotros
@cliente_bp.route('/nosotros')
@log_excepciones
def nosotros():
    return render_template('cliente/nosotros.html')


# Ruta de la galeria de calletas
@cliente_bp.route('/galeria')
@log_excepciones
def geleria():
    return render_template('cliente/galeria.html')


# Ruta de contacto
@cliente_bp.route('/contacto')
@log_excepciones
def contacto():
    return render_template('cliente/contacto.html')


# Ruta de aviso de privacidad
@cliente_bp.route('/aviso-de-privacidad')
@log_excepciones
def avisodeprivacidad():
    return render_template('cliente/avisodeprivacidad.html')


# Ruta de terminos y condiciones
@cliente_bp.route('/terminos-y-condiciones')
@log_excepciones
def terminosycondiciones():
    return render_template('cliente/terminosycondiciones.html')


# Ruta de productos
@cliente_bp.route('/productos')
def productos():
    galletas = Galleta.query.options(db.joinedload(Galleta.receta)).filter(
        Galleta.estatus == 1).order_by(Galleta.nombre.asc())
    return render_template('cliente/productos.html', galletas=galletas)


# Ruta para mostrar imagenes del las galletas
@cliente_bp.route('/imagen/<int:galleta_id>')
def mostrar_imagen(galleta_id):
    galleta = Galleta.query.get_or_404(galleta_id)
    if not galleta.foto:
        return send_from_directory('static', 'images/default-cookie.png')
    return Response(galleta.foto, mimetype='image/jpeg')


# Agregar al carrito
@cliente_bp.route('/agregar-al-carrito', methods=['POST'])
@login_required
@role_required('cliente')
@log_excepciones
def agregar_al_carrito():
    galleta_id = request.form.get('galleta_id')
    cantidad = int(request.form.get('cantidad', 1))
    presentacion = request.form.get('presentacion', 'pieza')

    if not galleta_id or cantidad < 1:
        flash('Datos inválidos', 'danger')
        return redirect(url_for('cliente_bp.productos'))

    galleta = Galleta.query.get(galleta_id)
    if not galleta:
        flash('Galleta no encontrada', 'danger')
        return redirect(url_for('cliente_bp.productos'))
    if presentacion == "caja":
        piezas = cantidad * 30
        precio_unitario = galleta.precio * 30
    elif presentacion == "kilo":
        piezas = cantidad * 24
        precio_unitario = galleta.precio * 24
    else:
        piezas = cantidad
        precio_unitario = galleta.precio

    carrito = session.get('carrito', [])
    if not isinstance(carrito, list):
        carrito = []

    ya_en_carrito = False
    for item in carrito:
        if item['galleta_id'] == int(
                galleta_id) and item['presentacion'] == presentacion:
            item['cantidad'] += cantidad
            item['piezas'] += piezas
            ya_en_carrito = True
            break

    if not ya_en_carrito:
        carrito.append({
            'galleta_id': int(galleta_id),
            'nombre': galleta.nombre,
            'precio': precio_unitario,
            'presentacion': presentacion,
            'cantidad': cantidad,
            'piezas': piezas
        })

    session['carrito'] = carrito

    existente = CarritoTemporal.query.filter_by(
        usuario_id=current_user.id,
        galleta_id=galleta.id,
        presentacion=presentacion).first()

    if existente:
        existente.cantidad += cantidad
    else:
        nuevo = CarritoTemporal(usuario_id=current_user.id,
                                galleta_id=galleta.id,
                                cantidad=cantidad,
                                presentacion=presentacion)
        db.session.add(nuevo)

    db.session.commit()

    flash("Producto agregado al carrito", "success")
    return redirect(url_for('cliente_bp.productos'))


# Ruta para confirmar el pedido
@cliente_bp.route('/confirmar-pedido', methods=['POST'])
@login_required
@role_required('cliente')
def confirmar_pedido():
    carrito = session.get('carrito', [])
    if not carrito:
        flash(
            'Tu carrito está vacío. Agrega productos antes de confirmar el pedido.',
            'warning')
        return redirect(url_for('cliente_bp.carrito_compras'))

    fecha_str = request.form.get('fecha')
    hora = request.form.get('hora')
    if not fecha_str or not hora:
        flash('Por favor selecciona la fecha y hora de recolección.', 'danger')
        return redirect(url_for('cliente_bp.carrito_compras'))

    try:
        from datetime import datetime
        fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
    except ValueError:
        flash('Fecha inválida.', 'danger')
        return redirect(url_for('cliente_bp.carrito_compras'))

    total = sum(item['precio'] * item['cantidad'] for item in carrito)

    pedido = Pedido(usuario_id=current_user.id,
                    fecha_recoleccion=fecha,
                    hora_recoleccion=hora,
                    total=total,
                    estatus="En proceso")
    db.session.add(pedido)
    db.session.flush()

    for item in carrito:
        if item['presentacion'] == 'caja':
            piezas = item['cantidad'] * 30
            precio_unitario = item['precio'] / 30
        elif item['presentacion'] == 'kilo':
            piezas = item['cantidad'] * 24
            precio_unitario = item['precio'] / 24
        else:
            piezas = item['cantidad']
            precio_unitario = item['precio']

        detalle = DetallePedido(pedido_id=pedido.id,
                                galleta_id=item['galleta_id'],
                                cantidad=piezas,
                                precio_unitario=precio_unitario,
                                presentacion=item['presentacion'])
        db.session.add(detalle)

    CarritoTemporal.query.filter_by(usuario_id=current_user.id).delete()
    db.session.commit()
    session.pop('carrito', None)

    flash('Pedido confirmado con éxito.', 'success')
    return redirect(url_for('auth_bp.orders'))


# Ruta para ver los detelles del pedido
@cliente_bp.route('/detalle-pedido/<int:pedido_id>')
@login_required
@role_required('cliente')
def detalle_pedido(pedido_id):
    pedido = Pedido.query.filter_by(id=pedido_id,
                                    usuario_id=current_user.id).first_or_404()
    detalles = DetallePedido.query.options(joinedload(
        DetallePedido.galleta)).filter_by(pedido_id=pedido.id).all()

    return render_template_string("""
    <div class="w-full max-w-6xl mx-auto bg-white p-8 rounded-2xl shadow-xl border border-[#f0e8dd]">
    <h2 class="text-3xl font-bold text-[#5A3E1B] mb-6 text-center">Detalle del pedido #{{ '%05d' % pedido.id }}</h2>

    <div class="overflow-x-auto">
        <table class="w-full text-sm text-left border rounded-lg overflow-hidden shadow">
        <thead class="bg-[#F5E8D6] text-[#5A3E1B] font-semibold text-md">
            <tr>
            <th class="py-4 px-6">Imagen</th>
            <th class="py-4 px-6">Producto</th>
            <th class="py-4 px-6 text-center">Presentación</th>
            <th class="py-4 px-6 text-center">Cantidad</th>
            <th class="py-4 px-6 text-right">Subtotal</th>
            </tr>
        </thead>
        <tbody class="text-[#3D2B1F] bg-white">
            {% for item in detalles %}
            <tr class="border-b hover:bg-[#faf6f1] transition">
            <td class="py-4 px-6">
                <div class="w-24 h-28">
                <img src="{{ url_for('cliente_bp.mostrar_imagen', galleta_id=item.galleta.id) }}"
                    alt="Galleta"
                    class="w-full h-full object-contain rounded-lg border" />
                </div>
            </td>
            <td class="py-4 px-6 font-medium">{{ item.galleta.nombre }}</td>
            <td class="py-4 px-6 text-center">{{ item.presentacion|capitalize }}</td>
            <td class="py-4 px-6 text-center">
                {% if item.presentacion == 'caja' %}
                {{ item.cantidad // 30 }} caja{{ 's' if item.cantidad // 30 > 1 }}
                {% elif item.presentacion == 'kilo' %}
                {{ item.cantidad // 24 }} kilo{{ 's' if item.cantidad // 24 > 1 }}
                {% else %}
                {{ item.cantidad }} pieza{{ 's' if item.cantidad > 1 }}
                {% endif %}
            </td>
            <td class="py-4 px-6 text-right">${{ "%.2f"|format(item.precio_unitario * item.cantidad) }}</td>
            </tr>
            {% endfor %}
        </tbody>
        </table>
    </div>

    <div class="text-right text-[#5A3E1B] text-xl font-semibold mt-6">
        Total del pedido: <span class="text-2xl font-bold">${{ "%.2f"|format(pedido.total) }}</span>
    </div>
    </div>
    """,
                                  pedido=pedido,
                                  detalles=detalles)


# Ruta de carrito productos
@cliente_bp.route('/carrito_compras')
@login_required
@role_required('cliente')
def carrito_compras():
    carrito_sesion = session.get('carrito', [])

    if carrito_sesion and isinstance(carrito_sesion[0], dict):
        carrito_limpio = carrito_sesion
    else:
        carrito_limpio = []
        elementos = CarritoTemporal.query.filter_by(
            usuario_id=current_user.id).all()
        for item in elementos:
            galleta = Galleta.query.get(item.galleta_id)
            if galleta:
                presentacion = item.presentacion
                cantidad = item.cantidad

                if presentacion == 'caja':
                    piezas = cantidad * 30
                    precio = galleta.precio * 30
                elif presentacion == 'kilo':
                    piezas = cantidad * 24
                    precio = galleta.precio * 24
                else:
                    piezas = cantidad
                    precio = galleta.precio

                carrito_limpio.append({
                    'galleta_id': galleta.id,
                    'nombre': galleta.nombre,
                    'precio': precio,
                    'presentacion': presentacion,
                    'cantidad': cantidad,
                    'piezas': piezas
                })
        session['carrito'] = carrito_limpio

    return render_template('cliente/carrito_compras.html',
                           carrito=carrito_limpio)


# Ruta para cambiar la cantidad de galletas en el carrito
@cliente_bp.route('/cambiar-cantidad', methods=['POST'])
@login_required
@role_required('cliente')
def cambiar_cantidad():
    galleta_id = int(request.form.get('galleta_id'))
    cantidad = int(request.form.get('cantidad', 1))
    presentacion = request.form.get('presentacion', 'pieza')

    if cantidad < 1:
        flash("Cantidad inválida", "danger")
        return redirect(url_for('cliente_bp.carrito_compras'))

    if presentacion == "caja":
        piezas = cantidad * 30
    elif presentacion == "kilo":
        piezas = cantidad * 24
    else:
        piezas = cantidad

    carrito = session.get('carrito', [])
    for item in carrito:
        if item['galleta_id'] == galleta_id and item[
                'presentacion'] == presentacion:
            item['cantidad'] = cantidad
            item['piezas'] = piezas
            break
    session['carrito'] = carrito

    temp = CarritoTemporal.query.filter_by(usuario_id=current_user.id,
                                           galleta_id=galleta_id,
                                           presentacion=presentacion).first()

    if temp:
        temp.cantidad = cantidad
        db.session.commit()
    return redirect(url_for('cliente_bp.carrito_compras'))


# Ruta para eliminar galletas del carrito
@cliente_bp.route('/eliminar-galleta', methods=['POST'])
@login_required
@role_required('cliente')
def eliminar_galleta():
    galleta_id = int(request.form.get('galleta_id'))
    presentacion = request.form.get('presentacion')

    carrito = session.get('carrito', [])
    carrito = [
        item for item in carrito
        if not (item.get('galleta_id') == galleta_id
                and item.get('presentacion') == presentacion)
    ]
    session['carrito'] = carrito

    temp = CarritoTemporal.query.filter_by(usuario_id=current_user.id,
                                           galleta_id=galleta_id,
                                           presentacion=presentacion).first()
    if temp:
        db.session.delete(temp)

    db.session.commit()
    flash("Galleta eliminada del carrito", "info")
    return redirect(url_for('cliente_bp.carrito_compras'))

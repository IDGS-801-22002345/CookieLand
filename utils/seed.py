import sys
import os
from datetime import datetime
from werkzeug.security import generate_password_hash

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importa desde models.models
from models.models import db, Role, Usuario, MateriaPrima, InventarioMateria, Proveedores

def run_seed():
    try:
        print("\n=== Iniciando carga de datos iniciales ===")
        
        # 1. Crear roles básicos
        roles = [
            {"role_name": "ADMIN"},
            {"role_name": "VENDEDOR"},
            {"role_name": "PRODUCCION"},
            {"role_name": "CLIENTE"}
        ]
        
        for rol in roles:
            if not Role.query.filter_by(role_name=rol["role_name"]).first():
                new_role = Role(role_name=rol["role_name"])
                db.session.add(new_role)
                print(f"✅ Rol {rol['role_name']} creado")
            else:
                print(f"ℹ️ Rol {rol['role_name']} ya existe")
        
        db.session.commit()
        
        # 2. Crear usuarios iniciales
        usuarios = [
            {
                "nombre": "Admin Principal",
                "telefono": "5551234567",
                "correo": "maico@gmail.com",
                "username": "maico",
                "contrasenia": "123",
                "rol_name": "ADMIN"
            },
            {
                "nombre": "Vendedor Ejemplo",
                "telefono": "5557654321",
                "correo": "vendedor@galletas.com",
                "username": "vendedor1",
                "contrasenia": "Vendedor123",
                "rol_name": "VENDEDOR"
            },
            {
                "nombre": "Jefe Producción",
                "telefono": "5559876543",
                "correo": "produccion@galletas.com",
                "username": "jefeprod",
                "contrasenia": "Produccion123",
                "rol_name": "PRODUCCION"
            }
        ]
        
        for user_data in usuarios:
            if not Usuario.query.filter_by(username=user_data["username"]).first():
                rol = Role.query.filter_by(role_name=user_data["rol_name"]).first()
                if rol:
                    new_user = Usuario(
                        nombre=user_data["nombre"],
                        telefono=user_data["telefono"],
                        correo=user_data["correo"],
                        username=user_data["username"],
                        contrasenia=generate_password_hash(user_data["contrasenia"]),
                        rol_id=rol.id
                    )
                    db.session.add(new_user)
                    print(f"✅ Usuario {user_data['username']} creado")
                else:
                    print(f"⚠️ Rol {user_data['rol_name']} no encontrado para usuario {user_data['username']}")
            else:
                print(f"ℹ️ Usuario {user_data['username']} ya existe")
        
        db.session.commit()
        
        # 3. Crear materias primas con su inventario
        materias_primas = [
            {
                "nombre": "Harina de trigo",
                "unidad": "kg",
                "cantidad": 100,
                "cantidad_minima": 20,
                "estado_stock": "DISPONIBLE"
            },
            {
                "nombre": "Azúcar",
                "unidad": "kg",
                "cantidad": 50,
                "cantidad_minima": 10,
                "estado_stock": "DISPONIBLE"
            },
            {
                "nombre": "Huevo",
                "unidad": "piezas",
                "cantidad": 200,
                "cantidad_minima": 50,
                "estado_stock": "DISPONIBLE"
            },
            {
                "nombre": "Mantequilla",
                "unidad": "kg",
                "cantidad": 30,
                "cantidad_minima": 5,
                "estado_stock": "DISPONIBLE"
            }
        ]
        
        for mp_data in materias_primas:
            if not MateriaPrima.query.filter_by(nombre=mp_data["nombre"]).first():
                new_mp = MateriaPrima(
                    nombre=mp_data["nombre"],
                    unidad=mp_data["unidad"]
                )
                db.session.add(new_mp)
                db.session.flush()  
                
                new_inventario = InventarioMateria(
                    cantidad=mp_data["cantidad"],
                    cantidad_minima=mp_data["cantidad_minima"],
                    estado_stock=mp_data["estado_stock"],
                    material_id=new_mp.id
                )
                db.session.add(new_inventario)
                print(f"✅ Materia prima {mp_data['nombre']} creada con inventario")
            else:
                print(f"ℹ️ Materia prima {mp_data['nombre']} ya existe")
        
        db.session.commit()
        
        # 4. Crear proveedores
        proveedores = [
            {
                "nombre": "Distribuidora de Alimentos S.A.",
                "telefono": "5551112233",
                "email": "contacto@distrialimentos.com"
            },
            {
                "nombre": "Productos Agrícolas del Valle",
                "telefono": "5554445566",
                "email": "ventas@agricolavalle.com"
            },
            {
                "nombre": "Ingredientes Industriales MX",
                "telefono": "5557778899",
                "email": "info@ingremx.com"
            }
        ]
        
        for prov in proveedores:
            if not Proveedores.query.filter_by(nombre=prov["nombre"]).first():
                new_prov = Proveedores(
                    nombre=prov["nombre"],
                    telefono=prov["telefono"],
                    email=prov["email"]
                )
                db.session.add(new_prov)
                print(f"✅ Proveedor {prov['nombre']} creado")
            else:
                print(f"ℹ️ Proveedor {prov['nombre']} ya existe")
        
        db.session.commit()
        
        print("\n=== Carga de datos iniciales completada con éxito ===")
    
    except Exception as e:
        db.session.rollback()
        print(f"\n❌ Error durante la carga de datos: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    from app import create_app
    app = create_app()
    with app.app_context():
        run_seed()
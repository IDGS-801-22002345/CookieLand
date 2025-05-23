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
            {"role_name": "admin"},
            {"role_name": "cliente"},
            {"role_name": "produccion"},
            {"role_name": "vendedor"}
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
                "correo": "admin@gmail.com",
                "username": "admin",
                "contrasenia": "maicookies123", 
                "rol_name": "admin"
            },
            {
                "nombre": "Vendedor Ejemplo",
                "telefono": "5557654321",
                "correo": "vendedor@galletas.com",
                "username": "vendedor1",
                "contrasenia": "vendedor1",
                "rol_name": "vendedor"
            },
            {
                "nombre": "Jefe Producción",
                "telefono": "5559876543",
                "correo": "produccion@galletas.com",
                "username": "jefeprod",
                "contrasenia": "produccion1",
                "rol_name": "produccion"
            },
            {
                "nombre": "Cliente Feliz",
                "telefono": "5551112233",
                "correo": "cliente@galletas.com",
                "username": "cliente1",
                "contrasenia": "cliente1",
                "rol_name": "cliente"
            }
        ]

        for user_data in usuarios:
            if not Usuario.query.filter_by(username=user_data["username"]).first():
                rol = Role.query.filter_by(role_name=user_data["rol_name"].lower()).first()
                if rol:
                    new_user = Usuario(
                        nombre=user_data["nombre"],
                        telefono=user_data["telefono"],
                        correo=user_data["correo"],
                        username=user_data["username"],
                        contrasenia=generate_password_hash(user_data["contrasenia"]),
                        estatus=1,
                        verificado=True,
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
                "unidad": "gr",
                "cantidad": 5000,
                "cantidad_minima": 1000,
                "estado_stock": "Disponible"
            },
            {
                "nombre": "Leche",
                "unidad": "ml",
                "cantidad": 5000,
                "cantidad_minima": 1000,
                "estado_stock": "Disponible"
            },
            {
                "nombre": "Azúcar",
                "unidad": "gr",
                "cantidad": 1200,
                "cantidad_minima": 1000,
                "estado_stock": "Disponible"
            },
            {
                "nombre": "Huevo",
                "unidad": "pz",
                "cantidad": 50,
                "cantidad_minima": 30,
                "estado_stock": "Disponible"
            },
            {
                "nombre": "Mantequilla",
                "unidad": "gr",
                "cantidad": 500,
                "cantidad_minima": 1000,
                "estado_stock": "Disponible"
            },
            {
                "nombre": "Polvo para hornear",
                "unidad": "gr",
                "cantidad": 800,
                "cantidad_minima": 1000,
                "estado_stock": "Disponible"
            },
            {
                "nombre": "Esencia de vainilla",
                "unidad": "ml",
                "cantidad": 250,
                "cantidad_minima": 1000,
                "estado_stock": "Disponible"
            },
            {
                "nombre": "Chispas de chocolate",
                "unidad": "gr",
                "cantidad": 1000,
                "cantidad_minima": 1000,
                "estado_stock": "Disponible"
            },
            {
                "nombre": "Cacao en polvo",
                "unidad": "gr",
                "cantidad": 700,
                "cantidad_minima": 1000,
                "estado_stock": "Disponible"
            },
            {
                "nombre": "Nueces",
                "unidad": "gr",
                "cantidad": 600,
                "cantidad_minima": 1000,
                "estado_stock": "Disponible"
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
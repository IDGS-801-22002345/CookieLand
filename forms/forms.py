# from wtforms import Form
# from wtforms import StringField,PasswordField,EmailField,BooleanField,RadioField, IntegerField
# from wtforms import validators

# class UserForm(Form):
#     matricula=IntegerField("Matricula",[validators.DataRequired(message="El campo es requerido"),
#    ])
#     nombre=StringField("Nombre",[validators.DataRequired(message="El campo es requerido"),
#    ])
#     apellido=StringField("Apellido",[validators.DataRequired(message="El campo es requerido"),
#    ])
#     correo=EmailField("Correo",[validators.DataRequired(message="El campo es requerido"),
#    ])


# class UserForm2(Form):
#     id=IntegerField('id',
#     [validators.number_range(min=1, max=20,message='valor no valido')])
#     nombre=StringField('nombre',[
#         validators.DataRequired(message='El nombre es requerido'),
#         validators.length(min=4,max=20, message='requiere min=4 max=20')
#     ])
   
#     apaterno=StringField('apaterno',[
#         validators.DataRequired(message='El apellido es requerido')
#     ])
   
#     email=EmailField('correo',[
#         validators.DataRequired(message='El apellido es requerido'),
#         validators.Email(message='Ingrese un correo valido')
#     ])
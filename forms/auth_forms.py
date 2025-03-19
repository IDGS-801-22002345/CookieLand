from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, BooleanField
from wtforms.validators import DataRequired, Length, Email

class RegisterFormDashboard(FlaskForm):
    nombre = StringField("Nombre", validators=[DataRequired(), Length(min=3, max=100)])
    telefono = StringField("Teléfono", validators=[DataRequired(), Length(min=10, max=10)])
    correo = StringField("Correo", validators=[DataRequired(), Email()])
    username = StringField("Usuario", validators=[DataRequired(), Length(min=4, max=50)])
    password = PasswordField("Contraseña", validators=[DataRequired(), Length(min=8, max=128)])
    rol = SelectField("Rol", choices=[("Administrador", "Administrador"),
                                       ("Vendedor", "Vendedor"),
                                       ("Comprador", "Comprador"),
                                       ("Producción", "Producción")], validators=[DataRequired()])

class RegisterFormLandingPage(FlaskForm):
    nombre = StringField("Nombre", validators=[DataRequired(), Length(min=3, max=100)])
    telefono = StringField("Teléfono", validators=[DataRequired(), Length(min=10, max=10)])
    correo = StringField("Correo", validators=[DataRequired(), Email()])
    username = StringField("Usuario", validators=[DataRequired(), Length(min=4, max=50)])
    password = PasswordField("Contraseña", validators=[DataRequired(), Length(min=8, max=128)])

class LoginForm(FlaskForm):
    email = StringField("Correo Electrónico", validators=[DataRequired(), Email()])
    password = PasswordField("Contraseña", validators=[DataRequired(), Length(min=8)])
    remember = BooleanField("Recordarme")
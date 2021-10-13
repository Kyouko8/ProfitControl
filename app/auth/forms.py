""" Working with Users """
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo


class SignupForm(FlaskForm):
    firstname = StringField("Nombre: ", validators=[
        DataRequired("Este campo no puede estar vacío."),
        Length(min=3, message="Ingrese mínimo %(min)s caracteres."),
        Length(max=64, message="Este campo admite hasta %(max)s caracteres.")
    ])

    lastname = StringField("Apellido: ", validators=[
        Length(max=64, message="Este campo admite hasta %(max)s caracteres.")
    ])

    email = StringField("Email:", validators=[
        DataRequired("Este campo no puede estar vacío."),
        Length(max=256, message="Este campo admite hasta %(max)s caracteres."),
        Email(message="El email ingresado no es válido.")
    ])

    password = PasswordField("Contraseña:", validators=[
        DataRequired("Este campo no puede estar vacío."),
        Length(min=8, message="Ingrese mínimo %(min)s caracteres."),
        Length(max=160, message="Este campo admite hasta %(max)s caracteres."),
        EqualTo('confirm', message='Las contraseñas deben coincidir')
    ])
    confirm = PasswordField("Confirmar:", validators=[
        DataRequired("Este campo no puede estar vacío."),
        Length(min=8, message="Ingrese mínimo %(min)s caracteres."),
        Length(max=160, message="Este campo admite hasta %(max)s caracteres.")
    ])

    remember_me = BooleanField("Recuérdame", default="checked")
    fast_log = BooleanField("Mantener en inicios recientes", default="checked")
    submit = SubmitField("Crear Cuenta")


class LoginForm(FlaskForm):
    email = StringField("Email: ", validators=[
        DataRequired("Este campo no puede estar vacío."),
        Length(max=256, message="Este campo admite hasta %(max)s caracteres."),
        Email(message="El email ingresado no es válido.")
    ])

    password = PasswordField("Contraseña:", validators=[
        DataRequired("Este campo no puede estar vacío."),
        Length(min=8, message="Ingrese mínimo %(min)s caracteres."),
        Length(max=160, message="Este campo admite hasta %(max)s caracteres.")
    ])

    remember_me = BooleanField("Recuérdame", default="checked")
    fast_log = BooleanField("Mantener en inicios recientes", default="checked")
    submit = SubmitField("Iniciar")

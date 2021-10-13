""" Working with Users """
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, HiddenField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Length, EqualTo

# name = COLUMN(STRING(256), nullable=False)
# description = COLUMN(STRING(2048), nullable=True)
# telephone = COLUMN(STRING(20), nullable=True)
# telephone_alt = COLUMN(STRING(20), nullable=True)
# phone_number = COLUMN(STRING(20), nullable=True)
# phone_number_alt = COLUMN(STRING(20), nullable=True)
# email = COLUMN(STRING(320), nullable=True)
# address = COLUMN(STRING(128), nullable=True)
# location = COLUMN(STRING(128), nullable=True)

class AddClientForm(FlaskForm):
    name = StringField("Nombre", validators=[
        DataRequired("Este campo no puede estar vacío."),
        Length(min=3, message="Ingrese mínimo %(min)s caracteres."),
        Length(max=64, message="Este campo admite hasta %(max)s caracteres.")
    ])

    description = StringField("Descripcion", validators=[
        Length(max=2048, message="Este campo admite hasta %(max)s caracteres.")
    ])

    telephone = StringField("Teléfono", validators=[
        Length(max=20, message="Este campo admite hasta %(max)s caracteres.")
    ])

    telephone_alt = StringField("Teléfono (Alternativo)", validators=[
        Length(max=20, message="Este campo admite hasta %(max)s caracteres.")
    ])

    phone_number = StringField("Número de Celular", validators=[
        Length(max=20, message="Este campo admite hasta %(max)s caracteres.")
    ])

    phone_number_alt = StringField("Número de Celular (Alternativo)", validators=[
        Length(max=20, message="Este campo admite hasta %(max)s caracteres.")
    ])

    email = StringField("Correo Electrónico", validators=[
        Length(max=320, message="Este campo admite hasta %(max)s caracteres.")
    ])

    address = StringField("Dirección", validators=[
        Length(max=20, message="Este campo admite hasta %(max)s caracteres.")
    ])

    location = StringField("Localidad", validators=[
        Length(max=20, message="Este campo admite hasta %(max)s caracteres.")
    ])

    note = TextAreaField("Nota", validators=[
        Length(max=2048, message="Este campo admite hasta %(max)s caracteres.")
    ])
    
    submit = SubmitField("Guardar")

class AddClientProductForm(FlaskForm):
    hidden_token = HiddenField()

    product = StringField("Nombre del Producto")

    price = StringField("Precio de Venta", validators=[
        DataRequired("Este campo no puede estar vacío."),
    ])

    cost = StringField("Costo")

    extra_cost = StringField("Costo Extra")

    quantity = StringField("Cantidad Vendida", validators=[
        DataRequired("Este campo no puede estar vacío."),
    ])

    submit = SubmitField("Agregar")
    submit_and_finish = SubmitField("Agregar y Finalizar")



class SearchClientForm(FlaskForm):
    name = StringField("Nombre")

    submit = SubmitField("Buscar")


class NoteForm(FlaskForm):
    note = TextAreaField("Nota", validators=[
        Length(max=2048, message="Este campo admite hasta %(max)s caracteres.")
    ])
    
    submit = SubmitField("Guardar")
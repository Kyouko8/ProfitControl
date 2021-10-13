""" Working with Users """
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, HiddenField, RadioField, SelectField
from wtforms.validators import DataRequired, Length, EqualTo


class AddProductForm(FlaskForm):
    hidden_token = HiddenField()

    product = StringField("Nombre del Producto", validators=[
        DataRequired("Este campo no puede estar vacío."),
        Length(min=3, message="Ingrese mínimo %(min)s caracteres."),
        Length(max=64, message="Este campo admite hasta %(max)s caracteres.")
    ])

    description = StringField("Descripcion", validators=[
        Length(max=256, message="Este campo admite hasta %(max)s caracteres.")
    ])

    default_price = StringField("Precio Predeterminado", validators=[
        DataRequired("Este campo no puede estar vacío."),
    ])

    cost = StringField("Costo", validators=[
        DataRequired("Este campo no puede estar vacío."),
    ])

    extra_cost = StringField("Costo Extra (Opcional)", validators=[])

    quantity = StringField("Cantidad", validators=[
        DataRequired("Este campo no puede estar vacío."),
    ])
    
    new = RadioField('Condición', choices=[('1','Nuevo'), ('0','Usado')], default="1")
    status = RadioField('Estado', choices=[('1','Activo'), ('0','Inactivo')], default="1")
    
    submit = SubmitField("Guardar")
    submit_and_finish = SubmitField("Guardar y Finalizar")


class ToolsNicePriceForm(FlaskForm):
    cost = StringField("Costo", validators=[
        DataRequired("Este campo no puede estar vacío."),
    ])

    extra_cost = StringField("Costo Extra (Opcional)")

    price = StringField("Posible Precio (Opcional)")

    new = RadioField('Condición', choices=[('1','Nuevo'), ('0','Usado')], default="1")

    show_all = HiddenField()
    
    submit = SubmitField("Calcular")


class SearchProductForm(FlaskForm):
    name = StringField("Nombre")

    min_price = StringField("Precio Mínimo")

    max_price = StringField("Precio Máximo")

    min_stock = StringField("Cantidad Mínima")

    max_stock = StringField("Cantidad Máxima")
    
    min_cost = StringField("Costo Mínimo")

    max_cost = StringField("Costo Máximo")

    min_sales = StringField("Venta Mínima")

    max_sales = StringField("Venta Máxima")
    
    min_profit = StringField("Ganancia Mínimo")

    max_profit = StringField("Ganancia Máximo")

    show_all = RadioField('Condición', choices=[('1','Mostrar Todo'), ('0','Solo Disponibles')], default="1")
    
    submit = SubmitField("Buscar")
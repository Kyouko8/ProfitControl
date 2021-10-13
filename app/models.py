import secrets
import os
import datetime
import math
import json

from flask import url_for
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import func

from app import db
from .constants import COLUMN, INTEGER, FLOAT, STRING, BOOLEAN, DATETIME, TEXT, FK, ModelSaveDelete
from .functions import nice_price, round_price, get_day_name

class Profile(db.Model, ModelSaveDelete):
    __tablename__ = "profile"

    id = COLUMN(INTEGER, primary_key=True, autoincrement=True, nullable=False)
    id_user = COLUMN(INTEGER, FK('user.id'), nullable=False)
    token = COLUMN(STRING(200), unique=True, nullable=False)
    name = COLUMN(STRING(64), nullable=False)
    active = COLUMN(BOOLEAN, nullable=False)

    user = db.relationship("User", backref="profiles")

    def __repr__(self):
        return f"<Profile {self.id}: {self.name}; {self.token}; {self.user}>"

    def save(self):
        db.session.add(self)
        if not self.token:
            self.token = generate_token(9)

        while self._exists_token(self.token):
            self.token = generate_token(9)

        try:
            db.session.commit()

        except IntegrityError:
            db.session.rollback()

    def _exists_token(self, token):
        if token is None:
            raise ValueError("Invalid Token.")

        profile = Profile.get_by_token(token)

        if profile is None:
            return False

        elif profile.id == self.id:
            return False

        return True

    @staticmethod
    def get_by_id(id):
        return Profile.query.get(id)

    @staticmethod
    def get_by_token(token):
        return Profile.query.filter_by(token=token).first()

    @staticmethod
    def get_by_user(id_user, only_active=False):
        if only_active:
            return Profile.query.filter_by(id_user=id_user, active=True).\
                order_by(Profile.name).all()

        else:
            return Profile.query.filter_by(id_user=id_user).\
                order_by(Profile.name).all()
    
    @staticmethod
    def get_by_name(name, id_user):
        return Profile.query.filter_by(id_user=id_user).filter(func.upper(Profile.name) == name.upper()).first()

    @staticmethod
    def get_count_by_user(id_user, only_active=False):
        if only_active:
            return db.session.query(
                Profile.id, Profile.id_user, Profile.active).filter_by(
                    id_user=id_user, active=True).count()

        else:
            return db.session.query(Profile.id, Profile.id_user).filter_by(id_user=id_user).count()

    def get_name(self):
        if self.name is None:
            return f"Perfil-{str(self.token).upper()}"
        else:
            return str(self.name).upper()

    def get_status(self):
        if self.active:
            return "Activo"
        else:
            return "Inactivo"

    def can_be_deleted(self):
        spendings = Spending.get_by_profile(self.id)
        if spendings is not None and len(spendings) >= 1:
            profiles = Profile.get_by_user(self.id_user)
            if profiles is not None and len(profiles) >= 1:
                return False
        
        return True


class Product(db.Model, ModelSaveDelete):
    __tablename__ = "product"

    id = COLUMN(INTEGER, primary_key=True, autoincrement=True, nullable=False)
    id_user = COLUMN(INTEGER, FK('user.id'), nullable=False)
    token = COLUMN(STRING(200), unique=True, nullable=False)
    name = COLUMN(STRING(64), nullable=False)
    description = COLUMN(STRING(256), nullable=True)
    date = COLUMN(DATETIME, nullable=False, server_default=func.now())
    new = COLUMN(BOOLEAN, nullable=False)
    stock = COLUMN(INTEGER, nullable=False)
    #default_price = COLUMN(INTEGER, nullable=False)
    active = COLUMN(BOOLEAN, nullable=False)
    #favorite = COLUMN(BOOLEAN, nullable=False)

    user = db.relationship("User", backref="products")

    def __repr__(self):
        return f"<Product {self.id}: {self.name}, x{self.stock}, ${self.get_price()}; {self.token}; {self.user}>"

    def save(self):
        db.session.add(self)
        if not self.token:
            self.token = generate_token(13)

        while self._exists_token(self.token):
            self.token = generate_token(13)

        self.name = str(self.name).upper()
        try:
            db.session.commit()

        except IntegrityError:
            db.session.rollback()

    def _exists_token(self, token):
        if token is None:
            raise ValueError("Invalid Token.")

        product = Product.get_by_token(token)

        if product is None:
            return False

        elif product.id == self.id:
            return False

        return True

    @staticmethod
    def get_by_id(id):
        return Product.query.get(id)

    @staticmethod
    def get_by_token(token):
        return Product.query.filter_by(token=token).first()

    @staticmethod
    def get_by_name(name, id_user):
        return Product.query.filter_by(id_user=id_user).filter(func.upper(Product.name) == name.upper()).first()

    @staticmethod
    def get_by_name_advanced(search_name, id_user, limit=None, offset=None, only_active=False):
        query = Product.query.filter_by(id_user=id_user).\
            filter(func.upper(Product.name).contains(search_name.upper())).\
            order_by(Product.name)

        if only_active:
            query = query.filter_by(active=True)
            
        if limit is not None:
            query = query.limit(limit)
        
        if offset is not None:
            query = query.offset(offset)

        return query.all()

    @staticmethod
    def get_by_user(id_user, limit=None, offset=None, only_active=False):
        query = Product.query.filter_by(id_user=id_user).\
            order_by(Product.name)
        if only_active:
            query = query.filter_by(active=True)
            
        if limit is not None:
            query = query.limit(limit)
        
        if offset is not None:
            query = query.offset(offset)

        return query.all()

    @staticmethod
    def get_count_by_user(id_user, only_active=False):
        if only_active:
            return db.session.query(
                Product.id, Product.id_user, Product.active
            ).filter_by(id_user=id_user, active=True).count()
        else:
            return db.session.query(Product.id, Product.id_user).filter_by(id_user=id_user).count()

    def get_name(self):
        return self.name.upper()

    def get_cost(self, date):
        if date is None:
            date = datetime.datetime.utcnow()

        return Cost.get_cost_of_day(self.id, date)

    def get_percent_cost(self, date=None, cost=None):
        if cost is None:
            cost = self.get_cost(date)
        price = cost.get_price()

        return int(round(100*(cost.get_real_cost()/price)))

    def get_current_cost(self):
        return Cost.get_cost_of_day(self.id, datetime.datetime.utcnow())

    def get_gain(self, date=None, cost=None):
        if cost is None:
            cost = self.get_cost(date)

        return cost.get_price() - cost.get_real_cost()

    def get_profile_gain(self, date=None, cost=None):
        count = Profile.get_count_by_user(self.id_user, only_active=True)
        gain = self.get_gain(date, cost)
        return int(round(gain/count))

    def get_percent_gain_by_cost(self, date=None, cost=None):
        rcost = cost.get_real_cost()
        gain = self.get_gain(date, cost)
        return int(round(100*(gain / max(0.5, rcost))))

    def get_percent_gain(self, date=None, cost=None):
        return 100-self.get_percent_cost(date, cost)

    def get_price(self, date=None, cost=None):
        if cost is None:
            cost = self.get_cost(date)

        return cost.get_price()

    def get_price_status(self, date=None, cost=None):
        if cost is None:
            cost = self.get_cost(date)

        rcost = cost.get_real_cost()
        price = cost.get_price()
        
        return nice_price.get_price_status(price, rcost, self.new)

    def get_price_status_as_word(self, date=None, cost=None):
        if cost is None:
            cost = self.get_cost(date)

        rcost = cost.get_real_cost()
        price = cost.get_price()

        return nice_price.get_price_status_as_word(price, rcost, self.new)

    def get_price_status_color(self, date=None, cost=None):
        if cost is None:
            cost = self.get_cost(date)

        rcost = cost.get_real_cost()
        price = cost.get_price()

        return nice_price.get_price_status_color(price, rcost, self.new)

    def get_price_status_percent(self, date=None, cost=None):
        if cost is None:
            cost = self.get_cost(date)

        rcost = cost.get_real_cost()
        price = cost.get_price()

        return nice_price.get_price_status_percent(price, rcost, self.new)

    def get_nice_price(self, date=None, cost=None, level=1):
        if cost is None:
            cost = self.get_cost(date)

        rcost = cost.get_real_cost()
        return nice_price.get_price(rcost=rcost, new=self.new, level=level)
        
    def get_nice_price_difference(self, date=None, cost=None, level=1):
        if cost is None:
            cost = self.get_cost(date)

        rcost = cost.get_real_cost()
        price = cost.get_price()

        return nice_price.get_price_difference(price, rcost, self.new, level)

    def get_nice_percent_gain_by_cost(self, date=None, cost=None, level=1):
        if cost is None:
            cost = self.get_cost(date)

        rcost = cost.get_real_cost()
        return nice_price.get_percent_gain_by_cost(rcost, self.new, level)

    def get_nice_percent_cost(self, date=None, cost=None, level=1):
        if cost is None:
            cost = self.get_cost(date)

        rcost = cost.get_real_cost()
        return nice_price.get_percent_cost(rcost, self.new, level)

    def get_nice_percent_gain(self, date=None, cost=None, level=1):
        if cost is None:
            cost = self.get_cost(date)

        rcost = cost.get_real_cost()
        return nice_price.get_percent_gain(rcost, self.new, level)

    def get_nice_gain(self, date=None, cost=None, level=1):
        if cost is None:
            cost = self.get_cost(date)

        rcost = cost.get_real_cost()
        return nice_price.get_gain(rcost, self.new, level)

    def get_nice_profile_gain(self, date=None, cost=None, level=1):
        count = Profile.get_count_by_user(self.id_user, only_active=True)
        gain = self.get_nice_gain(date, cost, level=level)
        return int(round(gain/count))

    def get_stock(self, sales=None):
        sales_count = self.get_sales_count(sales)

        return self.stock - sales_count

    def set_stock(self, new_quantity, stock=None, relative=True):
        if stock is None:
            stock = self.get_stock()
        
        if relative:
            new_quantity += self.stock
        else:
            new_quantity = (self.stock-stock) + max(0, new_quantity)

        self.stock = max(self.stock-stock, new_quantity)
        return self.stock

    def get_sales_count(self, sales=None):
        if sales is None:
            sales = self.get_sales()

        count = 0
        for sale in sales:
            count += sale.quantity

        return count

    def get_sales(self):
        return ListSales.get_by_product(self.id)

    def get_sales_sorted(self):
        sales = self.get_sales()

        dates = {}
        for sale in sales:
            workday = sale.workday
            if not workday in dates:
                dates[workday] = {'quantity': 0, 'amount': 0, 'price': 0}

            dates[workday]['quantity'] += sale.quantity
            dates[workday]['price'] += sale.price * sale.quantity

        return dates

    def is_in_price(self):
        status = self.get_price_status()
        return status >= 3 and status <= 5

    def is_in_price_tooltip(self, warning='<i class="material-icons tiny">warning</i> <b>Advertencia</b>'):
        status = self.get_price_status()
        return {
            0: (f'{warning}: Precio Demasiado barato', 'red-text'),
            1: (f'{warning}: Precio Muy Barato', 'red-text'),
            2: (f'{warning}: Precio Barato', 'orange-text'),
            3: ('Precio Recomendado', 'blue-text'),
            4: ('Precio Aceptable', 'green-text'),
            5: (f'{warning}: Precio Poco Aceptable', 'orange-text'),
            6: (f'{warning}: Precio No Recomendado', 'red-text'),
            7: (f'{warning}: Precio Muy Caro', 'red-text'),
            8: (f'{warning}: Precio Demasiado Caro', 'red-text'),
            9: (f'{warning}: Precio Extremo', 'red-text'),
            }.get(int(status))

    def can_be_deleted(self):
        sales = self.get_sales_count()
        if sales >= 1:
            return False
        
        return True

    def delete_product_and_costs(self):
        costs = Cost.get_by_product_all(self.id)
        for cost in costs:
            cost.delete()

        self.delete()

    def as_dict(self):
        data = {
            'name': self.name,
            'stock': self.get_stock(),
            'price': self.get_price(),
            'cost': [],
            'date': self.date.timestamp(),
            'new': self.new,
            'active': self.active,
            'description': self.description,
        }
        for cost in self.costs:
            data['cost'].append(cost.as_dict())

        return data

    @staticmethod
    def from_dict(data, id_user, do_nothing_if_exists=0, update_stock=0, update_information=0):
        product = Product.get_by_name(data['name'], id_user)

        if product is not None:
            if do_nothing_if_exists:
                return product

            if not product.description and data.get('description'):
                product.description = data.get('description')
            
            # No modify
            if update_stock == 0:
                pass

            # Add to current
            elif update_stock == 1:
                product.set_stock(int(data['stock']), relative=True)

            # Reset to 0
            elif update_stock == 2:
                product.set_stock(0, relative=False)

            # Set to new_value
            elif update_stock == 3:
                product.set_stock(int(data['stock']), relative=False)

            
            # Modify Price
            if update_information in (1, 2):
                try:
                    default_price = int(data['price'])

                except TypeError:
                    pass

            product.save()

            # Modify Costs
            if update_information in (1, 3):
                current_costs = []
                for cost in product.costs:
                    current_costs.append(cost.as_dict())

                for cost_data in data['cost']:
                    if not cost_data in current_costs:
                        Cost.from_dict(cost_data, product.id, default_price=default_price)
            
            

        else:
            product = Product(
                id_user=id_user,
                name=data['name'].upper(),
                stock=int(data['stock']),
                new=bool(data['new']),
                active=bool(data['active']),
                date=datetime.datetime.fromtimestamp(data['date']),
                description=data['description']
            )

            product.save()

            for cost_data in data['cost']:
                Cost.from_dict(cost_data, product.id, data.get('price', 0))

        return product


class Cost(db.Model, ModelSaveDelete):
    __tablename__ = "cost"

    id = COLUMN(INTEGER, primary_key=True, autoincrement=True, nullable=False)
    id_product = COLUMN(INTEGER, FK('product.id'), nullable=False)
    token = COLUMN(STRING(200), unique=True, nullable=False)
    cost = COLUMN(FLOAT, nullable=False)
    extra_cost = COLUMN(FLOAT, nullable=False, default=0)
    price = COLUMN(FLOAT, nullable=False, default=0)
    date = COLUMN(DATETIME, nullable=False, server_default=func.now())

    product = db.relationship("Product", backref="costs")

    def __repr__(self):
        return f"<Cost {self.id}: ${self.cost}, +${self.extra_cost}, ${self.date}; {self.token}; Price: ${self.get_price()}>"

    def save(self):
        db.session.add(self)
        if not self.token:
            self.token = generate_token(14)

        while self._exists_token(self.token):
            self.token = generate_token(14)

        try:
            db.session.commit()

        except IntegrityError:
            db.session.rollback()

    def _exists_token(self, token):
        if token is None:
            raise ValueError("Invalid Token.")

        cost = Cost.get_by_token(token)

        if cost is None:
            return False

        elif cost.id == self.id:
            return False

        return True

    @staticmethod
    def get_by_id(id):
        return Cost.query.get(id)

    @staticmethod
    def get_by_token(token):
        return Cost.query.filter_by(token=token).first()

    @staticmethod
    def get_by_product(id_product):
        return Cost.query.filter_by(id_product=id_product).order_by(Cost.date.desc()).first()

    @staticmethod
    def get_by_product_all(id_product):
        return Cost.query.filter_by(id_product=id_product).order_by(Cost.date.desc()).all()

    @staticmethod
    def get_cost_of_day(id_product, date):
        timestamp_search = date.timestamp()
        timestamps = []
        accept = None

        costs = Cost.get_by_product_all(id_product)
        for cost in costs:
            timestamps.append((cost.date.timestamp(), cost))

        timestamps.sort(key=lambda x: x[0])
        for t in timestamps:
            if t[0] <= timestamp_search or accept is None:
                accept = t[1]

        return accept
                
    def get_real_cost(self):
        return self.cost + self.extra_cost

    def get_price(self):
        if self.price == 0:
            return float(round(self.get_real_cost()*1.5))

        return max(self.get_real_cost(), self.price)

    def as_dict(self):
        return {'cost': self.cost, 'extra_cost': self.extra_cost, 'price': self.get_price(), 'date': self.date.timestamp()}

    @staticmethod
    def from_dict(data, id_product, default_price=0):
        cost = Cost(
            id_product=id_product,
            cost=data['cost'],
            extra_cost=data['extra_cost'],
            price=data.get('price', default_price),
            date=datetime.datetime.fromtimestamp(data['date'])
        )
        cost.save()
        return cost


class ListSales(db.Model, ModelSaveDelete):
    __tablename__ = "list_sales"

    id = COLUMN(INTEGER, primary_key=True, autoincrement=True, nullable=False)
    id_group_sale = COLUMN(INTEGER, FK('groupsale.id'), nullable=False)
    id_cost = COLUMN(INTEGER, FK('cost.id'), nullable=False)
    token = COLUMN(STRING(200), unique=True, nullable=False)
    price = COLUMN(INTEGER, unique=False, nullable=False)
    note = COLUMN(STRING(512), nullable=True)
    quantity = COLUMN(INTEGER, nullable=False)

    cost = db.relationship("Cost")
    group_sale = db.relationship("GroupSale")

    _workday = None
    _is_workday = None
    client = None
    _is_client = None

    def __repr__(self):
        return f"<ListSales {self.id}: Product {self.cost.product.name}, ${self.cost.cost}, x{self.quantity}, ${self.price}; {self.token}; WorkDay: {self.is_workday()}>"

    def get_workday(self):
        if self._workday is None and self._is_workday is None:
            self._workday = self.group_sale.workday
            if self._workday is None:
                self._is_workday = False
            else:
                self._is_workday = True

        return self._workday

    def refresh_workday(self):
        self._workday = None
        self._is_workday = None
        return self.get_workday()
    
    def is_workday(self):
        self.get_workday()
        return (self._is_workday == True)

    workday = property(get_workday)

    def get_client(self):
        if self._client is None and self._is_client is None:
            self._client = self.group_sale.client
            if self._client is None:
                self._is_client = False
            else:
                self._is_client = True

        return self._client

    def refresh_client(self):
        self._client = None
        self._is_client = None
        return self.get_client()
    
    def is_client(self):
        self.get_client()
        return (self._is_client == True)

    client = property(get_client)

    def save(self):
        db.session.add(self)
        if not self.token:
            self.token = generate_token(20)

        while self._exists_token(self.token):
            self.token = generate_token(20)

        try:
            db.session.commit()

        except IntegrityError:
            db.session.rollback()

    def _exists_token(self, token):
        if token is None:
            raise ValueError("Invalid Token.")

        listsales = ListSales.get_by_token(token)

        if listsales is None:
            return False

        elif listsales.id == self.id:
            return False

        return True

    @staticmethod
    def get_by_id(id):
        return ListSales.query.get(id)

    @staticmethod
    def get_by_token(token):
        return ListSales.query.filter_by(token=token).first()

    @staticmethod
    def get_by_product(id_product) -> list:
        return ListSales.query.join(Cost).filter(Cost.id_product==id_product).\
            filter(Cost.id==ListSales.id_cost).order_by(ListSales.id_group_sale).all()

    @staticmethod
    def get_by_cost(id_cost) -> list:
        return ListSales.query.filter_by(id_cost=id_cost).\
            order_by(ListSales.id_group_sale).all()

    @staticmethod
    def get_by_workday(id_workday) -> list:
        workday = WorkDay.get_by_id(id_workday)
        return ListSales.query.filter_by(id_group_sale=workday.id_group_sale).all()

    @staticmethod
    def get_by_client(id_client) -> list:
        client = Client.get_by_id(id_client)
        return ListSales.query.filter_by(id_group_sale=client.id_group_sale).all()

    @staticmethod
    def get_by_group_sale(id_group_sale) -> list:
        return ListSales.query.filter_by(id_group_sale=id_group_sale).all()

    @staticmethod
    def get_by_price_cost_and_group_sale(price, id_cost, id_group_sale):
        return ListSales.query.filter_by(id_group_sale=id_group_sale, id_cost=id_cost, price=price).first()

    @staticmethod
    def get_by_price_cost_and_workday(price, id_cost, id_workday):
        workday = WorkDay.get_by_id(id_workday)
        return ListSales.query.filter_by(id_group_sale=workday.id_group_sale, id_cost=id_cost, price=price).first()

    @staticmethod
    def get_by_price_cost_and_workday(price, id_cost, id_client):
        client = Client.get_by_id(id_client)
        return ListSales.query.filter_by(id_group_sale=client.id_group_sale, id_cost=id_cost, price=price).first()

    def get_client_sale(self, force=True):
        return ClientSale.get_by_list_sales(id_list_sales=self.id)

    def can_be_deleted(self): # Always can be deleted.
        return True


class WorkDay(db.Model, ModelSaveDelete):
    __tablename__ = "workday"

    id = COLUMN(INTEGER, primary_key=True, autoincrement=True, nullable=False)
    id_user = COLUMN(INTEGER, FK('user.id'), nullable=False)
    id_group_sale = COLUMN(INTEGER, FK('groupsale.id'), unique=True, nullable=False)
    token = COLUMN(STRING(200), unique=True, nullable=False)
    date = COLUMN(DATETIME, nullable=False, server_default=func.now())
    product_date = COLUMN(DATETIME, nullable=False, server_default=func.now())
    note = COLUMN(STRING(2048), nullable=True,)

    user = db.relationship("User", backref="workdays")
    group_sale = db.relationship("GroupSale", back_populates="workday", uselist=False)

    def __repr__(self):
        return f"<WorkDay {self.id}: {self.user.username}, {self.date}; {self.token}; {self.group_sale}>"

    def save(self):
        db.session.add(self)
        if not self.token:
            self.token = generate_token(11)

        while self._exists_token(self.token):
            self.token = generate_token(11)

        try:
            db.session.commit()

        except IntegrityError:
            db.session.rollback()

    def _exists_token(self, token):
        if token is None:
            raise ValueError("Invalid Token.")

        workday = WorkDay.get_by_token(token)

        if workday is None:
            return False

        elif workday.id == self.id:
            return False

        return True

    @staticmethod
    def get_by_id(id):
        return WorkDay.query.get(id)

    @staticmethod
    def get_by_token(token):
        return WorkDay.query.filter_by(token=token).first()

    @staticmethod
    def get_by_user(id_user):
        return WorkDay.query.filter_by(id_user=id_user).order_by(WorkDay.date).all()

    @staticmethod
    def get_by_group_sale(id_group_sale, id_user):
        return WorkDay.query.filter_by(id_user=id_user, id_group_sale=id_group_sale).first()
    
    @staticmethod
    def get_by_date(id_user, date):
        return WorkDay.query.filter_by(id_user=id_user, date=date).order_by(WorkDay.date).first()
    
    @staticmethod
    def get_by_user_and_contains_notes(id_user):
        return WorkDay.query.filter_by(id_user=id_user).filter(WorkDay.note.isnot(None)).order_by(WorkDay.date).all() 

    def get_format(self, symbol="/"):
        return self.date.strftime(f"%d{symbol}%m{symbol}%Y")

    def get_day_name(self):
        day_number = self.date.isoweekday()
        return get_day_name(day_number)

    def get_products(self):
        list_sales = ListSales.get_by_group_sale(self.id_group_sale)

        products = []
        for sale in list_sales:
            product.append(sale.cost.product)

        return products

    def get_sales(self):
        return ListSales.get_by_group_sale(self.id_group_sale)

    def get_spendings(self):
        return Spending.get_by_workday(self.id)

    def get_resume(self, sales=None, spendings=None, profiles=None):
        if profiles is None:
            profiles = Profile.get_by_user(self.id_user, only_active=True)
        count = max(1, len(profiles))
        
        if sales is None:
            sales = self.get_sales()

        if spendings is None:
            spendings = self.get_spendings()

        total = {
            'quantity': 0,
            'price': 0,
            'cost': 0,
            'original_cost': 0,
            'original_extra_cost': 0,
            'original_rcost': 0,
            'profit': 0,
            'default_price': 0,
            'percent_price_cost': 0,
            'percent_profit_cost': 0,
            'profile_count': count,
        }

        for sale in sales:
            product = sale.cost.product
            total['quantity'] += sale.quantity
            total['price'] += sale.price * sale.quantity
            total['default_price'] += sale.cost.get_price() * sale.quantity
            total['cost'] += sale.cost.get_real_cost()*sale.quantity
            total['profit'] += (sale.price - sale.cost.get_real_cost())*sale.quantity
            
            total['original_cost'] += sale.cost.cost*sale.quantity
            total['original_extra_cost'] += sale.cost.extra_cost*sale.quantity
            total['original_rcost'] += sale.cost.get_real_cost()*sale.quantity


        total_spending = {'count': 0, 'total': 0, 'general_count': 0, 'general_spending': 0, 'profiles': {}}

        total_spending['profiles'] = {profile: {'spending': 0, 'count': 0} for profile in profiles}

        for spending in spendings:
            total_spending['count'] += 1
            total_spending['total'] += spending.price

            if spending.profile is None:
                total['cost'] += spending.price
                total['profit'] -= spending.price
                total_spending['general_spending'] += spending.price
                total_spending['general_count'] += 1
            else:
                profile = spending.profile
                if not profile in total_spending['profiles']:
                    continue
                
                dc = total_spending['profiles'][profile]
                
                dc['spending'] += spending.price
                dc['count'] += 1

        total['spendings'] = total_spending
        total['profit_profile'] = int(round(total['profit'] / count))

        try:
            total['percent_profit_cost'] = round(100*total['profit'] / total['cost'], 2)
        except ZeroDivisionError:
            total['percent_profit_cost'] = 0

        try:
            total['percent_profit_price'] = round(100*total['profit'] /  total['price'], 2)
        except ZeroDivisionError:
            total['percent_profit_price'] = 0
        
        return total

    def get_mount_of_sales(self, sales=None, spendings=None):
        if sales is None:
            sales = self.get_sales()

        if spendings is None:
            spendings = self.get_spendings()
        
        total = {'price': 0, 'quantity': 0, 'cost': 0, 'spendings_count': 0, 'spendings': 0}
        for sale in sales:
            total['price'] += sale.price * sale.quantity
            total['cost'] += sale.cost.get_real_cost() * sale.quantity
            total['quantity'] += sale.quantity

        for spending in spendings:
            total['spendings_count'] += 1
            total['spendings'] += spending.price

            if spending.profile is None:
                total['cost'] += spending.price

        total['profit'] = total['price'] - total['cost']
        return total

    def get_mount_of_spendings(self, spendings=None):
        if spendings is None:
            spendings = self.get_spendings()

        total = {'count': 0, 'mount': 0}
        for spending in spendings:
            total['count'] += 1
            total['mount'] += spending.price
        
        return total

    def get_date_as_tuple(self):
        return (self.date.year, self.date.month, self.date.day)

    def can_be_deleted(self):
        sales = self.get_sales()
        if not self.group_sale.can_be_deleted():
            return False

        if sales is not None and len(sales) >= 1:
            spendings = self.get_spendings()
            if spendings is not None and len(spendings) >= 1:
                return False
        
        return True

    def between(self, min_date, max_date, format_date="%d/%m/%Y"):
        result1 = False
        result2 = False
        if min_date is None:
            result1 = True
        else:
            min_date = datetime.datetime.strptime(f"{min_date} 0#0#0", f"{format_date} %H#%M#%S")
            result1 = (min_date < self.date)

        if max_date is None:
            result2 = True
        else:
            max_date = datetime.datetime.strptime(f"{max_date} 23#59#59", f"{format_date} %H#%M#%S")
            result2 = (self.date < max_date)

        return result1 and result2


class Spending(db.Model, ModelSaveDelete):
    __tablename__ = "spending"

    id = COLUMN(INTEGER, primary_key=True, autoincrement=True, nullable=False)
    id_workday = COLUMN(INTEGER, FK('workday.id'), nullable=False)
    id_profile = COLUMN(INTEGER, FK('profile.id'), nullable=True)
    name = COLUMN(STRING(64), nullable=False)
    description = COLUMN(STRING(256), nullable=True)
    price = COLUMN(INTEGER, nullable=False)
    token = COLUMN(STRING(200), unique=True, nullable=False)

    profile = db.relationship("Profile")
    workday = db.relationship("WorkDay")

    def __repr__(self):
        return f"<Spending {self.id}: {self.name}, ${self.price}; {self.token}; {self.workday.date}, {self.profile}>"

    def save(self):
        db.session.add(self)
        if not self.token:
            self.token = generate_token(15)

        while self._exists_token(self.token):
            self.token = generate_token(15)

        try:
            db.session.commit()

        except IntegrityError:
            db.session.rollback()

    def _exists_token(self, token):
        if token is None:
            raise ValueError("Invalid Token.")

        spending = Spending.get_by_token(token)

        if spending is None:
            return False

        elif spending.id == self.id:
            return False

        return True

    @staticmethod
    def get_by_id(id):
        return Spending.query.get(id)

    @staticmethod
    def get_by_token(token):
        return Spending.query.filter_by(token=token).first()

    @staticmethod
    def get_by_profile(id_profile) -> list:
        return Spending.query.filter_by(id_profile=id_profile).\
            order_by(Spending.id_profile).all()

    @staticmethod
    def get_by_workday(id_workday) -> list:
        return Spending.query.filter_by(id_workday=id_workday).\
            order_by(Spending.id_profile).all()

    def get_profile_token(self):
        if self.profile is None:
            return None

        else:
            return self.profile.token

    def get_profile_name(self, general="General"):
        if self.profile is None:
            return general.upper()

        return self.profile.name.upper()

    def get_name(self):
        return str(self.name).upper()

    def get_description(self):
        if self.description is None:
            return ""

        return self.description

    def can_be_deleted(self): # Always can be deleted.
        return True


class Note(db.Model, ModelSaveDelete):
    __tablename__ = "note"

    id = COLUMN(INTEGER, primary_key=True, autoincrement=True, nullable=False)
    id_user = COLUMN(INTEGER, FK('user.id'), nullable=False)
    token = COLUMN(STRING(200), unique=True, nullable=False)
    title = COLUMN(STRING(64), nullable=False)
    content = COLUMN(STRING(8192), nullable=False)
    date = COLUMN(DATETIME, nullable=False, server_default=func.now())

    user = db.relationship("User", backref="notes")

    def __repr__(self):
        return f"<Note {self.id}: {self.title}; {self.token}; {self.user}>"

    def save(self):
        db.session.add(self)
        if not self.token:
            self.token = generate_token(13)

        while self._exists_token(self.token):
            self.token = generate_token(13)

        try:
            db.session.commit()

        except IntegrityError:
            db.session.rollback()

    def _exists_token(self, token):
        if token is None:
            raise ValueError("Invalid Token.")

        notes = Note.get_by_token(token)

        if notes is None:
            return False

        elif notes.id == self.id:
            return False

        return True

    @staticmethod
    def get_by_id(id):
        return Note.query.get(id)

    @staticmethod
    def get_by_token(token):
        return Note.query.filter_by(token=token).first()

    @staticmethod
    def get_by_user(id_user, only_active=False):
        return Note.query.filter_by(id_user=id_user).order_by(Note.date).all()
    
    @staticmethod
    def get_by_name(name, id_user):
        return Note.query.filter_by(id_user=id_user).filter(func.upper(Note.title) == name.upper()).first()

    @staticmethod
    def get_count_by_user(id_user, only_active=False):
        return db.session.query(Note.id, Note.id_user).filter_by(id_user=id_user).count()

    def get_name(self):
        if self.name is None:
            return f"Note-{str(self.token).upper()}"
        else:
            return str(self.name).upper()

    def can_be_deleted(self):
        return True

    def splitlines(self):
        return self.content.splitlines()

    def get_format(self, symbol="/"):
        return self.date.strftime(f"%d{symbol}%m{symbol}%Y")


class GroupSale(db.Model, ModelSaveDelete):
    __tablename__ = "groupsale"

    id = COLUMN(INTEGER, primary_key=True, autoincrement=True, nullable=False)
    token = COLUMN(STRING(200), unique=True, nullable=False)
    creation_date = COLUMN(DATETIME, nullable=False, server_default=func.now())

    workday = db.relationship("WorkDay", back_populates="group_sale", uselist=False)
    client = db.relationship("Client", back_populates="group_sale", uselist=False)
    
    def __repr__(self):
        return f"<GroupSale {self.id}: {self.token}; {self.creation_date}>"

    def save(self):
        db.session.add(self)
        if not self.token:
            self.token = generate_token(18)

        while self._exists_token(self.token):
            self.token = generate_token(18)

        try:
            db.session.commit()

        except IntegrityError:
            db.session.rollback()

    def _exists_token(self, token):
        if token is None:
            raise ValueError("Invalid Token.")

        group_sale = GroupSale.get_by_token(token)

        if group_sale is None:
            return False

        elif group_sale.id == self.id:
            return False

        return True

    @staticmethod
    def get_by_id(id):
        return GroupSale.query.get(id)

    @staticmethod
    def get_by_token(token):
        return GroupSale.query.filter_by(token=token).first()

    def delete_all_sales(self):
        list_sales = ListSales.get_by_group_sale(self.id)
        for sale in list_sales:
            sale.delete()
    
    def can_be_deleted(self):
        return True

    def get_format(self, symbol="/"):
        return self.creation_date.strftime(f"%d{symbol}%m{symbol}%Y")


class GroupShopping(db.Model, ModelSaveDelete):
    __tablename__ = "groupshopping"

    id = COLUMN(INTEGER, primary_key=True, autoincrement=True, nullable=False)
    token = COLUMN(STRING(200), unique=True, nullable=False)
    creation_date = COLUMN(DATETIME, nullable=False, server_default=func.now())

    shoppingday = db.relationship("ShoppingDay", back_populates="group_shopping", uselist=False)
    
    def __repr__(self):
        return f"<GroupShopping {self.id}: {self.token}; {self.creation_date}>"

    def save(self):
        db.session.add(self)
        if not self.token:
            self.token = generate_token(17)

        while self._exists_token(self.token):
            self.token = generate_token(17)

        try:
            db.session.commit()

        except IntegrityError:
            db.session.rollback()

    def _exists_token(self, token):
        if token is None:
            raise ValueError("Invalid Token.")

        group_shopping = GroupShopping.get_by_token(token)

        if group_shopping is None:
            return False

        elif group_shopping.id == self.id:
            return False

        return True

    @staticmethod
    def get_by_id(id):
        return GroupShopping.query.get(id)

    @staticmethod
    def get_by_token(token):
        return GroupShopping.query.filter_by(token=token).first()
    
    def delete_all_shoppings(self):
        list_shoppings = ListShopping.get_by_group_shopping(self.id)
        for shopping in list_shoppings:
            shopping.delete()
    
    def can_be_deleted(self):
        return True

    def get_format(self, symbol="/"):
        return self.creation_date.strftime(f"%d{symbol}%m{symbol}%Y")


class ListShopping(db.Model, ModelSaveDelete):
    __tablename__ = "list_shopping"

    id = COLUMN(INTEGER, primary_key=True, autoincrement=True, nullable=False)
    id_group_shopping = COLUMN(INTEGER, FK('groupshopping.id'), nullable=False)
    id_cost = COLUMN(INTEGER, FK('cost.id'), nullable=False)
    token = COLUMN(STRING(200), unique=True, nullable=False)
    note = COLUMN(STRING(512), nullable=True)
    quantity = COLUMN(INTEGER, nullable=False)

    cost = db.relationship("Cost")
    group_shopping = db.relationship("GroupShopping")

    _shoppingday = None
    _is_shoppingday = None

    def __repr__(self):
        return f"<ListShopping {self.id}: Product {self.cost.product.name}, ${self.cost.cost}, x{self.quantity}; {self.token}; ShoppingDay: {self.is_shoppingday}>"

    def get_shoppingday(self):
        if self._shoppingday is None and self._is_shoppingday is None:
            self._shoppingday = WorkDay.get_by_group_sale(self.group_sale.id)
            if self._shoppingday is None:
                self._is_shoppingday = False
            else:
                self._is_shoppingday = True

        return self._shoppingday

    def refresh_shoppingday(self):
        self._shoppingday = None
        self._is_shoppingday = None
        return self.get_shoppingday()

    def is_shoppingday(self):
        self.get_shoppingday()
        return (self._is_shoppingday == True)
    
    shoppingday = property(get_shoppingday)


    def save(self):
        db.session.add(self)
        if not self.token:
            self.token = generate_token(19)

        while self._exists_token(self.token):
            self.token = generate_token(19)

        try:
            db.session.commit()

        except IntegrityError:
            db.session.rollback()

    def _exists_token(self, token):
        if token is None:
            raise ValueError("Invalid Token.")

        listshopping = ListShopping.get_by_token(token)

        if listshopping is None:
            return False

        elif listshopping.id == self.id:
            return False

        return True

    @staticmethod
    def get_by_id(id):
        return ListShopping.query.get(id)

    @staticmethod
    def get_by_token(token):
        return ListShopping.query.filter_by(token=token).first()

    @staticmethod
    def get_by_product(id_product) -> list:
        return ListShopping.query.join(Cost).filter(Cost.id_product==id_product).\
            filter(Cost.id==ListShopping.id_cost).order_by(ListShopping.id_group_shopping).all()

    @staticmethod
    def get_by_cost(id_cost) -> list:
        return ListShopping.query.filter_by(id_cost=id_cost).\
            order_by(ListShopping.id_group_shopping).all()

    @staticmethod
    def get_by_shoppingday(id_shoppingday) -> list:
        shoppingday = ShoppingDay.get_by_id(id_shoppingday)
        return ListShopping.query.filter_by(id_group_shopping=shoppingday.id_group_shopping).all()

    @staticmethod
    def get_by_group_shopping(id_group_shopping) -> list:
        return ListShopping.query.filter_by(id_group_shopping=id_group_shopping).all()

    @staticmethod
    def get_by_cost_and_group_shopping(id_cost, id_group_shopping):
        return ListShopping.query.filter_by(id_group_shopping=id_group_shopping, id_cost=id_cost).first()

    @staticmethod
    def get_by_cost_and_shoppingday(id_cost, id_shoppingday):
        shoppingday = ShoppingDay.get_by_id(id_shoppingday)
        return ListShopping.query.filter_by(id_group_shopping=shoppingday.id_group_shopping, id_cost=id_cost).first()

    def can_be_deleted(self): # Always can be deleted.
        return True


class ShoppingDay(db.Model, ModelSaveDelete):
    __tablename__ = "shoppingday"

    id = COLUMN(INTEGER, primary_key=True, autoincrement=True, nullable=False)
    id_user = COLUMN(INTEGER, FK('user.id'), nullable=False)
    id_group_shopping = COLUMN(INTEGER, FK('groupshopping.id'), unique=True, nullable=False)
    token = COLUMN(STRING(200), unique=True, nullable=False)
    date = COLUMN(DATETIME, nullable=False, server_default=func.now())
    note = COLUMN(STRING(2048), nullable=True,)

    user = db.relationship("User", backref="shoppingdays")
    group_shopping = db.relationship("GroupShopping", back_populates="shoppingday", uselist=False)

    def __repr__(self):
        return f"<ShoppingDay {self.id}: {self.user.username}, {self.date}; {self.token}; {self.group_shopping}>"

    def save(self):
        db.session.add(self)
        if not self.token:
            self.token = generate_token(10)

        while self._exists_token(self.token):
            self.token = generate_token(10)

        try:
            db.session.commit()

        except IntegrityError:
            db.session.rollback()

    def _exists_token(self, token):
        if token is None:
            raise ValueError("Invalid Token.")

        shoppingday = ShoppingDay.get_by_token(token)

        if shoppingday is None:
            return False

        elif shoppingday.id == self.id:
            return False

        return True

    @staticmethod
    def get_by_id(id):
        return ShoppingDay.query.get(id)

    @staticmethod
    def get_by_token(token):
        return ShoppingDay.query.filter_by(token=token).first()

    @staticmethod
    def get_by_user(id_user):
        return ShoppingDay.query.filter_by(id_user=id_user).order_by(ShoppingDay.date).all()

    @staticmethod
    def get_by_group_sale(id_group_shopping, id_user):
        return ShoppingDay.query.filter_by(id_user=id_user, id_group_shopping=id_group_shopping).first()
    
    @staticmethod
    def get_by_date(id_user, date):
        return ShoppingDay.query.filter_by(id_user=id_user, date=date).order_by(ShoppingDay.date).first()
        
    @staticmethod
    def get_by_user_and_contains_notes(id_user):
        return ShoppingDay.query.filter_by(id_user=id_user).filter(ShoppingDay.note.isnot(None)).order_by(ShoppingDay.date).all() 

    def get_format(self, symbol="/"):
        return self.date.strftime(f"%d{symbol}%m{symbol}%Y")

    def get_day_name(self):
        day_number = self.date.isoweekday()
        return get_day_name(day_number)

    def get_products(self):
        list_shoppings = ListShopping.get_by_group_shopping(self.id_group_shopping)

        products = []
        for shopping in list_shoppings:
            product.append(shopping.cost.product)

        return products

    def get_shoppings(self):
        return ListShopping.get_by_group_shopping(self.id_group_shopping)
    
    def get_spendings(self):
        return ShoppingSpending.get_by_shoppingday(self.id)

    def get_resume(self, shoppings=None, spendings=None, profiles=None):
        if profiles is None:
            profiles = Profile.get_by_user(self.id_user, only_active=True)
        count = max(1, len(profiles))
        
        if shoppings is None:
            shoppings = self.get_shoppings()

        
        if spendings is None:
            spendings = self.get_spendings()

        total = {
            'quantity': 0,
            'price': 0,
            'rcost': 0,
            'cost': 0,
            'profit': 0,
            'percent_price_cost': 0,
            'percent_profit_cost': 0,
            'profile_count': count,
        }

        for shopping in shoppings:
            product = shopping.cost.product
            total['quantity'] += shopping.quantity
            total['price'] += shopping.cost.get_price() * shopping.quantity
            total['rcost'] += shopping.cost.get_real_cost() * shopping.quantity
            total['cost'] += shopping.cost.cost * shopping.quantity
            total['profit'] += (shopping.cost.get_price() - shopping.cost.get_real_cost())*shopping.quantity


        total_spending = {'count': 0, 'total': 0}

        total_spending['profiles'] = {profile: {'spending': 0, 'count': 0} for profile in profiles}

        for spending in spendings:
            total_spending['count'] += 1
            total_spending['total'] += spending.price

        total['spendings'] = total_spending

        total['profit_profile'] = int(round(total['profit'] / count))

        try:
            total['percent_profit_cost'] = round(100*total['profit'] / total['cost'], 2)
        except ZeroDivisionError:
            total['percent_profit_cost'] = 0

        try:
            total['percent_profit_price'] = round(100*total['profit'] /  total['price'], 2)
        except ZeroDivisionError:
            total['percent_profit_price'] = 0
        
        return total

    def get_mount_of_shoppings(self, shoppings=None, spendings=None):
        if shoppings is None:
            shoppings = self.get_shoppings()

        if spendings is None:
            spendings = self.get_spendings()
        
        total = {'price': 0, 'quantity': 0, 'cost': 0, 'rcost': 0, 'spendings': 0, 'spendings_count': 0}
        for shopping in shoppings:
            total['price'] += shopping.cost.get_price() * shopping.quantity
            total['rcost'] += shopping.cost.get_real_cost() * shopping.quantity
            total['cost'] += shopping.cost.cost * shopping.quantity
            total['quantity'] += shopping.quantity

        for spending in spendings:
            total['spendings_count'] += 1
            total['spendings'] += spending.price

        total['rprofit'] = total['price'] - total['rcost']
        total['profit'] = total['price'] - total['cost']

        return total

    def get_mount_of_spendings(self, spendings=None):
        if spendings is None:
            spendings = self.get_spendings()

        total = {'count': 0, 'mount': 0}
        for spending in spendings:
            total['count'] += 1
            total['mount'] += spending.price
        
        return total

    def get_date_as_tuple(self):
        return (self.date.year, self.date.month, self.date.day)

    def can_be_deleted(self):
        if not self.group_shopping.can_be_deleted():
            return False

        return True

    def between(self, min_date, max_date, format_date="%d/%m/%Y"):
        result1 = False
        result2 = False
        if min_date is None:
            result1 = True
        else:
            min_date = datetime.datetime.strptime(f"{min_date} 0#0#0", f"{format_date} %H#%M#%S")
            result1 = (min_date < self.date)

        if max_date is None:
            result2 = True
        else:
            max_date = datetime.datetime.strptime(f"{max_date} 23#59#59", f"{format_date} %H#%M#%S")
            result2 = (self.date < max_date)

        return result1 and result2


class ShoppingSpending(db.Model, ModelSaveDelete):
    __tablename__ = "shopping_spending"

    id = COLUMN(INTEGER, primary_key=True, autoincrement=True, nullable=False)
    id_shoppingday = COLUMN(INTEGER, FK('shoppingday.id'), nullable=False)
    name = COLUMN(STRING(64), nullable=False)
    description = COLUMN(STRING(256), nullable=True)
    price = COLUMN(INTEGER, nullable=False)
    token = COLUMN(STRING(200), unique=True, nullable=False)

    shoppingday = db.relationship("ShoppingDay", backref="spendings")

    def __repr__(self):
        return f"<ShoppingSpending {self.id}: {self.name}, ${self.price}; {self.token}; {self.shoppingday.date}>"

    def save(self):
        db.session.add(self)
        if not self.token:
            self.token = generate_token(14)

        while self._exists_token(self.token):
            self.token = generate_token(14)

        try:
            db.session.commit()

        except IntegrityError:
            db.session.rollback()

    def _exists_token(self, token):
        if token is None:
            raise ValueError("Invalid Token.")

        spending = ShoppingSpending.get_by_token(token)

        if spending is None:
            return False

        elif spending.id == self.id:
            return False

        return True

    @staticmethod
    def get_by_id(id):
        return ShoppingSpending.query.get(id)

    @staticmethod
    def get_by_token(token):
        return ShoppingSpending.query.filter_by(token=token).first()

    @staticmethod
    def get_by_shoppingday(id_shoppingday) -> list:
        return ShoppingSpending.query.filter_by(id_shoppingday=id_shoppingday).\
            order_by(ShoppingSpending.name).all()

    def get_name(self):
        return str(self.name).upper()

    def get_description(self):
        if self.description is None:
            return ""

        return self.description

    def can_be_deleted(self): # Always can be deleted.
        return True


class UserConfig(db.Model, ModelSaveDelete):
    __tablename__ = "userconfig"

    id = COLUMN(INTEGER, primary_key=True, autoincrement=True, nullable=False)
    id_user = COLUMN(INTEGER, FK('user.id'), nullable=False)
    key = COLUMN(STRING(200), unique=True, nullable=False)
    value = COLUMN(STRING(800), nullable=False)

    user = db.relationship("User", back_populates="configs")

    def __repr__(self):
        return f"<UserConfig {self.id}: {self.key} = {self.value}; {self.user}>"

    def save(self):
        db.session.add(self)

        try:
            db.session.commit()

        except IntegrityError:
            db.session.rollback()


    @staticmethod
    def get_by_id(id):
        return UserConfig.query.get(id)

    @staticmethod
    def get_by_user(id_user, only_active=False):
        return UserConfig.query.filter_by(id_user=id_user).order_by(UserConfig.key).all()
    
    @staticmethod
    def get_by_name(name, id_user):
        return UserConfig.query.filter_by(id_user=id_user).filter(func.upper(UserConfig.key) == name.upper()).first()

    def _preprocess(self):
        if self.value.lower() in ("false", "no", "off", "f"):
            return False

        elif self.value.lower() in  ("true", "yes", "on", "y"):
            return True
            
        else:
            return self.value

    def as_int(self):
        return int(self._preprocess())

    def as_float(self):
        return float(self._preprocess())

    def as_bool(self):
        return bool(self._preprocess())

    def as_str(self):
        return str(self.value)

    def as_json(self):
        return json.loads(self.value)

    def __int__(self):
        return self.as_int()

    def __float__(self):
        return self.as_float()
        
    def __bool__(self):
        return self.as_bool()

    def __str__(self):
        return self.as_str()
        
        
    process = process_as_json = property(as_json)
    process_as_int = property(as_int)
    process_as_float = property(as_float)
    process_as_str = property(as_str)


class Client(db.Model, ModelSaveDelete):
    __tablename__ = "client"

    id = COLUMN(INTEGER, primary_key=True, autoincrement=True, nullable=False)
    id_user = COLUMN(INTEGER, FK('user.id'), nullable=False)
    id_group_sale = COLUMN(INTEGER, FK('groupsale.id'), unique=True, nullable=False)

    # Datos del cliente
    name = COLUMN(STRING(256), nullable=False)
    description = COLUMN(STRING(2048), nullable=True)
    telephone = COLUMN(STRING(20), nullable=True)
    telephone_alt = COLUMN(STRING(20), nullable=True)
    phone_number = COLUMN(STRING(20), nullable=True)
    phone_number_alt = COLUMN(STRING(20), nullable=True)
    email = COLUMN(STRING(320), nullable=True)
    address = COLUMN(STRING(128), nullable=True)
    location = COLUMN(STRING(128), nullable=True)
    credit_amount = COLUMN(FLOAT, nullable=True)

    # Otros datos
    token = COLUMN(STRING(200), unique=True, nullable=False)
    creation_date = COLUMN(DATETIME, nullable=False, server_default=func.now())
    note = COLUMN(STRING(2048), nullable=True)

    user = db.relationship("User", backref="clientes")
    group_sale = db.relationship("GroupSale", back_populates="client", uselist=False)

    def __repr__(self):
        return f"<Client {self.id}: {self.user.username}, {self.name}; {self.token}; {self.group_sale}>"

    def save(self):
        db.session.add(self)
        if not self.token:
            self.token = "c-"+generate_token(14)

        while self._exists_token(self.token):
            self.token = "c-"+generate_token(14)

        try:
            db.session.commit()

        except IntegrityError:
            db.session.rollback()

    def _exists_token(self, token):
        if token is None:
            raise ValueError("Invalid Token.")

        client = Client.get_by_token(token)

        if client is None:
            return False

        elif client.id == self.id:
            return False

        return True

    @staticmethod
    def get_by_id(id):
        return Client.query.get(id)

    @staticmethod
    def get_by_token(token):
        return Client.query.filter_by(token=token).first()

    @staticmethod
    def get_by_user(id_user):
        return Client.query.filter_by(id_user=id_user).order_by(Client.name).all()

    @staticmethod
    def get_by_group_sale(id_group_sale, id_user):
        return Client.query.filter_by(id_user=id_user, id_group_sale=id_group_sale).first()
    
    @staticmethod
    def get_by_date(id_user, date):
        return Client.query.filter_by(id_user=id_user, creation_date=date).first()

    @staticmethod
    def get_by_name(id_user, name):
        return Client.query.filter_by(id_user=id_user).filter(func.upper(Client.name) == name.upper()).first()
    
    @staticmethod
    def get_by_user_and_contains_notes(id_user):
        return Client.query.filter_by(id_user=id_user).filter(Client.note.isnot(None)).order_by(Client.name).all() 

    def has_any_property(self):
        if (self.description or self.telephone or self.telephone_alt or \
            self.phone_number or self.phone_number_alt or self.email or \
                self.address or self.location):
            return True

        else:
            return False

    def get_format(self, symbol="/"):
        return self.creation_date.strftime(f"%d{symbol}%m{symbol}%Y")

    def get_name(self):
        return self.name.upper()

    def get_contact(self, email=False, separator="\n"):
        data = []
        for item in [self.phone_number, self.phone_number_alt, self.telephone, self.telephone_alt]:
            data.append(str(item))

        if self.email and email:
            data.append(str(self.email))

        return separator.join(data)

    def get_products(self):
        list_sales = ListSales.get_by_group_sale(self.id_group_sale)

        products = []
        for sale in list_sales:
            product.append(sale.cost.product)

        return products

    def get_sales(self):
        return ListSales.get_by_group_sale(self.id_group_sale)

    def get_spendings(self):
        return []

    def get_resume(self, sales=None, spendings=None, profiles=None):
        if profiles is None:
            profiles = Profile.get_by_user(self.id_user, only_active=True)
        count = max(1, len(profiles))
        
        if sales is None:
            sales = self.get_sales()

        if spendings is None:
            spendings = self.get_spendings()

        total = {
            'quantity': 0,
            'price': 0,
            'cost': 0,
            'original_cost': 0,
            'original_extra_cost': 0,
            'original_rcost': 0,
            'profit': 0,
            'default_price': 0,
            'percent_price_cost': 0,
            'percent_profit_cost': 0,
            'profile_count': count,
        }

        for sale in sales:
            product = sale.cost.product
            total['quantity'] += sale.quantity
            total['price'] += sale.price * sale.quantity
            total['default_price'] += sale.cost.get_price() * sale.quantity
            total['cost'] += sale.cost.get_real_cost()*sale.quantity
            total['profit'] += (sale.price - sale.cost.get_real_cost())*sale.quantity
            
            total['original_cost'] += sale.cost.cost*sale.quantity
            total['original_extra_cost'] += sale.cost.extra_cost*sale.quantity
            total['original_rcost'] += sale.cost.get_real_cost()*sale.quantity


        total_spending = {'count': 0, 'total': 0, 'general_count': 0, 'general_spending': 0, 'profiles': {}}

        total_spending['profiles'] = {profile: {'spending': 0, 'count': 0} for profile in profiles}

        for spending in spendings:
            total_spending['count'] += 1
            total_spending['total'] += spending.price

            if spending.profile is None:
                total['cost'] += spending.price
                total['profit'] -= spending.price
                total_spending['general_spending'] += spending.price
                total_spending['general_count'] += 1
            else:
                profile = spending.profile
                if not profile in total_spending['profiles']:
                    continue
                
                dc = total_spending['profiles'][profile]
                
                dc['spending'] += spending.price
                dc['count'] += 1

        total['spendings'] = total_spending
        total['profit_profile'] = int(round(total['profit'] / count))

        try:
            total['percent_profit_cost'] = round(100*total['profit'] / total['cost'], 2)
        except ZeroDivisionError:
            total['percent_profit_cost'] = 0

        try:
            total['percent_profit_price'] = round(100*total['profit'] /  total['price'], 2)
        except ZeroDivisionError:
            total['percent_profit_price'] = 0
        
        return total

    def get_mount_of_sales(self, sales=None, spendings=None):
        if sales is None:
            sales = self.get_sales()

        if spendings is None:
            spendings = self.get_spendings()
        
        total = {'price': 0, 'quantity': 0, 'cost': 0, 'spendings_count': 0, 'spendings': 0}
        for sale in sales:
            total['price'] += sale.price * sale.quantity
            total['cost'] += sale.cost.get_real_cost() * sale.quantity
            total['quantity'] += sale.quantity

        for spending in spendings:
            total['spendings_count'] += 1
            total['spendings'] += spending.price

            if spending.profile is None:
                total['cost'] += spending.price

        total['profit'] = total['price'] - total['cost']
        return total

    def get_mount_of_spendings(self, spendings=None):
        if spendings is None:
            spendings = self.get_spendings()

        total = {'count': 0, 'mount': 0}
        for spending in spendings:
            total['count'] += 1
            total['mount'] += spending.price
        
        return total

    def get_date_as_tuple(self):
        return (self.date.year, self.date.month, self.date.day)

    def can_be_deleted(self):
        sales = self.get_sales()
        if not self.group_sale.can_be_deleted():
            return False

        if sales is not None and len(sales) >= 1:
            spendings = self.get_spendings()
            if spendings is not None and len(spendings) >= 1:
                return False
        
        return True


class ClientSale(db.Model, ModelSaveDelete):
    __tablename__ = "client_sale"

    id = COLUMN(INTEGER, primary_key=True, autoincrement=True, nullable=False)
    id_list_sales = COLUMN(INTEGER, FK('list_sales.id'), nullable=False, unique=True)
    profit_paid = COLUMN(BOOLEAN, unique=False, nullable=False)
    date = COLUMN(DATETIME, nullable=False, server_default=func.now())
    note = COLUMN(STRING(512), nullable=True)

    list_sales = db.relationship("ListSales")

    def __repr__(self):
        return f"<ClientSale {self.id}: ListSales {self.list_sales}, ${self.profit_paid}>"

    def save(self):
        db.session.add(self)
        try:
            db.session.commit()

        except IntegrityError:
            db.session.rollback()

    @staticmethod
    def get_by_id(id):
        return ClientSale.query.get(id)

    @staticmethod
    def get_by_list_sales(id_list_sales):
        if isinstance(id_list_sales, ListSales):
            id_list_sales = id_list_sales.id

        return ClientSale.query.filter_by(id_list_sales=id_list_sales).first()

    def can_be_deleted(self): # Always can be deleted.
        return True


def generate_token(self, number=10):
    return secrets.token_hex(number)
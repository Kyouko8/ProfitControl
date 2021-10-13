import secrets

from flask_login import UserMixin
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import func
from werkzeug.security import check_password_hash, generate_password_hash

from app import db
from app.constants import COLUMN, INTEGER, STRING, DATETIME
from app.models import UserConfig


class User(db.Model, UserMixin):
    __tablename__ = "user"

    id = COLUMN(INTEGER, primary_key=True, autoincrement=True, nullable=False)
    username = COLUMN(STRING(256), unique=False, nullable=False)
    email = COLUMN(STRING(256), unique=True, nullable=False)
    password = COLUMN(STRING(400), unique=True, nullable=False)
    token = COLUMN(STRING(200), unique=True, nullable=False)
    creation_date = COLUMN(DATETIME, nullable=False, server_default=func.now())

    def __repr__(self):
        return f"<User {self.id}:{self.email} with token {self.token}>"

    configs = db.relationship("UserConfig", back_populates="user", uselist=False)

    def save(self):
        db.session.add(self)
        if not self.token:
            self.token = self._generate_token()

        self.email = self.email.lower()

        while self._exists_token(self.token):
            self.token = self._generate_token()

        try:
            db.session.commit()

        except IntegrityError:
            db.session.rollback()

    def delete(self):
        try:
            db.session.delete(self)

        except:
            db.session.rollback()

        finally:
            db.session.commit()

    def _generate_token(self):
        return secrets.token_hex(12)

    def exists_email(self, email):
        if email is None:
            raise ValueError("Invalid Email.")

        return not (User.get_by_email(email) is None)

    def _exists_token(self, token):
        if token is None:
            raise ValueError("Invalid Token.")

        user = User.get_by_token(token)

        if user is None:
            return False

        elif user.id == self.id:
            return False

        return True

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def get_creation_date_format(self, symbol="/", include_time=False):
        if include_time:
            return self.creation_date.strftime(f"%d{symbol}%m{symbol}%Y %H:%M")

        return self.creation_date.strftime(f"%d{symbol}%m{symbol}%Y")

    @staticmethod
    def get_by_email(email):
        return User.query.filter_by(email=email.lower()).first()

    @staticmethod
    def get_by_token(token):
        return User.query.filter_by(token=token).first()

    @staticmethod
    def get_by_id(id_user):
        return User.query.get(id_user)

    def get_all_configs(self):
        return UserConfig.get_by_user(self.id)

    def get_config(self, key) -> UserConfig:
        return UserConfig.get_by_name(key, self.id)

    def get_config_force(self, key, default_value) -> UserConfig:
        config = self.get_config(key)
        if config is None:
            config = UserConfig(id_user=self.id, key=key, value=str(default_value))
            config.save()

        return config

    def set_config(self, key, value) -> bool:
        config = self.get_config(key)
        if config is None:
            config = UserConfig(id_user=self.id, key=key, value=str(value))
        else:
            config.value = str(int(value))
        
        config.save()
        return config

    def get_simple_mode(self) -> bool:
        config = self.get_config_force("simple_mode", 1)
        return (config.as_int() == 1)

    def set_simple_mode(self, value) -> bool:
        config = self.set_config("simple_mode", value)
        return (config.as_int() == 1)


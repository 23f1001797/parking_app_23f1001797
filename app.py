from flask import Flask
from flask_security import SQLAlchemyUserDatastore, Security, hash_password

from config import LocalDevelopmentConfig
from application.database import db
from application.models import User, Role, UserRoles

def create_app():
    app = Flask(__name__)
    app.config.from_object(LocalDevelopmentConfig)

    db.init_app(app)

    datastore = SQLAlchemyUserDatastore(db, User, Role)
    app.security = Security(app, datastore)

    app.app_context().push()
    return app

app = create_app()

with app.app_context():
    db.create_all()

    app.security.datastore.find_or_create_role(name = 'admin', description = 'Super User')
    app.security.datastore.find_or_create_role(name = 'user', description = 'User')

    db.session.commit()

    if not app.security.datastore.find_user(email = "user0@admin.com"):
        app.security.datastore.create_user(
            email = "user0@admin.com",
            username = "admin",
            password = hash_password("1111"),
            roles = ['admin'],
        )
    db.session.commit()

from application.routes import *

if __name__ == "__main__":
    app.run()
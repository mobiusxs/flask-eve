from flask_eve import Eve
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
eve = Eve()
migrate = Migrate()

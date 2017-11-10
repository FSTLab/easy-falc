from flask_sqlalchemy import sqlalchemy

from database import metadata

db = SQLAlchemy(metadata=metadata)

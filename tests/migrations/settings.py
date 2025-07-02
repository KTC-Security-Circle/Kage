from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

path = "sqlite:///db.sqlite3"
# path = 'mysql+pymysql://root:@127.0.0.1:3306/alembic_sample'

# Engine の作成
Engine = create_engine(path, echo=False)
Base = declarative_base()

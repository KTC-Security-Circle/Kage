from sqlalchemy import Column, Integer, String

from settings import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    fullname = Column(String)
    nickname = Column(String)

    def __repr__(self) -> str:
        return f"<User('name={self.name}', fullname={self.fullname}, nickname={self.nickname})>"


class Ask(Base):
    __tablename__ = "asks"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)  # Assuming a foreign key to User
    title = Column(String)
    content = Column(String)

    def __repr__(self) -> str:
        return f"<Ask('title={self.title}', content={self.content})>"

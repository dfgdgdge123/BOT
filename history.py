from sqlalchemy import create_engine, Column, Integer, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base

Base = declarative_base()


class UserDish(Base):
    __tablename__ = 'history'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    dish_id = Column(Integer, nullable=False)


def add_dish(user_id, dish_id):  # добавление блюда
    engine = create_engine('sqlite:///history.db')
    Session = sessionmaker(bind=engine)
    session = Session()

    # Проверка существование записи
    result = session.query(UserDish).filter_by(
        user_id=user_id,
        dish_id=dish_id
    ).first()

    if not result:
        new_record = UserDish(user_id=user_id, dish_id=dish_id)
        session.add(new_record)
        session.commit()

    session.close()


def show_dishes(user_id):  # возврат списка истории блюд
    engine = create_engine('sqlite:///history.db')
    Session = sessionmaker(bind=engine)
    session = Session()

    result = session.query(UserDish).filter_by(user_id=user_id).all()
    return [obj.dish_id for obj in result]

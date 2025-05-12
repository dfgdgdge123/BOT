from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

Base = declarative_base()


class UserDish(Base):
    __tablename__ = 'favorites'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    dish_id = Column(Integer, nullable=False)
    dish_name = Column(String, nullable=False)


def add_to_favorites(user_id, dish_id, dish_name):  # добавление блюда
    engine = create_engine('sqlite:///database.db')
    Session = sessionmaker(bind=engine)
    session = Session()

    # Проверка существование записи
    result = session.query(UserDish).filter_by(
        user_id=user_id,
        dish_id=dish_id,
    ).first()

    if not result:
        new_record = UserDish(user_id=user_id, dish_id=dish_id, dish_name=dish_name)
        session.add(new_record)
        session.commit()

    session.close()


def get_favorites(user_id):  # возврат списка кортежей понравившихся блюд
    engine = create_engine('sqlite:///database.db')
    Session = sessionmaker(bind=engine)
    session = Session()

    result = session.query(UserDish).filter_by(user_id=user_id).all()
    session.close()
    return [(obj.dish_id, obj.dish_name) for obj in result]


def check_recipe_in_db(user_id, dish_id):
    engine = create_engine('sqlite:///database.db')
    Session = sessionmaker(bind=engine)
    session = Session()

    result = session.query(UserDish).filter_by(
        user_id=user_id,
        dish_id=dish_id,
    ).first()
    session.close()
    return bool(result)


def remove_from_favorites(user_id, dish_name):
    engine = create_engine('sqlite:///database.db')
    Session = sessionmaker(bind=engine)
    session = Session()

    session.query(UserDish).filter(UserDish.user_id == user_id, UserDish.dish_name == dish_name).delete()
    session.commit()
    session.close()


def create_favorite_button(recipe_id):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("⭐ Add to favorites", callback_data=f"add_to_favorites: {recipe_id}"))
    return markup

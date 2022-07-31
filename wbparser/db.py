from sqlalchemy import Column, Float, Integer, String, create_engine, engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, mapper

base = declarative_base()
engine = create_engine('sqlite:///category.db')
engine.connect()
session = Session(bind=engine)


class Card(base):
    __tablename__ = 'Card'
    id = Column(Integer, primary_key=True)
    brand = Column(String(128))
    card_name = Column(String(256))
    name = Column(String(256))
    price = Column(Integer, nullable=False)
    old_price = Column(Integer, nullable=True)
    description = Column(String(2048))
    rating = Column(Float)


class Db():
    def write_db(self, data):
        wb_cards = []
        for record in data:
            wb_cards.append(Card(id = record['id'], brand = record['brand'], card_name = record['card_name'],
                name = record['name'], price = record['price'], old_price = record['old_price'],
                description = record['description'], rating = record['rating']))
        session.add_all(wb_cards)
        session.commit()

    def get(self):
        show = session.query(Card).all()
        return show

    def drop(self):
        base.metadata.drop_all(engine)
        base.metadata.create_all(engine)

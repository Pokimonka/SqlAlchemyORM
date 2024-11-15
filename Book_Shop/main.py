import json
import os

import sqlalchemy
from sqlalchemy.orm import sessionmaker

from model import create_tables, Publisher, Shop, Book, Stock, Sale

# os.environ["DB_USER_NAME"] = "postgres"
# os.environ["PASSWORD"] = "password"
# os.environ["DB_NAME"] = "book_shop"

DB_USER_NAME = os.getenv("DB_USER_NAME")
PASSWORD = os.getenv("PASSWORD")
DB_NAME = os.getenv("DB_NAME")

DSN = f'postgresql://{DB_USER_NAME}:{PASSWORD}@localhost:5432/{DB_NAME}'
engine = sqlalchemy.create_engine(DSN)

create_tables(engine)

Session = sessionmaker(bind=engine)
session = Session()

def get_shops(id_or_name):
     response = (session.query(Book.title, Shop.name, Sale.price, Sale.date_sale)
                    .select_from(Shop)
                    .join(Stock).filter(Stock.id_shop == Shop.id)
                    .join(Book).filter(Book.id == Stock.id_book)
                    .join(Publisher).filter(Publisher.id == Book.id_publisher)
                    .join(Sale).filter(Sale.id_stock == Stock.id))
     if id_or_name.isdigit():
          res = response.filter(Publisher.id == id_or_name).all()
     else:
          res = response.filter(Publisher.name == id_or_name).all()
     if res:
          for title, name, price, date in res:
               #если оставить ваше форматирование, то в ответе много пробелов
               #Modern Operating Systems                 | OZON       | 16.00    | 25-10-2018
               #print(f"{title: <40} | {name: <10} | {price: <8} | {date.strftime('%d-%m-%Y')}")
               print(f"{title} | {name} | {price} | {date.strftime('%d-%m-%Y')}")
     else:
          print('Такой покупки не найдено')


if __name__ == '__main__':

     with open("fixtures/test_data.json", 'r') as td:
          data = json.load(td)

     for record in data:
          model = {
               'publisher': Publisher,
               'shop': Shop,
               'book': Book,
               'stock': Stock,
               'sale': Sale
          }[record.get('model')]
          session.add(model(id=record.get('pk'), **record.get('fields')))
     session.commit()

     print("Введите имя или ID автора:")
     publisher_name = input()

     get_shops(publisher_name)

     session.close()
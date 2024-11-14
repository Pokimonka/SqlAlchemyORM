import json
import os

import sqlalchemy
from sqlalchemy import false, func
from sqlalchemy.orm import sessionmaker

from model import create_tables, Publisher, Shop, Book, Stock, Sale


if __name__ == '__main__':

     #для тестирования
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

     print("Введите имя автора:")
     publisher_name = input()

     response = (session.query(Book.title, Shop.name, Sale.price, func.to_char(Sale.date_sale, 'dd-mm-yyyy'))
          .join(Stock.book).filter(Stock.id_book == Book.id)
          .join(Shop).filter(Shop.id == Stock.id_shop)
          .join(Publisher).filter(Publisher.id == Book.id_publisher).filter(Publisher.name == publisher_name)
          .join(Sale).filter(Sale.id_stock == Stock.id)).all()
     if response:
          for item in response:
               print(' | '.join(list(item)))
     else:
          print('Такой покупки не найдено')

     session.close()
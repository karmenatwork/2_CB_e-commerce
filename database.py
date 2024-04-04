import json

class User:
    def __init__(self, id, email, password, admin = 0, **kwargs ):
        self.id = id 
        self.email = email
        self.password = password
        self.admin = admin
        self.cart = {}
        for k, v in kwargs.items():
            self.__setattr__(k, v)

    def is_admin(self):
        return self.admin == 1
    
    def __iter__(self):
        return self.__dict__.items()
    
class Admin:
    def __init__(self, email, password):
        self.email = email
        self.password = password       
    
class Category:
    def __init__(self, id, name, description):
        self.id = id
        self.name = name
        self.description = description
        
class Product:
    def __init__(self, id, name, author, description, price, category_name, category_id):
        self.id = id
        self.name = name
        self.author = author
        self.price = price
        self.description = description
        self.category = category_name
        self.category_id = category_id

class DummyEcommerceDB:
    def __init__(self):
        self.users = {}
        self.admins = {}
        self.catalogs = {}
        self.categories = {}
        self.products = {}
        self.user_id_counter = 1
        self.category_id_counter = 1
        self.product_id_counter = 1

import json

class User:
    def __init__(self, id, name, email, password, admin = 0):
        self.id = id 
        self.name = name
        self.email = email,
        self.password = password
        self.admin = admin

    def is_admin(self):
        return self.admin == True
    
    def __iter__(self):
        return self.__dict__.items()    

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
        self.catalogs = {}
        self.categories = {}
        self.products = {}

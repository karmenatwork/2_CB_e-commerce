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
    
    def email(self):
        str(self.email)
        

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
        self.title = name
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

    
    def register(self, name, email, password, is_admin=0):
        last_user = list(self.users.keys())[-1]
        new_user_id = self.users[last_user]["id"] + 1
        if email in self.users:
            return False, f"User {email} already exists."
        self.users[email] = { "id": new_user_id, "name": name, "email": email, "password": password, "admin": is_admin}
        return True, "User registered successfully.", self.users[email]

    def add_category(self, email, category_name, description):
        categories = self.categories
        category_key = "_".join(category_name.lower().split())
        if category_key in categories:
            return "Category already exists."
        categories[category_key] = {"name": category_name, "description": description}
        return True, "Category added successfully.", self.categories

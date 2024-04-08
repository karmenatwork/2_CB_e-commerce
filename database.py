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
    def __init__(self, id, email, password):
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
        self.admin_id_counter = 1
        self.category_id_counter = 1 
        self.product_id_counter = 1


    def add_user(self, email, password, user_type="user", **kwargs):
        admin = 1 if user_type == "admin" else 0
        if email in self.users:
            # print(f"User {email} already exists")
            return False, f"User {email} already exists", None
        
        user = User(self.user_id_counter,email, password, admin, **kwargs)
        self.users[email] = user
        # self.users[email] = User(self.user_id_counter,email, password, admin, **kwargs)
        self.user_id_counter += 1
        if user_type == "admin":
            self.add_admin(email, password)

        return True, f"User {email} added successfully", user

    def add_admin(self, email, password):
        if email in self.admins:
            # print(f"Admin {email} already exists")
            return False, f"Admin {email} already exists", None
        
        self.admins[email] = Admin(self.admin_id_counter, email, password)
        self.admin_id_counter += 1
        return True, f"User {email} added successfully", self.admins[email]

      

db = DummyEcommerceDB()
# Adding just user
db.add_user("user1@test.com", "userpass", "user", name = "Bianca")
print(db.users["user1@test.com"].__dict__)
db.add_user("user2@test.com", "userpass")
print(db.users["user2@test.com"].__dict__)
# Adding just admin
db.add_admin("admin1@test.com", "adminpass1")
print(db.admins["admin1@test.com"].__dict__)
# Adding user that is an admin too
db.add_user("admin2@test.com", "adminpass2", "admin", name = "Juan")
print(db.admins["admin2@test.com"].__dict__)

# Already exists
print(db.add_user("admin2@test.com", "adminpass2", "admin", name = "Juan"))
print(db.add_admin("admin1@test.com", "adminpass1"))




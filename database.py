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
    def __init__(self, id, name, description, price, category_name, category_id, **kwargs):
        self.id = id
        self.name = name
        self.author = kwargs.get("author", None)
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

    def add_category(self, name, description):
        categories = self.categories
        category_key = "_".join(name.lower().split())
        if category_key in categories:
            # print(f"Category {category_name} already exists.")
            return False, f"Category '{name}' already exists.", None
        
        ##  Add data to db.categories and update db.catalogs. Note n  
        category_data = {"id": self.category_id_counter, "name": name, "description": description}
        categories[category_key] = category_data
        self.category_id_counter += 1

        if category_key in self.catalogs:
            self.catalogs[category_key].update(category_data)
        else:
            self.catalogs[category_key] = category_data

        # print(f"Category '{category_name}' added successfully.")
        return True , f"Category '{name}' added successfully.", categories[category_key]

    def add_product(self, name, description, price, category, **kwargs):
        categories = self.categories
        if category not in self.categories:
            # print("Invalid category.")
            return False, f"Invalid category ({category}).", None
        # categories[category]['products']
        if 'products' in categories[category]:
            for product in categories[category]['products']:
                if name == product.name and price == product.price:
                    return False, f"Product {name} already exists in {category}.", None

        category_id = categories[category]['id']
        item = Product(self.product_id_counter, name, description, price, category, category_id, **kwargs)
        self.products[self.product_id_counter] = item
        if 'products' in self.categories[category]:
            self.categories[category]["products"].append(item)
        else:
            self.categories[category]["products"] = [item]

        self.product_id_counter += 1
        # print(f"Product '{name}' added to category '{category}' successfully.")
        return True, f"Product '{name}' added to category '{category}' successfully.", item    
   

db = DummyEcommerceDB()
# Adding just user
# db.add_user("user1@test.com", "userpass", "user", name = "Bianca")
# print(db.users["user1@test.com"].__dict__)
# db.add_user("user2@test.com", "userpass")
# print(db.users["user2@test.com"].__dict__)
# # Adding just admin
# db.add_admin("admin1@test.com", "adminpass1")
# print(db.admins["admin1@test.com"].__dict__)
# # Adding user that is an admin too
# db.add_user("admin2@test.com", "adminpass2", "admin", name = "Juan")
# print(db.admins["admin2@test.com"].__dict__)

# # Already exists
# print(db.add_user("admin2@test.com", "adminpass2", "admin", name = "Juan"))
# print(db.add_admin("admin1@test.com", "adminpass1"))

# Add category and products 
print(db.add_category("Home Appliances", "Everything you need to make your home comfortable")[1])
print(db.add_product("Lamp to relax", "Himalayan Pink Lamp", 19.99, 'home_appliances')[1])
print(db.add_product("Lamp to relax", "Himalayan Pink Lamp", 19.99, 'home')[1])

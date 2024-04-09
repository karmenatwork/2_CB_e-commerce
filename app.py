import utils
import json
import uuid

from database import DummyEcommerceDB
from database import User, Admin, Product

def load_json_file(filename):
    fullfilepath = f"data/{filename}.json"
    print(f"Loading demo {filename} from JSON file ... \n")
    f = open(fullfilepath)
    # # returns JSON object as a dictionary
    data = json.loads(f.read())
    f.close
    return data 

class ECommerceApp:
    def __init__(self):
        self.sessions = {}
        self.db = DummyEcommerceDB()

    #==== Load data from data/*.json ===    
    def load_users(self):
        data = load_json_file("users")
        
        # Initialize counters
        user_id_counter = self.db.user_id_counter
        admin_id_counter = self.db.admin_id_counter

        # Iterating through the json  list
        # Use the enumerate() function to generate the user IDs automatically,
        for idx, user_data in enumerate(data, start=user_id_counter):
            # users[user['email']] = {**user_data, **{'id': idx}}
            user = User(idx, user_data['email'], user_data['password'], user_data['admin'], name = user_data['name'])
            self.db.users[user_data['email']] = user

            if user.is_admin():
                self.db.admins[user.email] = Admin(admin_id_counter, user.email, user.password)
                admin_id_counter += 1
                
        self.db.user_id_counter = user_id_counter
        self.db.admin_id_counter = admin_id_counter

        dbUsers_emails = self.db.users.keys()
        
        print(f"Total demo users: {len(dbUsers_emails)} - {list(dbUsers_emails)} \n")
        print(f"Total demo admins: {list(self.db.admins.keys())} \n")
        return True
    
    def load_catalog(self):
        catalogs = load_json_file("catalog")

        for (category_key, category) in catalogs.items():
            # Initialize counter    
            last_category_id = self.db.category_id_counter

        #     ## Categories. Populate db.categories if empty, if not, update data. Remove key products
            category_data = category.copy()
            if category_data["products"]:
                del category_data["products"]
        #     # print(f'category_data {category_data}')
            print(category_data)

            status, _message, category_obj = self.db.add_category(**category_data)
            if status == False:
                next
            
            ## Initialize product attributes
            category_name = category["name"]
            prodId = self.db.product_id_counter

            category_products = []
            for prod_idx, product in enumerate(category["products"], start= prodId):
        #       # # Build 1 to many relationship Category <-> Products
                product_data = {**product, **{'id': prod_idx, 'category_id': last_category_id, 'category_name': category_name }}
                print(f"product_data => {product_data}")

                status, message, product_obj = self.db.add_product(product["name"], product["description"], product["price"], category_key)
                
                if status == False:
                    next
                
                category_products.append(product_data)

            self.db.catalogs[category_key]["products"] = category_products

        # print(f"Total demo categories: {len(db.categories)} - Total demo products: {len(db.products)}\n")
        return({'catalog': self.db.catalogs, "categories": self.db.categories, "products": self.db.products})



    def login(self, email, password, user_type='user'):
        users = self.db.users
        if user_type == 'user':
            if email not in users or users[email].password != password:
                # print("Invalid username or password.")
                return False, "Invalid username or password."
            session_id = str(uuid.uuid4())
            self.sessions[session_id] = users[email]
            print(f"User {email} logged in successfully!")
            return session_id
        elif user_type == 'admin':
            admins = self.db.admins
            if email not in admins or admins[email].password != password:
                # print("Invalid admin username or password.")
                return False, "Invalid admin username or password."
            session_id = str(uuid.uuid4())
            self.sessions[session_id] = self.db.admins[email]
            print(f"Admin {email} logged in successfully!")
            return session_id

    ## To register User and/Or Admin 
    def register(self, email, password, user_type="user", **kwargs):
    
        users = self.db.users
        # Generate id manually to simulate DB
        new_user_id = self.db.user_id_counter

        if email in self.db.users:
            print(f"User {email} already exists.")
            return False 

        result = self.db.add_user(email, password, user_type, **kwargs)
        status, message, user = result
        return message
    
    ## To register just admins
    def register_admin(self, email, password ):
        result = self.db.add_admin(email, password)
        status, message, user = result
        print(message)
        return status

    def must_be_admin(func):
        def wrapper(self, session_id, *args, **kwargs):
            print(session_id )
            if session_id in self.sessions and isinstance(self.sessions[session_id], Admin):
                return func(self, session_id, *args, **kwargs)
            else:
                # print("Admin privileges required." )
                return False,"Admin privileges required." 
        return wrapper
    
    @must_be_admin
    def add_category(self, session_id, category_name, description):
        result = self.db.add_category(category_name, description)
        print(result)

        return result[1] # message
    
    @must_be_admin
    def add_product(self, session_id, name, description, price, category, **kwargs):
        result = self.db.add_product(name, description, price, category, **kwargs)
        return result[1] # message 
    
app = ECommerceApp()
# app.load_users()
# # print(list(app.db.users.keys()))
print(app.register( "admin@test.com", "adminpass", user_type="admin", name="admin1" ))
print(app.register( email ="user@test.com", password ="userpass", name="Carmencita" ))

#Admin login
admin_session_id = app.login("admin@test.com", "adminpass", user_type='admin')

# User login
user_session_id = app.login("user@test.com", "userpass", user_type='user')

print(utils.print_divider())
# Add category as Admin should be valid
print(app.add_category(admin_session_id, "Home Appliances", "Everything you need for your home"))
print(app.add_product(admin_session_id, "Ruby for children", "Teaching Ruby to children", 19.99, "books", author = "Carmen Diaz"))

print(utils.print_divider())
# Add category as User should be invalid
print(app.add_category(user_session_id, "Home Appliances", "Everything you need for your home"))
print(app.add_product(user_session_id, "Teach your kids to Code", "Teaching code in a fun way", 10.00, "books", author = "Carmen Diaz"))

# Load catalog
app.load_catalog()
print(utils.print_divider())

# It should keep category previously added
print(app.db.categories.keys()) # it should be 4 keys
print(app.add_product(admin_session_id,"Lamp to relax", "Himalayan Pink Lamp", 19.99, 'home_appliances'))

print(app.db.categories["home_appliances"]) # it should now has products
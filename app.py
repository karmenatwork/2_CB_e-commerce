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
            last_category_id = self.db.category_id_counter
            # Categories. Populate db.categories if empty, if not, update data. Remove key products
            category_data = category.copy()
            if category_data["products"]:
                del category_data["products"]
            # print(f'category_data: {category_data}')

            status, message, category_obj = self.db.add_category(**category_data)
            print(message)
            if status == False:
                next
            # print(self.db.categories)
            ## Initialize product attributes
            category_name = category_obj["name"]
            prodId = self.db.product_id_counter

            for prod_idx, product in enumerate(category["products"], start= prodId):
        #       # # Build 1 to many relationship Category <-> Products
                product_data = {**product, **{'id': prod_idx, 'category_id': last_category_id, 'category_name': category_name }}
                # print(f"product_data => {product_data}")

                status, message, product_obj = self.db.add_product(product["name"], product["description"], product["price"], category_key)
                print(f"{message} {product_obj} {type(product_obj)}\n")
                # print(f"category_key:{self.db.categories[category_key]}")

                if status == False:
                    next
                
            
            # self.db.catalog[category_key]["products"] = []
            # print(self.db.categories["books"])
        # print(f"Total demo categories: {len(db.categories)} - Total demo products: {len(db.products)}\n")
        return({ "categories": self.db.categories, "products": self.db.products})

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
    
    def view_categories(self):
        categories = self.db.categories
        print(utils.print_header("View Categories"))
        for category in categories:
            print(f"\nCategory : {categories[category]['name']}")
            if 'products'in categories[category]:
                for item in categories[category]['products']:
                    # print(item)
                    print(f"  {item.id}: {item.name} - ${item.price}")
            else:
                print("==No products \n")
        print("="* 80)
        return True
    
    # decorator
    def must_be_user(func):
        def wrapper(self, session_id, *args, ** kwargs):
            if session_id not in self.sessions or isinstance(self.sessions[session_id], Admin):
                print("User privileges required.")
                return False
            else:
                return func(self, session_id, *args, **kwargs)
        return wrapper

    @must_be_user
    def add_to_cart(self, session_id, product_id, quantity):
        # if session_id not in self.sessions or isinstance(self.sessions[session_id], Admin):
        #     print("User privileges required.")
        #     return False
        user = self.sessions[session_id]
        if product_id not in self.db.products:
            print("Invalid Product ID.")
            return False
        if product_id in user.cart:
            user.cart[product_id] += quantity
        else:
            user.cart[product_id] = quantity
        print(f"Item '{self.db.products[product_id].name}' added to cart. Quantity: {quantity}")
        return True
    
    def remove_from_cart(self, session_id, product_id, quantity):
        user = self.sessions[session_id]
        if product_id not in user.cart:
            print("Item not found in cart.")
            return False
        print(f"product_id {product_id}'qty: {user.cart[product_id]} qty: {quantity}")
        print(user.cart[product_id] <= quantity)
        if user.cart[product_id] <= quantity or quantity == 0:
            del user.cart[product_id]
        else:
            user.cart[product_id] -= quantity
        print(f"Item '{self.db.products[product_id].name}' removed from cart. Quantity removed: {quantity}")
        return True
    
    @must_be_user
    def view_cart(self, session_id):
        print(utils.print_header("View User cart"))
        user = self.sessions[session_id]
        if not user.cart:
            print("Cart is empty.")
            return False
        print("Items in cart:")
        total_amount = 0
        for id, quantity in user.cart.items():
            item = self.db.products[id]
            print(f"  {item.id}: {item.name} - ${item.price} x {quantity}")
            total_amount += item.price * quantity
        print(f"\nTotal amount $ {total_amount}")        
        return True
    
    # decorator
    def must_be_admin(func):
        def wrapper(self, session_id, *args, **kwargs):
            if session_id in self.sessions and isinstance(self.sessions[session_id], Admin):
                return func(self, session_id, *args, **kwargs)
            else:
                # print("Admin privileges required." )
                return False,"Admin privileges required." 
        return wrapper
    
    @must_be_admin
    def add_category(self, session_id, category_name, description):
        result = self.db.add_category(category_name, description)
        # print(result)

        return result[1] # message
    
    @must_be_admin
    def add_product(self, session_id, name, description, price, category, **kwargs):
        result = self.db.add_product(name, description, price, category, **kwargs)
        return result[1] # message 
    
    @must_be_admin
    def update_product(self, session_id, product_id, name=None, category=None, price=None):
        if product_id not in self.db.products:
            print("Invalid item Product ID.")
            return False
        product = self.db.products[product_id]
        if name:
            product.name = name
        if category:
            if category not in self.db.categories:
                print("Invalid category.")
                return False
            self.db.categories[product.category]["products"].remove(product)
            product.category = category
            self.db.categories[category]["products"].append(product)
        if price:
            product.price = price
        print(f"Product '{product.name}' updated successfully.")
        return True
    
    @must_be_admin
    def remove_product(self, session_id, product_id):
        if product_id not in self.db.products:
            print("Invalid Product ID.")
            return False
        product = self.db.products.pop(product_id)
        self.db.categories[product.category]["products"].remove(product)
        print(f"Item '{product.name}' removed successfully.")
        return True

app = ECommerceApp()
# app.load_users()
# # print(list(app.db.users.keys()))
print(app.register( "admin@test.com", "adminpass", user_type="admin", name="admin1" ))
print(app.register( email ="user@test.com", password ="userpass", name="Carmencita" ))

# Admin login
admin_session_id = app.login("admin@test.com", "adminpass", user_type='admin')

# User login
user_session_id = app.login("user@test.com", "userpass", user_type='user')

# print(utils.print_divider())
# # # Load catalog
app.load_catalog()

# # Add category as Admin should be valid
print(app.add_category(admin_session_id, "Home Appliances", "Everything you need for your home"))
# print(app.add_category(admin_session_id, "Books", "Healthy brain"))
print(app.add_product(admin_session_id, "Ruby for children", "Teaching Ruby to children", 19.99, "books", author = "Carmen Diaz"))

# print(utils.print_divider())
## Add category as User should be invalid
print(app.add_category(user_session_id, "Home Appliances", "Everything you need for your home"))
print(app.add_product(user_session_id, "Teach your kids to Code", "Teaching code in a fun way", 10.00, "books", author = "Carmen Diaz"))

# It should keep category previously added
print(app.db.categories.keys()) # it should be 4 keys
print(app.add_product(admin_session_id,"Lamp to relax", "Himalayan Pink Lamp", 19.99, 'home_appliances'))

# print(app.db.categories["home_appliances"]) # it should now has products
# print(utils.print_divider())
# print(app.db.catalog)
# print(utils.print_divider())
# # print(utils.print_divider())
print(app.view_categories())

# Admin updates item
app.update_product(admin_session_id, 5, category="clothing", price=55)

app.view_cart(user_session_id)
print(utils.print_header("User adds items to cart"))
# User adds items to cart
app.add_to_cart(user_session_id, 1, 2)
app.add_to_cart(user_session_id, 3, 1)
app.add_to_cart(user_session_id, 4, 3)
app.view_cart(user_session_id)
# Update quantity 
app.remove_from_cart(user_session_id, 4, 1)
# Remove completely from the cart
app.remove_from_cart(user_session_id, 3, 0)
app.view_cart(user_session_id)
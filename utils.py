import json

def print_header(title):
    header = f"{'='* 80 }\n"
    header += f"{title}\n"
    header += f"{'='* 80 }"
    return header

def print_divider():
    return f"{'=' * 80}\n"

def load_users(users = {}):
    print("Loading demo users from JSON file ... \n")
    f = open('data/users.json')
    
    # # returns JSON object as a dictionary
    data = json.loads(f.read())
    
    # Iterating through the json  list
    # Use the enumerate() function to generate the user IDs automatically,
    for idx, user in enumerate(data, start=1):
        users[user['email']] = {**user, **{'id': idx}}
        # self.users[user['email']] = User(idx, user['name'], user['email'], user['password'], user['admin'])
   
    # Closing file
    f.close()
    print(f"Total demo users: {len(users)} \n")
    return users

def load_categories(categories):
    print("Loading DEMO categories from JSON file ... \n")

    f = open('data/categories.json')
    categories_data = json.loads(f.read())

    for cat_idx, (category) in enumerate(categories_data, start=1):
        category_key = "_".join(category['name'].lower().split())
        category_data = { **category, **{'id': cat_idx}}
        categories[category_key] = category_data

    f.close()
    return categories
    
def load_catalog(db):
    catalogs = db.catalogs
    if len(catalogs) == 0:
        print("Loading DEMO catalog from JSON file :p ... \n")
        f = open('data/catalog.json')
            # # returns JSON object as a dictionary
        catalogs = json.loads(f.read())
        f.close()

    # {
    #     "electronics": {
    #         "id": 1,
    #         "name": "Electronics",
    #         "description": "Electronic products",
    #         "products": []
    #     } 

    # }
    # print(f'catalogs.items ==> {catalogs.items()}')

    # To generate category_id. Grab the last category_id if exists, if not start with 1 
    if len(db.categories) > 0:
        last_category_id = int(db.categories[list(db.categories)[-1]]["id"])
    else:
        last_category_id = 0
    
    # current_category_id = int(db.categories[list(db.categories)[-1]]["id"]) + 1 if len(db.categories) > 0 else 
    for (key,category) in catalogs.items():
        ## Categories. Populate db.categories if empty, if not, update data. Remove key products
        category_data = category.copy()
        if category_data["products"]:
            del category_data["products"]

        # print(f'category_data {category_data}')

        if key in db.categories:
            db.categories[key].update(category_data)
            cat_idx = db.categories[key]["id"]
        else:
            category_key = "_".join(key.lower().split())
            cat_idx = last_category_id + 1
            db.categories[category_key] = {**category_data, "id": cat_idx}
            last_category_id = cat_idx  
        # print(category)
        if category["products"]:
            # To create dummy products
            # products = category.pop("products")
            products = category["products"]
            # print(f'category {key}: products {products}')

        if key not in db.catalogs:
            db.catalogs[key] =  {**category, "id": cat_idx}

        ## Product ID is based on the Category ID
        prodId = int(str(cat_idx) + '0')
       
        category_products = []
        for prod_idx, product in enumerate(products, start= prodId + 1):
            # # Generate product ID and build 1 to many relationship Category <-> Products
            product_data = {**product, **{'id': prod_idx, 'category_id': cat_idx, 'category_name': category['name'] }}

            category_products.append(product_data)
            product_id = product_data["id"]
            if product_id in db.products:
                print(product_data)
                db.products[product_id].update({**product_data})
            else:
                db.products[product_id] = {**product_data}

        db.catalogs[key]["products"] = category_products

    # print(f"Total demo categories: {len(db.categories)} - Total demo products: {len(db.products)}\n")
    return({'catalog': db.catalogs, "categories": db.categories, "products": db.products})


def register(name, email, password, users={}, is_admin=0):
    print(f"Register users {users}")
    if email in users:
        return False, f"User {email} already xists."
    users[email] = {"name": name, "password": password, "admin": is_admin}
    return True, "User registered successfully.", users[email]

# login users
def login(email, password, users):
    # print(f"Login users {users}")
    user = users.get(email)
    if not user  or (user and users[email].get("password") != password):
        return False, "Invalid username or password.",{}
    return True, "Login sucessful.", user

from models.database import User
def current_user(email, password, users):
    user_data = login(email, password, users)[2] #for debugging/testing purposes I return a tuple, user data is position 2
    if  user_data:
        return User(**user_data)
    

import pandas as pd
import ipywidgets as widgets
from ipywidgets import HBox
from IPython.display import display

def cart_data(cart, email):
    main_display1 = widgets.Output()
    items = cart[email]
    data =[]
    for product_id, item in items.items():
        # print(f'{product_id} - {item} | type{type(item["price"])}' )
        quantity = item["quantity"]
        subtotal =round(quantity * item["price"], 3)
        data.append([item["name"], quantity, item["price"], subtotal])
        

    data_df = pd.DataFrame(data)

    # Format with commas and round off to two decimal places in pandas
    # pd.options.display.float_format = '{:,.2f}'.format

    data_df.columns = ['Item', 'Qty', 'Price', 'Subtotal']
    # print(data_df['Price'])

    # # Calculate grand total
    grand_total = data_df['Subtotal'].sum()
    # print(grand_total)

    # # Append a row with the grand total to the DataFrame
    data_df['Price'] = data_df['Price'].apply(lambda x: '${:,.2f}'.format(x))
    data_df['Subtotal'] = data_df['Subtotal'].apply(lambda x: '${:,.2f}'.format(x))
    data_df.loc[len(data_df)] = ['Grand Total','','', grand_total]
    data_df.index=[''] * len(data_df)
    

    data_df.style.set_table_styles(
                            [{
    'selector': 'th',
    'props': [
    ('background-color', 'black'),
        ('color', 'white'),
        ('border-color', 'black'),
        ('border-style ', 'solid'),
        ('border-width','1px')]  

    },
    {
    'selector': 'td',
    'props': [
        ('border-color', 'black'),
        ('border-style ', 'solid'),
        ('border-width','1px'),
        ('text-align','left')]
    },
    {'selector': '.row_heading',
        'props': [('display', 'none')]},
    {'selector': '.blank.level0',
        'props': [('display', 'none')]}])

    with main_display1:
        main_display1.clear_output()
        print(f'{email} cart')
        display(data_df)

    
    main_display = HBox([main_display1])
    return {'output': main_display} 


def must_be_admin(func):
    def wrapper(email, db, *args, **kwargs):
        print(db.users.get(email, {}).get("admin"))
        if db.users.get(email, {}).get("admin"):
            return func(email, db, *args, **kwargs)
        else:
            return("Admin permissions required")
    return wrapper


@must_be_admin
def add_category(email, db, category_name, description):
    users = db.users
    categories = db.categories
    category_key = "_".join(category_name.lower().split())
    category_id = len(db.categories) + 1
    if category_key in categories:
        return "Category already exists."
    
    ##  Add data to db.categories and update db.catalogs. Note n  
    category_data = {"id":category_id, "name": category_name, "description": description}
    categories[category_key] = category_data

    if category_key in db.catalogs:
        db.catalogs[category_key].update(category_data)
    else:
        db.catalogs[category_key] = category_data
    return True, "Category added successfully.", db.categories


@must_be_admin
def add_item(email, db,category_name, item_name, price):
    if category_name not in db.categories:
        return "Category does not exist."
    db.categories[category_name][item_name] = price

    db.category[category_name][item_name] = price

    return "Item added successfully."

        #    # Generate product ID and build 1 to many relationship Category <-> Products
        #     product_data = {**product, **{'id': prod_idx, 'category_id': cat_idx, 'category_name': category['name'] }}
        #     # print(product_data)
        #     # db.products.append(product_data)
        #     db.products[str(prod_idx)] = {**product_data}


# def add_to_cart(email, category_name, item_id, db):
#     if category_name not in db.categories or item_id not in db.categories[category_name]:
#         return "Item does not exist."
#     cart.setdefault(email, {}).setdefault(item_id, 0)
#     cart[email][item_id] += 1
#     return "Item added to cart."

# def remove_from_cart(username, item_name):
#     if item_name not in cart.get(username, {}):
#         return "Item not in cart."
#     del cart[username][item_name]
#     return "Item removed from cart."

def checkout(email, cart, categories):
    if email not in cart or not cart[email]:
        return "Cart is empty."
    total_amount = sum(categories[category_name][item_name] * quantity for category_name in categories for item_name, quantity in cart[username].items())
    cart[email] = {}  # Reset cart
    return f"Checkout successful. Total amount: {total_amount}"
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
        dbUsers_emails = self.db.users.keys()
        print(f"Total demo users: {len(dbUsers_emails)} - {list(dbUsers_emails)} \n")
        print(f"Total demo admins: {list(self.db.admins.keys())} \n")
        return True
    
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
# print(app.register( "admin@test.com", "adminpass", user_type="admin", name="admin1" ))
print(app.register( email ="user@test.com", password ="userpass", name="Carmencita" ))

#Admin login
# admin_session_id = app.login("admin@test.com", "adminpass", user_type='admin')
# admin_session_id = app.login("admin@test.com", "adminpass", user_type='admin')

# User login
user_session_id = app.login("user@test.com", "userpass", user_type='user')

# Add category as Admin
# print(app.add_category(admin_session_id, "Home Appliances", "Everything you need for your home"))
# Add category as User
print(app.add_category(user_session_id, "Home Appliances", "Everything you need for your home"))

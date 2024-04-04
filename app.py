import utils
import json
import uuid

from database import DummyEcommerceDB
from database import User, Admin


class ECommerceApp:
    def __init__(self):
        self.sessions = {}
        self.db = DummyEcommerceDB()

    def load_users(self):
        print("Loading demo users from JSON file ... \n")
        f = open('data/users.json')
        # # returns JSON object as a dictionary
        data = json.loads(f.read())

        id_counter = self.db.user_id_counter
        # Iterating through the json  list
        # Use the enumerate() function to generate the user IDs automatically,
        for idx, user_data in enumerate(data, start=id_counter):
            # users[user['email']] = {**user_data, **{'id': idx}}
            user = User(idx, user_data['email'], user_data['password'], user_data['admin'], name = user_data['name'])
            self.db.users[user_data['email']] = user

            if user.is_admin():
                self.db.admins[user.email] = Admin(user.email, user.password)
        self.db.user_id_counter = id_counter
        # Closing file
        f.close()
        print(f"Total demo users: {len(self.db.users)} \n")
        return True

app = ECommerceApp()
app.load_users()
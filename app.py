import utils
import uuid

from models.database import DummyEcommerceDB

class ECommerceApp:
    def __init__(self):
        self.sessions = {}
        self.db = DummyEcommerceDB()

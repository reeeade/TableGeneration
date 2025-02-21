# models.py
from dataclasses import dataclass

@dataclass
class User:
    geo: str
    apple_id: str
    password: str
    number: str
    name: str
    address: str
    birthday: str
    creation: str
    proxy: str

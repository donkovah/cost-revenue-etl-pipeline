from dataclasses import dataclass
from datetime import date

@dataclass
class Shipment:
    guid: str
    origin: str
    destination: str
    cost: int
    revenue: int
    shipping_date: date
    delivery_date: date

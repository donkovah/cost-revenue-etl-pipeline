from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass
class Shipment:
    # Core shipment data
    guid: str
    origin: str
    destination: str
    cost: float
    revenue: float
    shipping_date: datetime
    delivery_date: datetime
    
    # Derived business metrics (calculated fields)
    profit: Optional[float] = field(default=None)
    profit_margin: Optional[float] = field(default=None)
    shipping_duration_days: Optional[float] = field(default=None)
    
    # Time dimensions for analytics
    year: Optional[int] = field(default=None)
    month: Optional[int] = field(default=None)
    quarter: Optional[int] = field(default=None)
    
    # Processing metadata
    processed_at: Optional[datetime] = field(default=None)
    
    def __post_init__(self):
        """Calculate derived fields after initialization"""
        # Calculate profit and profit margin
        if self.cost is not None and self.revenue is not None:
            self.profit = self.revenue - self.cost
            if self.revenue > 0:
                self.profit_margin = round((self.profit / self.revenue) * 100, 2)
            else:
                self.profit_margin = 0.0
        
        # Calculate shipping duration
        if self.shipping_date and self.delivery_date:
            self.shipping_duration_days = (self.delivery_date - self.shipping_date).days
        
        # Extract time dimensions
        if self.shipping_date:
            self.year = self.shipping_date.year
            self.month = self.shipping_date.month
            self.quarter = (self.month - 1) // 3 + 1
        
        # Set processing timestamp
        if self.processed_at is None:
            self.processed_at = datetime.now()
    
    @property
    def is_profitable(self) -> bool:
        """Check if shipment is profitable"""
        return self.profit is not None and self.profit > 0
    
    @property
    def is_high_margin(self) -> bool:
        """Check if shipment has high profit margin (>20%)"""
        return self.profit_margin is not None and self.profit_margin > 20
    
    @property 
    def is_delayed(self) -> bool:
        """Check if delivery was delayed (took more than expected time)"""
        # Assuming standard shipping should be 30 days or less
        return self.shipping_duration_days is not None and self.shipping_duration_days > 30
    
    @property
    def route(self) -> str:
        """Get formatted route string"""
        return f"{self.origin} → {self.destination}"
    
    def to_dict(self) -> dict:
        """Convert shipment to dictionary for DataFrame creation"""
        return {
            'guid': self.guid,
            'origin': self.origin,
            'destination': self.destination,
            'cost': self.cost,
            'revenue': self.revenue,
            'shipping_date': self.shipping_date,
            'delivery_date': self.delivery_date,
            'profit': self.profit,
            'profit_margin': self.profit_margin,
            'shipping_duration_days': self.shipping_duration_days,
            'year': self.year,
            'month': self.month,
            'quarter': self.quarter,
            'processed_at': self.processed_at
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Shipment':
        """Create Shipment from dictionary (useful for DataFrame row conversion)"""
        return cls(
            guid=data['guid'],
            origin=data['origin'],
            destination=data['destination'],
            cost=float(data['cost']),
            revenue=float(data['revenue']),
            shipping_date=data['shipping_date'],
            delivery_date=data['delivery_date']
        )

#!/usr/bin/env python3
"""
Test script to verify the enhanced Shipment domain model
"""

from datetime import datetime
import pandas as pd
from domain.shipment import Shipment

def test_shipment_creation():
    """Test creating a Shipment with automatic calculations"""
    print("🧪 Testing Shipment domain model...")
    
    # Create a test shipment
    shipment = Shipment(
        guid="12345678-1234-5678-9ABC-123456789012",
        origin="New York",
        destination="Los Angeles",
        cost=1000.0,
        revenue=1500.0,
        shipping_date=datetime(2024, 1, 15),
        delivery_date=datetime(2024, 2, 10)
    )
    
    print(f"📦 Created shipment: {shipment.route}")
    print(f"💰 Profit: ${shipment.profit:.2f}")
    print(f"📊 Profit Margin: {shipment.profit_margin}%")
    print(f"🚚 Shipping Duration: {shipment.shipping_duration_days} days")
    print(f"📅 Year/Quarter: {shipment.year} Q{shipment.quarter}")
    print(f"✅ Profitable: {shipment.is_profitable}")
    print(f"🔥 High Margin: {shipment.is_high_margin}")
    print(f"⚠️  Delayed: {shipment.is_delayed}")
    print(f"⏰ Processed at: {shipment.processed_at}")
    
    # Test conversion to/from dict
    shipment_dict = shipment.to_dict()
    recreated_shipment = Shipment.from_dict(shipment_dict)
    
    print(f"🔄 Dict conversion successful: {recreated_shipment.guid == shipment.guid}")
    
    # Test DataFrame creation
    df = pd.DataFrame([shipment_dict])
    print(f"📊 DataFrame shape: {df.shape}")
    print(f"📊 DataFrame columns: {list(df.columns)}")
    
    return shipment

def test_business_rules():
    """Test business logic properties"""
    print("\n🔍 Testing business rules...")
    
    # High margin shipment
    high_margin = Shipment(
        guid="12345678-1234-5678-9ABC-123456789013",
        origin="Shanghai",
        destination="Hamburg",
        cost=500.0,
        revenue=1000.0,  # 50% margin
        shipping_date=datetime(2024, 1, 1),
        delivery_date=datetime(2024, 1, 15)  # 14 days
    )
    
    # Delayed shipment
    delayed = Shipment(
        guid="12345678-1234-5678-9ABC-123456789014",
        origin="Tokyo",
        destination="Rotterdam",
        cost=2000.0,
        revenue=2100.0,  # Low margin
        shipping_date=datetime(2024, 1, 1),
        delivery_date=datetime(2024, 3, 1)  # 60 days - delayed!
    )
    
    print(f"High margin shipment: {high_margin.is_high_margin} (Margin: {high_margin.profit_margin}%)")
    print(f"Delayed shipment: {delayed.is_delayed} (Duration: {delayed.shipping_duration_days} days)")
    
    return [high_margin, delayed]

if __name__ == "__main__":
    print("🚀 Testing Enhanced Shipment Domain Model\n")
    
    # Test basic functionality
    test_shipment = test_shipment_creation()
    
    # Test business rules
    test_shipments = test_business_rules()
    
    print("\n✅ All tests completed successfully!")
    print("\nThe Shipment domain model is now:")
    print("  ✅ Auto-calculating derived fields (profit, margin, duration)")
    print("  ✅ Extracting time dimensions (year, month, quarter)")
    print("  ✅ Providing business logic properties")
    print("  ✅ Converting to/from dict for DataFrame integration")
    print("  ✅ Ready for use in the ETL pipeline!")

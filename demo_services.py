#!/usr/bin/env python3
"""
Demo script showcasing the separated domain services:
- ShipmentETLService: Handles ETL pipeline
- ShipmentAnalyticsService: Provides business intelligence
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import config
from domain.services import ShipmentETLService, ShipmentAnalyticsService
from infra.adapters import (
    S3StorageAdapter, 
    CSVShipmentRepository, 
    PanderaDataValidator,
    ConsoleNotificationAdapter,
    SimpleMetricsAdapter
)
import boto3

def demo_separated_services():
    """Demonstrate the separated domain services"""
    
    print("🚀 Domain Services Separation Demo")
    print("=" * 50)
    
    # Setup infrastructure adapters
    s3_client = boto3.client(
        "s3",
        endpoint_url=config.aws_endpoint_url,
        aws_access_key_id=config.aws_access_key_id,
        aws_secret_access_key=config.aws_secret_access_key,
        region_name=config.aws_default_region
    )
    
    storage_service = S3StorageAdapter(s3_client=s3_client)
    repository = CSVShipmentRepository(storage_service)
    validator = PanderaDataValidator()
    notification_service = ConsoleNotificationAdapter()
    metrics_collector = SimpleMetricsAdapter(enable_file_logging=True)
    
    print("✅ Infrastructure adapters created")
    
    # 1. ETL Service Demo
    print("\n📊 1. ShipmentETLService - ETL Pipeline")
    print("-" * 40)
    
    etl_service = ShipmentETLService(
        repository=repository,
        storage_service=storage_service,
        validator=validator,
        notification_service=notification_service,
        metrics_collector=metrics_collector
    )
    
    try:
        result = etl_service.process_shipments(config.csv_file_path, config.s3_bucket_name)
        
        if result['success']:
            print(f"✅ ETL completed: {result['valid_records']} records processed")
            print(f"⏱️  Duration: {result['processing_time_seconds']:.2f}s")
            
            # Get processed shipments for analytics
            shipments_data = repository.extract_shipments(config.csv_file_path)
            from domain.models.shipment import Shipment
            shipments = [Shipment.from_dict(record) for record in shipments_data[:50]]  # Sample for demo
            
            # 2. Analytics Service Demo
            print("\n📈 2. ShipmentAnalyticsService - Business Intelligence")
            print("-" * 50)
            
            analytics_service = ShipmentAnalyticsService(repository)
            
            # Route Analysis
            print("\n🛣️  Route Profitability Analysis:")
            route_analysis = analytics_service.analyze_profitability_by_route(shipments)
            
            # Show top 3 routes by profit margin
            top_routes = sorted(route_analysis.items(), 
                              key=lambda x: x[1]['avg_profit_margin'], 
                              reverse=True)[:3]
            
            for i, (route, metrics) in enumerate(top_routes, 1):
                print(f"   {i}. {route}")
                print(f"      💰 Avg Margin: {metrics['avg_profit_margin']:.1f}%")
                print(f"      📦 Shipments: {metrics['total_shipments']}")
                print(f"      ⏱️  Avg Duration: {metrics['avg_duration']:.1f} days")
                print()
            
            # Temporal Analysis
            print("📅 Temporal Trends Analysis:")
            temporal_analysis = analytics_service.analyze_temporal_trends(shipments)
            
            monthly_data = temporal_analysis['monthly']
            if monthly_data:
                print(f"   📊 Analyzed {len(monthly_data)} months of data")
                latest_month = max(monthly_data.keys())
                latest_metrics = monthly_data[latest_month]
                print(f"   🆕 Latest month ({latest_month}):")
                print(f"      📦 {latest_metrics['shipments']} shipments")
                print(f"      💰 ${latest_metrics['total_profit']:,.2f} profit")
                print(f"      📈 {latest_metrics.get('profitability_rate', 0):.1f}% profitable")
                print()
            
            # Optimization Opportunities
            print("🎯 Optimization Opportunities:")
            opportunities = analytics_service.identify_optimization_opportunities(shipments)
            
            print(f"   🔴 Cost reduction needed: {len(opportunities['cost_reduction_routes'])} routes")
            print(f"   🟢 Price increase candidates: {len(opportunities['price_increase_candidates'])} routes")
            print(f"   🟡 Process improvement needed: {len(opportunities['process_improvement_needed'])} routes")
            print(f"   🌟 High performers: {len(opportunities['high_performers'])} routes")
            
            # Priority Recommendations
            print("\n⭐ Priority Recommendations:")
            for rec in opportunities['summary']['recommendations_priority']:
                priority_emoji = "🔥" if rec['priority'] == 'HIGH' else "⚡" if rec['priority'] == 'MEDIUM' else "💡"
                print(f"   {priority_emoji} [{rec['priority']}] {rec['action']}: {rec['description']}")
            
            # Comprehensive Business Insights
            print("\n🎯 Comprehensive Business Insights:")
            insights = analytics_service.generate_business_insights(shipments)
            
            health = insights['business_health']
            print(f"   📊 Overall Business Health: {health['overall_score']:.1f}/100")
            print(f"      💰 Profitability: {health['profitability_score']:.1f}%")
            print(f"      ⚡ Efficiency: {health['efficiency_score']:.1f}%") 
            print(f"      🎯 Margin Quality: {health['margin_quality_score']:.1f}%")
            
            print("\n💡 Key Insights:")
            for insight in insights['key_insights']:
                print(f"   • {insight}")
            
        else:
            print("❌ ETL failed!")
            
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        return 1
    
    print("\n" + "=" * 50)
    print("✅ Domain Services Separation Demo Completed!")
    print("\nServices are now properly separated:")
    print("  📁 src/domain/services/etl_service.py - ShipmentETLService")
    print("  📁 src/domain/services/analytics_service.py - ShipmentAnalyticsService")
    print("  📁 src/domain/services/__init__.py - Clean imports")
    
    return 0

if __name__ == "__main__":
    exit_code = demo_separated_services()
    sys.exit(exit_code)

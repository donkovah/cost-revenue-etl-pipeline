from config.config import config
from domain.services import ShipmentETLService
from infra.adapters import (
    S3StorageAdapter, 
    CSVShipmentRepository, 
    PanderaDataValidator,
    ConsoleNotificationAdapter,
    SimpleMetricsAdapter
)
import boto3

def run_pipeline():
    # Create infrastructure adapters
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
    
    # Create domain service
    etl_service = ShipmentETLService(
        repository=repository,
        storage_service=storage_service,
        validator=validator,
        notification_service=notification_service,
        metrics_collector=metrics_collector
    )
    
    # Run the ETL pipeline
    result = etl_service.process_shipments(config.csv_file_path, config.s3_bucket_name)
    
    if result['success']:
        print("✅ ETL pipeline completed successfully!")
        print(f"📊 Processed: {result['records_processed']} records")
        print(f"✅ Valid: {result['valid_records']} records")
        print(f"⚠️  Errors: {len(result['validation_errors'])} validation errors")
        print(f"⏱️  Duration: {result['processing_time_seconds']:.2f} seconds")
        
        # Print business metrics
        metrics = result['business_metrics']
        print(f"\n📈 Business Metrics:")
        print(f"   💰 Profitable shipments: {metrics.get('profitable_shipments', 0)} ({metrics.get('profitability_rate', 0):.1f}%)")
        print(f"   🔥 High margin shipments: {metrics.get('high_margin_shipments', 0)} ({metrics.get('high_margin_rate', 0):.1f}%)")
        print(f"   ⚠️  Delayed shipments: {metrics.get('delayed_shipments', 0)} ({metrics.get('delayed_rate', 0):.1f}%)")
        print(f"   💵 Total profit: ${metrics.get('total_profit', 0):,.2f}")
        print(f"   📊 Avg profit margin: {metrics.get('avg_profit_margin', 0):.2f}%")
    else:
        print("❌ ETL pipeline failed!")
        if 'error' in result:
            print(f"Error: {result['error']}")
        return 1
    
    return 0

if __name__ == "__main__":
    run_pipeline()

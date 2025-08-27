from app.services.etl import extract, transform, load

def run_pipeline():
    csv_path = "path/to/your/downloaded_shipments.csv"
    bucket = "your-bucket-name"

    df = extract(csv_path)
    df_validated = transform(df)
    load(df_validated, bucket)
    print("ETL pipeline completed successfully!")

if __name__ == "__main__":
    run_pipeline()

from app.services.etl import extract, transform, load
from config.config import config

def run_pipeline():
    df = extract(config.csv_file_path)
    df_validated = transform(df)
    load(df_validated, config.s3_bucket_name)
    print("ETL pipeline completed successfully!")

if __name__ == "__main__":
    run_pipeline()

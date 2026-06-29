from app.Back_End.services.ingestion_service import ingest_folder

results = ingest_folder("documents")

print(results)
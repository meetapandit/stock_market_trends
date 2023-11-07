python visualize_prod.py

gcloud builds submit --tag gcr.io/mp-capstone-1/stock-market-app-mp --project=mp-capstone-1

gcloud run deploy --image gcr.io/mp-capstone-1/stock-market-app-mp --platform managed  --project=mp-capstone-1 --allow-unauthenticated
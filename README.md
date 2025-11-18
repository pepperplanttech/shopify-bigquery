# shopify-bigquery

This demo project illustrates an end to end solution for peristing and visualizing Shopify webhook data using the Google Cloud Platform.

The primary components include:
* Terraform configuration for cloud deployment of resources (infrastructure as code)
* Google Cloud Function written in Python (to receive and persist Shopify webook payload)
* Google BigQuery dataset to store webhook data
* Google Looker Studio to visualize the data


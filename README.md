# shopify-bigquery

This demo project illustrates an end to end solution for persisting and visualizing Shopify webhook data using the Google Cloud Platform.

The primary components include:
* Terraform configuration for cloud deployment of resources (IaC / infrastructure as code)
* Google Cloud Function written in Python (to receive and persist Shopify webook payload)
* Google BigQuery dataset to store webhook data
* Google Looker Studio to visualize the data

The workflow is simple:
* Shopify sends data via an HTTP POST to an API endpoint
* API endpoint receives the json webhook payload
* The data is persisted in BigQuery
* The data is retrieved for visualization via a SQL query

The project deployment:
* Terraform configuration files define the Google Cloud resources
* A shell script contains the commands to deploy the project with a single command
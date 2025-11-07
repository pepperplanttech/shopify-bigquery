# Define the Archive Data Source to automatically zip the code
data "archive_file" "source_archive" {
  type        = "zip"
  source_dir  = "../../webhook"  # The directory to zip up
  output_path = "function.zip" # The name and path of the created zip file
}

# Deploy the Cloud Function (Generation 2)
resource "google_cloudfunctions2_function" "webhook_function" {
  name     = "shopify-carts-webhook"
  location = var.dataset_location 
  project  = var.project_id
  
  build_config {
    runtime     = "python311"
    entry_point = "shopify_webhook_handler"
    service_account = "projects/${var.project_id}/serviceAccounts/${google_service_account.build_sa.email}"
    
    source {
      storage_source {
        bucket = google_storage_bucket.function_source.name
        object = google_storage_bucket_object.archive.name # "source.zip"
      }
    }
  }

  service_config {
    environment_variables = var.function_env_vars
    service_account_email = google_service_account.webhook_writer_sa.email
    ingress_settings = "ALLOW_ALL"
    all_traffic_on_latest_revision = true 
    available_memory   = "512Mi"
    timeout_seconds    = 30
    min_instance_count = 0
    max_instance_count = 3
  }
  
  # Explicit dependency to ensure the upload finishes before deployment starts
  # Ensure the IAM binding is in place before the function is built
  depends_on = [
    google_storage_bucket_object.archive,
    google_storage_bucket_iam_member.cloud_build_reader,
    google_service_account.build_sa
  ]
}

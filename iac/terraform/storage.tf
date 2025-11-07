# Define a bucket to hold the zipped function code
resource "google_storage_bucket" "function_source" {
  project       = var.project_id
  name          = "${var.project_id}-shopify-webhooks-source"
  location      = var.dataset_location
  force_destroy = true 
  uniform_bucket_level_access = true
}

resource "google_storage_bucket_object" "archive" {
  name   = "source.zip"
  bucket = google_storage_bucket.function_source.name
  
  # Reference the output file path from the data source
  source = data.archive_file.source_archive.output_path 
}

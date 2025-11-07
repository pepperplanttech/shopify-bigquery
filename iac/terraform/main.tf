# Configure Google Cloud provider
provider "google" {
  project = var.project_id 
  region  = var.dataset_location
  billing_project = var.project_id 
  user_project_override = true
}

# Only needed if using beta features
# provider "google-beta" {
#   project = var.project_id
#   region  = var.dataset_location
#   billing_project = var.project_id
#   user_project_override = true
# }

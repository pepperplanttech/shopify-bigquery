# Enable the Cloud Run API (required for Gen 2 Cloud Functions)
resource "google_project_service" "cloudrun" {
  project = var.project_id
  service = "run.googleapis.com"
  disable_on_destroy = false
}

# Ensure the Cloud Functions API is enabled
resource "google_project_service" "cloudfunctions" {
  project = var.project_id
  service = "cloudfunctions.googleapis.com"
  disable_on_destroy = false
  # Explicitly depend on Cloud Run for robustness
  depends_on = [google_project_service.cloudrun]
}
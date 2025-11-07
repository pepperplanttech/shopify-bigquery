
# Data source to fetch the Project Number (required for the service account email)
data "google_project" "current" {
  project_id = var.project_id
}

# Reference the existing BigQuery dataset ID created in main.tf
locals {
  dataset_id = "shopify_raw_data"
  gcf_source_bucket_name = "gcf-v2-sources-${data.google_project.current.number}-${var.dataset_location}"
}

# --- Cloud Build Stuff
// --- Reference your dedicated build service account defined previously
resource "google_service_account" "build_sa" {
  account_id   = "cf-builder-sa"
  display_name = "Cloud Function Build Service Account"
  project      = data.google_project.current.project_id
}

resource "google_storage_bucket_iam_member" "build_sa_gcf_viewer" {
  bucket = local.gcf_source_bucket_name
  role   = "roles/storage.objectViewer"
  member = "serviceAccount:${google_service_account.build_sa.email}"
}

// --- Grant the Logs Writer role to the new build service account
resource "google_project_iam_member" "build_sa_log_writer" {
  project = data.google_project.current.project_id
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:${google_service_account.build_sa.email}"
}

resource "google_project_iam_member" "build_sa_registry_writer" {
  project = data.google_project.current.project_id
  role    = "roles/artifactregistry.writer"
  member  = "serviceAccount:${google_service_account.build_sa.email}"
}

// --- Grant other necessary roles like Cloud Build Editor
resource "google_project_iam_member" "build_sa_builder" {
  project = data.google_project.current.project_id
  role    = "roles/cloudbuild.builds.editor" // Required for starting builds
  member  = "serviceAccount:${google_service_account.build_sa.email}"
}

# --- Grant the Cloud Build Service Accounts permission to read the source code from the buckets ---
resource "google_storage_bucket_iam_member" "cloud_build_reader" {
  bucket = google_storage_bucket.function_source.name
  role   = "roles/storage.objectViewer"
  member = "serviceAccount:${data.google_project.current.number}@cloudbuild.gserviceaccount.com"
}

# --- Create a Dedicated Service Account for the Cloud Function ---
resource "google_service_account" "webhook_writer_sa" {
  account_id   = "shopify-webhook-writer"
  display_name = "Shopify Webhook to BigQuery Writer"
  project      = data.google_project.current.project_id
}

# --- 2. Grant Permissions to the Service Account ---
# Permission for the Service Account to be callable (invoked) by the Cloud Function service
resource "google_project_iam_member" "cloud_function_invoker" {
  project = data.google_project.current.project_id
  role    = "roles/cloudfunctions.invoker"
  member  = "serviceAccount:${google_service_account.webhook_writer_sa.email}"
}

# Grant the Service Account the ability to write (insert) data into all tables 
# within the specific BigQuery dataset.
resource "google_bigquery_dataset_iam_member" "bigquery_data_editor" {
  dataset_id = local.dataset_id
  project    = data.google_project.current.project_id
  role       = "roles/bigquery.dataEditor"
  member     = "serviceAccount:${google_service_account.webhook_writer_sa.email}"
}

# Grant the Service Account the ability to read and view metadata about the dataset
resource "google_bigquery_dataset_iam_member" "bigquery_data_viewer" {
  dataset_id = local.dataset_id
  project    = data.google_project.current.project_id
  role       = "roles/bigquery.dataViewer"
  member     = "serviceAccount:${google_service_account.webhook_writer_sa.email}"
}

# Make the Cloud Function publicly invokable by anyone (for Shopify webhooks)
// --- ORG POLICY OVERRIDE ---
// This resource exempts the current project from the Domain Restricted Sharing policy,
// allowing 'allUsers' to be added for specific roles like run.invoker.

resource "google_org_policy_policy" "allow_public_run_invoker" {
  // 🎯 FIX: The 'name' argument should ONLY contain the constraint ID
  // when using the 'parent' argument to define the scope (project, folder, or org).
  name = "iam.allowedPolicyMemberDomains"

  // The 'parent' argument defines the scope and must use the full resource path format.
  parent = "projects/${data.google_project.current.project_id}"

  spec {
    // This resets the policy enforcement to Google's default (which typically allows allUsers 
    // unless the organization policy explicitly denies it at a higher level without exception).
    reset = true
  }
}

resource "google_cloud_run_v2_service_iam_member" "public_access_invoker" {
  project = data.google_project.current.project_id
  name     = google_cloudfunctions2_function.webhook_function.name
  location = google_cloudfunctions2_function.webhook_function.location
  role   = "roles/run.invoker" 
  member = "allUsers" 
  depends_on = [google_org_policy_policy.allow_public_run_invoker]
}

# --- Output the Service Account Email for Deployment ---
output "webhook_service_account_email" {
  description = "The email of the Service Account to be used when deploying the Cloud Function."
  value       = google_service_account.webhook_writer_sa.email
}

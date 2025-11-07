# Taint the function (Force the function to be destroyed and recreated)
terraform taint google_cloudfunctions2_function.webhook_function

# Taint the invoker role (Ensures the public access is reapplied to the new service)
terraform taint google_cloud_run_v2_service_iam_member.public_access_invoker

# Taint the source object (Ensures the newest code is uploaded)
terraform taint google_storage_bucket_object.archive

# Apply the changes
terraform apply
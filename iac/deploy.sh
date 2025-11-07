# 1. Taint the function (This forces the function to be destroyed and recreated)
terraform taint google_cloudfunctions2_function.webhook_function

# 2. Taint the invoker role (Ensures the public access is reapplied to the new service)
# Note: Tainting the function often recreates this dependency, but doing it explicitly
# is a safer way to prevent the 403.
terraform taint google_cloud_run_v2_service_iam_member.public_access_invoker

# 3. Taint the source object (Ensures the newest code is uploaded)
terraform taint google_storage_bucket_object.archive

# 4. Apply the changes
terraform apply
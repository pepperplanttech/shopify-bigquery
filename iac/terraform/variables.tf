variable "function_env_vars" {
  description = "Map of environment variables for the Cloud Function"
  type        = map(string)
  default     = {} 
}

variable "project_id" {
  description = "The GCP project ID where resources will be created."
  type        = string
  default     = "" 
}

variable "dataset_location" {
  description = "The geographic location (specific region) for the Cloud Function and related resources."
  type        = string
  default     = "us-central1" 
}

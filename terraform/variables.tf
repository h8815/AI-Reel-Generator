
# AWS region to deploy resources
variable "aws_region" {
  description = "The AWS region to deploy resources in"
  type        = string
  default     = "eu-north-1"
}

# AMI ID for the EC2 instance 
variable "ami_id" {
  description = "The AMI ID for the EC2 instance"
  type        = string
  default     = "ami-0a716d3f3b16d290c" # Example for eu-north-1, replace with your desired AMI ID
}

# Instance type for the EC2 instance
variable "instance_type" {
  description = "The instance type for the EC2 instance"
  type        = string
  default     = "t3.medium"
}

# The name of your SSH key pair
variable "key_pair_name" {
  description = "The name of the SSH key pair to use for the EC2 instance"
  type        = string
  default     = "AI-Reel-Generator" # Replace with your actual key pair name
}

variable "aws_region" {
  description = "AWS deployment region"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Deployment environment (dev, staging, prod)"
  type        = string
  default     = "prod"
}

variable "vpc_cidr" {
  description = "VPC CIDR block"
  type        = string
  default     = "10.0.0.0/16"
}

variable "backend_image" {
  description = "Docker image for FastAPI backend"
  type        = string
  default     = "123456789012.dkr.ecr.us-east-1.amazonaws.com/mcp-hub-backend:latest"
}

variable "frontend_image" {
  description = "Docker image for Next.js frontend"
  type        = string
  default     = "123456789012.dkr.ecr.us-east-1.amazonaws.com/mcp-hub-frontend:latest"
}

variable "db_password" {
  description = "PostgreSQL master password"
  type        = string
  sensitive   = true
}

variable "domain_name" {
  description = "Custom root domain name for ALB HTTPS listener"
  type        = string
  default     = "mcphub.internal"
}

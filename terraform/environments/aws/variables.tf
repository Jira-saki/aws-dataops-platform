variable "aws_region" {
  type        = string
  description = "Target AWS Region"
  default     = "ap-northeast-1"
}

variable "environment" {
  type        = string
  description = "Target deployment environment"
  default     = "prod"
}

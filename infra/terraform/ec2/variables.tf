variable "aws_region" {
  description = "Región de AWS para la demo."
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Prefijo de nombres y etiqueta del entorno."
  type        = string
  default     = "evaluacion-2-demo"
}

variable "vpc_cidr" {
  description = "Rango IPv4 privado de la VPC dedicada."
  type        = string
  default     = "10.42.0.0/16"
}

variable "public_subnet_cidr" {
  description = "Rango IPv4 de la única subred pública."
  type        = string
  default     = "10.42.1.0/24"
}

variable "instance_type" {
  description = "Tipo de instancia EC2; t3.small es el valor inicial para la demo."
  type        = string
  default     = "t3.small"
}

variable "root_volume_size" {
  description = "Tamaño del volumen raíz gp3 cifrado, en GiB."
  type        = number
  default     = 30

  validation {
    condition     = var.root_volume_size >= 30
    error_message = "El volumen raíz debe tener al menos 30 GiB."
  }
}

variable "allowed_http_cidr" {
  description = "CIDR IPv4 autorizado a acceder al sitio. El default publica HTTP en Internet."
  type        = string
  default     = "0.0.0.0/0"

  validation {
    condition     = can(cidrhost(var.allowed_http_cidr, 0))
    error_message = "allowed_http_cidr debe ser un bloque CIDR IPv4 válido."
  }
}

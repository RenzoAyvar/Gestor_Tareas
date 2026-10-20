output "public_ip" {
  description = "Elastic IP del frontend."
  value       = aws_eip.app.public_ip
}

output "url" {
  description = "URL HTTP de la demo."
  value       = "http://${aws_eip.app.public_ip}"
}

output "instance_id" {
  description = "ID de instancia para Session Manager."
  value       = aws_instance.app.id
}

output "aws_region" {
  description = "Región donde se creó el entorno."
  value       = var.aws_region
}

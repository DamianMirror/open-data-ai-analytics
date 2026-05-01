output "public_ip_address" {
  description = "Public IP address of the VM"
  value       = azurerm_public_ip.main.ip_address
}

output "web_url" {
  description = "URL of the web interface"
  value       = "http://${azurerm_public_ip.main.ip_address}:${var.web_port}"
}

output "ssh_command" {
  description = "SSH command to connect to the VM"
  value       = "ssh ${var.admin_username}@${azurerm_public_ip.main.ip_address}"
}

output "resource_group_name" {
  description = "Name of the resource group"
  value       = azurerm_resource_group.main.name
}

output "grafana_url" {
  description = "URL of the Grafana dashboard"
  value       = "http://${azurerm_public_ip.main.ip_address}:3000"
}

output "prometheus_url" {
  description = "URL of the Prometheus UI"
  value       = "http://${azurerm_public_ip.main.ip_address}:9090"
}

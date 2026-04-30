variable "resource_group_name" {
  description = "Name of the Azure Resource Group"
  type        = string
  default     = "ukraine-analytics-rg"
}

variable "location" {
  description = "Azure region"
  type        = string
  default     = "West Europe"
}

variable "vm_name" {
  description = "Name of the Virtual Machine"
  type        = string
  default     = "ukraine-analytics-vm"
}

variable "vm_size" {
  description = "VM size"
  type        = string
  default     = "Standard_D2s_v6"
}

variable "admin_username" {
  description = "Admin username for the VM"
  type        = string
  default     = "azureuser"
}

variable "admin_password" {
  description = "Admin password for the VM"
  type        = string
  sensitive   = true
  default     = "P@ssw0rd1234!"
}

variable "web_port" {
  description = "Port for the web interface"
  type        = number
  default     = 5000
}

variable "github_repo_url" {
  description = "GitHub repository URL to clone"
  type        = string
  default     = "https://github.com/DamianMirror/open-data-ai-analytics.git"
}

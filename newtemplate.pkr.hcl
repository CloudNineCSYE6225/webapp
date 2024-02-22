packer {
  required_plugins {
    googlecompute = {
      source  = "github.com/hashicorp/googlecompute"
      version = "~> 1"
    }
  }
}

variable "machine_type" {
  type    = string
  default = "n1-standard-1"
}

variable "project_id" {
  type    = string
  default = "dev6225webapp"
}

variable "source_image" {
  type    = string
  default = "centos-stream-8-v20240110"
}

variable "ssh_username" {
  type    = string
  default = "packer"
}

variable "zone" {
  type    = string
  default = "us-central1-a"
}

locals { timestamp = regex_replace(timestamp(), "[- TZ:]", "") }

source "googlecompute" "autogenerated_1" {
  credentials_file = "serviceaccount.json"
  disk_size        = 20
  image_name       = "centos-8-image-${local.timestamp}"
  machine_type     = "${var.machine_type}"
  project_id       = "${var.project_id}"
  source_image     = "${var.source_image}"
  ssh_username     = "${var.ssh_username}"
  zone             = "${var.zone}"
}



build {
  sources = ["source.googlecompute.autogenerated_1"]

  provisioner "file" {
    source      = "webapp"
    destination = "~/webapp"
  }

  provisioner "file" {
    source      = "flaskapp.service"
    destination = "~/flaskapp.service"
  }

  provisioner "shell" {
    script = "setup.sh"
  }

}

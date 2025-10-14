resource "aws_instance" "app_server" {
  ami             = var.ami_id
  instance_type   = var.instance_type
  key_name        = var.key_pair_name
  security_groups = [aws_security_group.app_security_group.name]

  # Configure the root volume
  root_block_device {
    volume_size           = 30    # Size in GB (adjust as needed)
    volume_type           = "gp3" # General Purpose SSD
    delete_on_termination = true
  }

  tags = {
    Name = "AI-Reel-App-Server"
  }
}

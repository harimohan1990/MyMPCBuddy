# Security Group for PostgreSQL
resource "aws_security_group" "rds" {
  name        = "mcp-hub-rds-sg"
  description = "Allow inbound traffic to RDS from ECS tasks"
  vpc_id      = aws_vpc.main.id

  ingress {
    description     = "PostgreSQL from Private App subnets"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs_tasks.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "mcp-hub-rds-sg"
  }
}

# Subnet Group
resource "aws_db_subnet_group" "rds" {
  name       = "mcp-hub-rds-subnet-group"
  subnet_ids = aws_subnet.private_data[*].id

  tags = {
    Name = "mcp-hub-rds-subnet-group"
  }
}

# RDS PostgreSQL 16 Instance
resource "aws_db_instance" "postgres" {
  identifier            = "mcp-hub-db-${var.environment}"
  engine                = "postgres"
  engine_version        = "16.1"
  instance_class        = "db.t4g.medium"
  allocated_storage     = 50
  max_allocated_storage = 500
  storage_type          = "gp3"
  storage_encrypted     = true

  db_name  = "mcp_hub"
  username = "mcphub_admin"
  password = var.db_password

  db_subnet_group_name   = aws_db_subnet_group.rds.name
  vpc_security_group_ids = [aws_security_group.rds.id]

  multi_az               = var.environment == "prod" ? true : false
  publicly_accessible    = false
  skip_final_snapshot    = var.environment == "prod" ? false : true
  final_snapshot_identifier = "mcp-hub-db-final-snapshot"

  backup_retention_period = 30
  backup_window           = "03:00-04:00"
  maintenance_window      = "Sun:04:30-Sun:05:30"

  auto_minor_version_upgrade = true
  deletion_protection        = var.environment == "prod" ? true : false

  tags = {
    Name = "mcp-hub-postgres"
  }
}

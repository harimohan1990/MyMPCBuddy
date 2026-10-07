# Security Group for Redis
resource "aws_security_group" "redis" {
  name        = "mcp-hub-redis-sg"
  description = "Allow inbound Redis traffic from ECS tasks"
  vpc_id      = aws_vpc.main.id

  ingress {
    description     = "Redis port 6379"
    from_port       = 6379
    to_port         = 6379
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
    Name = "mcp-hub-redis-sg"
  }
}

# Subnet Group
resource "aws_elasticache_subnet_group" "redis" {
  name       = "mcp-hub-redis-subnet-group"
  subnet_ids = aws_subnet.private_data[*].id
}

# ElastiCache Redis 7 Replication Group
resource "aws_elasticache_replication_group" "redis" {
  replication_group_id       = "mcp-hub-redis-${var.environment}"
  description                = "Personal MCP Hub Redis 7 Cluster"
  engine                     = "redis"
  engine_version             = "7.1"
  node_type                  = "cache.t4g.small"
  num_cache_clusters         = 2
  parameter_group_name       = "default.redis7"
  port                       = 6379
  subnet_group_name          = aws_elasticache_subnet_group.redis.name
  security_group_ids         = [aws_security_group.redis.id]

  automatic_failover_enabled = true
  multi_az_enabled           = true
  at_rest_encryption_enabled = true
  transit_encryption_enabled = false # Enable with auth_token in strict production

  tags = {
    Name = "mcp-hub-redis"
  }
}

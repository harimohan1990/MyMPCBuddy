resource "aws_cloudwatch_log_group" "backend" {
  name              = "/ecs/mcp-hub-backend"
  retention_in_days = 30
}

resource "aws_cloudwatch_log_group" "frontend" {
  name              = "/ecs/mcp-hub-frontend"
  retention_in_days = 30
}

# Metric Alarm: High HTTP 5XX Error Rate
resource "aws_cloudwatch_metric_alarm" "alb_5xx" {
  alarm_name          = "mcp-hub-high-5xx-errors"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "HTTPCode_Target_5XX_Count"
  namespace           = "AWS/ApplicationELB"
  period              = 60
  statistic           = "Sum"
  threshold           = 10
  alarm_description   = "Triggered when 5XX errors exceed 10 in 2 consecutive minutes"

  dimensions = {
    LoadBalancer = aws_lb.main.arn_suffix
  }
}

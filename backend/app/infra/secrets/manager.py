import os
import json
import time
from abc import ABC, abstractmethod
from typing import Optional, Dict
from app.core.logging import logger


class SecretsManagerBase(ABC):
    @abstractmethod
    async def get_secret(self, secret_name: str) -> Optional[str]:
        pass


class EnvSecretsManager(SecretsManagerBase):
    """
    Default Secrets Manager loading from environment variables or .env.
    """
    async def get_secret(self, secret_name: str) -> Optional[str]:
        return os.environ.get(secret_name)


class AWSSecretsManager(SecretsManagerBase):
    """
    Production AWS Secrets Manager with local in-memory caching and TTL.
    """
    def __init__(self, region_name: str = "us-east-1", cache_ttl: int = 3600):
        self.region_name = region_name
        self.cache_ttl = cache_ttl
        self._cache: Dict[str, tuple[str, float]] = {}

    async def get_secret(self, secret_name: str) -> Optional[str]:
        now = time.time()
        if secret_name in self._cache:
            val, exp = self._cache[secret_name]
            if now < exp:
                return val

        try:
            import boto3
            client = boto3.client("secretsmanager", region_name=self.region_name)
            response = client.get_secret_value(SecretId=secret_name)
            secret_val = response.get("SecretString") or response.get("SecretBinary")
            if secret_val:
                self._cache[secret_name] = (secret_val, now + self.cache_ttl)
                return secret_val
        except Exception as e:
            logger.warning(f"AWS Secrets Manager failed for {secret_name}: {e}. Falling back to env.")
            return os.environ.get(secret_name)
        return os.environ.get(secret_name)


def get_secrets_manager() -> SecretsManagerBase:
    use_aws = os.environ.get("USE_AWS_SECRETS_MANAGER", "false").lower() == "true"
    if use_aws:
        return AWSSecretsManager(region_name=os.environ.get("AWS_REGION", "us-east-1"))
    return EnvSecretsManager()

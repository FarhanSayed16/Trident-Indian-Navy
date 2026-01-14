"""
WAF Client Service
Handles communication with external WAF systems (including Mock WAF).
"""

import requests
import logging
from typing import Optional, Dict, Any
from app.config import settings

logger = logging.getLogger(__name__)


class WAFClient:
    """Client for communicating with WAF systems."""
    
    def __init__(self, waf_url: Optional[str] = None, api_key: Optional[str] = None):
        """
        Initialize WAF client.
        
        Args:
            waf_url: WAF service URL (defaults to MOCK_WAF_URL from settings)
            api_key: API key for authentication (defaults to WAF_API_KEY from settings)
        """
        self.waf_url = waf_url or settings.MOCK_WAF_URL
        self.api_key = api_key or settings.WAF_API_KEY
        self.headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        }
    
    def deploy_rule(
        self,
        rule_name: str,
        rule_type: str,
        rule_content: str,
        rule_format: str = "modsecurity",
        rule_config: Optional[Dict[str, Any]] = None,
        description: Optional[str] = None
    ) -> Optional[str]:
        """
        Deploy a rule to the WAF.
        
        Args:
            rule_name: Name of the rule
            rule_type: Type of rule
            rule_content: Rule content
            rule_format: Format of the rule
            rule_config: Rule configuration
            description: Rule description
            
        Returns:
            WAF rule ID if successful, None otherwise
        """
        if not settings.MOCK_WAF_ENABLED:
            logger.info("Mock WAF integration is disabled")
            return None
        
        try:
            payload = {
                "rule_name": rule_name,
                "rule_type": rule_type,
                "rule_content": rule_content,
                "rule_format": rule_format,
                "rule_config": rule_config or {},
                "description": description
            }
            
            response = requests.post(
                f"{self.waf_url}/waf/rules",
                headers=self.headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 201:
                result = response.json()
                waf_rule_id = result.get("waf_rule_id")
                logger.info(f"Rule deployed to WAF: {waf_rule_id}")
                return waf_rule_id
            else:
                logger.error(f"Failed to deploy rule to WAF: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error deploying rule to WAF: {str(e)}")
            return None
    
    def remove_rule(self, waf_rule_id: str) -> bool:
        """
        Remove a rule from the WAF.
        
        Args:
            waf_rule_id: WAF rule ID to remove
            
        Returns:
            True if successful, False otherwise
        """
        if not settings.MOCK_WAF_ENABLED:
            logger.info("Mock WAF integration is disabled")
            return False
        
        try:
            response = requests.delete(
                f"{self.waf_url}/waf/rules/{waf_rule_id}",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"Rule removed from WAF: {waf_rule_id}")
                return True
            else:
                logger.error(f"Failed to remove rule from WAF: {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error removing rule from WAF: {str(e)}")
            return False
    
    def check_health(self) -> bool:
        """
        Check WAF service health.
        
        Returns:
            True if WAF is healthy, False otherwise
        """
        if not settings.MOCK_WAF_ENABLED:
            return False
        
        try:
            response = requests.get(
                f"{self.waf_url}/health",
                timeout=5
            )
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False


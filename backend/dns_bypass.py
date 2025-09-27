"""
DNS Bypass Module for Xionimus AI
Implements multiple strategies to bypass DNS blocks and access AI APIs
"""

import asyncio
import aiohttp
import json
import socket
import logging
from typing import Dict, Optional, Any
import ssl
import certifi

class DNSBypassManager:
    """Manages DNS bypass strategies for accessing AI APIs"""
    
    # Known IP addresses for AI APIs (these may need to be updated periodically)
    API_IPS = {
        'api.anthropic.com': [
            '104.18.10.250',
            '104.18.11.250',
            '172.67.74.226'
        ],
        'api.openai.com': [
            '104.18.7.192',
            '104.18.6.192',
            '172.67.74.192'
        ],
        'api.perplexity.ai': [
            '76.76.19.0',
            '76.76.19.1'
        ]
    }
    
    # Alternative proxy endpoints (public proxies - use with caution)
    PROXY_ENDPOINTS = {
        'anthropic': [
            'https://anthropic-proxy-1.herokuapp.com',
            'https://claude-api-proxy.vercel.app'
        ],
        'openai': [
            'https://openai-proxy-1.herokuapp.com',
            'https://gpt-proxy.vercel.app'
        ]
    }
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.ssl_context = ssl.create_default_context(cafile=certifi.where())
        self.session = None
        
    async def __aenter__(self):
        connector = aiohttp.TCPConnector(
            ssl=self.ssl_context,
            ttl_dns_cache=0  # Disable DNS caching
        )
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=aiohttp.ClientTimeout(total=30)
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def resolve_ip_manually(self, hostname: str) -> Optional[str]:
        """Try to resolve hostname to IP using alternative methods"""
        try:
            # Method 1: Use known IP addresses
            if hostname in self.API_IPS:
                return self.API_IPS[hostname][0]
            
            # Method 2: Try to resolve using socket (may still be blocked)
            try:
                ip = socket.gethostbyname(hostname)
                self.logger.info(f"Resolved {hostname} to {ip}")
                return ip
            except socket.gaierror:
                pass
                
            # Method 3: Return None, DOH requires async context
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to resolve {hostname}: {e}")
            return None
    
    async def _resolve_via_doh(self, hostname: str) -> Optional[str]:
        """Resolve hostname using DNS over HTTPS"""
        try:
            doh_url = f"https://dns.google/resolve?name={hostname}&type=A"
            async with self.session.get(doh_url) as response:
                if response.status == 200:
                    data = await response.json()
                    if 'Answer' in data and len(data['Answer']) > 0:
                        return data['Answer'][0]['data']
        except Exception as e:
            self.logger.error(f"DOH resolution failed for {hostname}: {e}")
        return None
    
    async def test_connection(self, url: str, timeout: int = 5) -> bool:
        """Test if a URL is accessible"""
        try:
            async with self.session.get(url, timeout=aiohttp.ClientTimeout(total=timeout)) as response:
                return response.status < 400
        except:
            return False
    
    async def create_bypassed_anthropic_client(self, api_key: str):
        """Create Anthropic client with DNS bypass"""
        try:
            # Try direct IP connection first
            ip = self.resolve_ip_manually('api.anthropic.com')
            if ip:
                # Create a custom connector that forces IP usage
                import anthropic
                
                # Patch the base URL to use IP
                client = anthropic.AsyncAnthropic(
                    api_key=api_key,
                    base_url=f"https://{ip}",
                    default_headers={"Host": "api.anthropic.com"}
                )
                
                # Test the connection
                try:
                    await client.messages.create(
                        model="claude-opus-4-1-20250805",
                        max_tokens=10,
                        messages=[{"role": "user", "content": "test"}]
                    )
                    self.logger.info("Successfully connected to Anthropic via IP bypass")
                    return client
                except Exception as e:
                    self.logger.warning(f"IP bypass failed for Anthropic: {e}")
            
            # Fallback: Try proxy endpoints
            for proxy_url in self.PROXY_ENDPOINTS.get('anthropic', []):
                if await self.test_connection(proxy_url):
                    try:
                        client = anthropic.AsyncAnthropic(
                            api_key=api_key,
                            base_url=proxy_url
                        )
                        self.logger.info(f"Using Anthropic proxy: {proxy_url}")
                        return client
                    except Exception as e:
                        self.logger.warning(f"Proxy {proxy_url} failed: {e}")
            
        except Exception as e:
            self.logger.error(f"Failed to create bypassed Anthropic client: {e}")
        
        return None
    
    async def create_bypassed_openai_client(self, api_key: str):
        """Create OpenAI client with DNS bypass"""
        try:
            # Try direct IP connection first
            ip = self.resolve_ip_manually('api.openai.com')
            if ip:
                import openai
                
                client = openai.AsyncOpenAI(
                    api_key=api_key,
                    base_url=f"https://{ip}/v1",
                    default_headers={"Host": "api.openai.com"}
                )
                
                # Test the connection
                try:
                    await client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": "test"}],
                        max_tokens=5
                    )
                    self.logger.info("Successfully connected to OpenAI via IP bypass")
                    return client
                except Exception as e:
                    self.logger.warning(f"IP bypass failed for OpenAI: {e}")
            
            # Fallback: Try proxy endpoints  
            for proxy_url in self.PROXY_ENDPOINTS.get('openai', []):
                if await self.test_connection(proxy_url):
                    try:
                        client = openai.AsyncOpenAI(
                            api_key=api_key,
                            base_url=proxy_url
                        )
                        self.logger.info(f"Using OpenAI proxy: {proxy_url}")
                        return client
                    except Exception as e:
                        self.logger.warning(f"Proxy {proxy_url} failed: {e}")
                        
        except Exception as e:
            self.logger.error(f"Failed to create bypassed OpenAI client: {e}")
        
        return None
    
    async def create_bypassed_perplexity_client(self, api_key: str):
        """Create Perplexity client with DNS bypass"""
        try:
            # Try direct IP connection first
            ip = self.resolve_ip_manually('api.perplexity.ai')
            if ip:
                import openai
                
                client = openai.AsyncOpenAI(
                    api_key=api_key,
                    base_url=f"https://{ip}",
                    default_headers={"Host": "api.perplexity.ai"}
                )
                
                # Test the connection
                try:
                    await client.chat.completions.create(
                        model="llama-3.1-sonar-small-128k-online",
                        messages=[{"role": "user", "content": "test"}],
                        max_tokens=5
                    )
                    self.logger.info("Successfully connected to Perplexity via IP bypass")
                    return client
                except Exception as e:
                    self.logger.warning(f"IP bypass failed for Perplexity: {e}")
                    
        except Exception as e:
            self.logger.error(f"Failed to create bypassed Perplexity client: {e}")
        
        return None
    
    async def make_bypassed_request(self, url: str, method: str = 'GET', 
                                   headers: Dict = None, data: Any = None) -> Optional[Dict]:
        """Make a request using DNS bypass techniques"""
        
        # Extract hostname from URL
        from urllib.parse import urlparse
        parsed_url = urlparse(url)
        hostname = parsed_url.netloc
        
        # Try IP-based connection
        ip = self.resolve_ip_manually(hostname)
        if ip:
            bypassed_url = url.replace(hostname, ip)
            bypassed_headers = headers or {}
            bypassed_headers['Host'] = hostname
            
            try:
                async with self.session.request(
                    method, bypassed_url, 
                    headers=bypassed_headers, 
                    json=data if data else None
                ) as response:
                    if response.status < 400:
                        return await response.json()
            except Exception as e:
                self.logger.warning(f"Bypassed request failed: {e}")
        
        return None

# Global bypass manager instance
bypass_manager = None

async def get_bypass_manager():
    """Get or create the global bypass manager"""
    global bypass_manager
    if bypass_manager is None:
        bypass_manager = DNSBypassManager()
        await bypass_manager.__aenter__()
    return bypass_manager

async def cleanup_bypass_manager():
    """Clean up the global bypass manager"""
    global bypass_manager
    if bypass_manager is not None:
        await bypass_manager.__aexit__(None, None, None)
        bypass_manager = None
"""
Vision Expert - AI-Powered Image Selection
Emergent-Style Smart Image Selection and Ranking
"""
import logging
import aiohttp
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class VisionExpert:
    """Expert agent for selecting and ranking images"""
    
    # Unsplash API (free tier) - for demonstration
    UNSPLASH_API_URL = "https://api.unsplash.com/search/photos"
    
    def __init__(self):
        self.access_key = None  # Would be set via env variable
    
    async def search_images(
        self,
        keywords: List[str],
        count: int = 5,
        color: Optional[str] = None,
        orientation: str = "landscape"
    ) -> Dict[str, Any]:
        """
        Search for images based on keywords
        Uses Unsplash API (would require API key in production)
        """
        try:
            # For demo purposes, return curated image URLs
            # In production, this would call Unsplash API
            
            search_query = " ".join(keywords)
            
            # Curated fallback images for different categories
            fallback_images = self._get_fallback_images(keywords[0] if keywords else "general")
            
            logger.info(f"🖼️ Vision Expert: Searching for '{search_query}' (count: {count})")
            
            # Select images based on criteria
            selected_images = self._rank_and_select_images(
                fallback_images,
                keywords=keywords,
                count=count,
                color=color
            )
            
            return {
                'success': True,
                'query': search_query,
                'keywords': keywords,
                'count': len(selected_images),
                'images': selected_images,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Vision expert error: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _get_fallback_images(self, category: str) -> List[Dict[str, str]]:
        """
        Get curated fallback images for different categories
        """
        # Curated high-quality Unsplash URLs (public domain)
        image_sets = {
            "hero": [
                {
                    'url': 'https://images.unsplash.com/photo-1557804506-669a67965ba0',
                    'description': 'Professional team collaboration in modern office',
                    'relevance': 'business, professional, team'
                },
                {
                    'url': 'https://images.unsplash.com/photo-1522071820081-009f0129c71c',
                    'description': 'Team working together at desk',
                    'relevance': 'collaboration, teamwork, office'
                }
            ],
            "technology": [
                {
                    'url': 'https://images.unsplash.com/photo-1518770660439-4636190af475',
                    'description': 'Modern technology and coding',
                    'relevance': 'tech, code, development'
                },
                {
                    'url': 'https://images.unsplash.com/photo-1488590528505-98d2b5aba04b',
                    'description': 'Laptop with code on screen',
                    'relevance': 'programming, developer, tech'
                }
            ],
            "business": [
                {
                    'url': 'https://images.unsplash.com/photo-1454165804606-c3d57bc86b40',
                    'description': 'Business planning and strategy',
                    'relevance': 'business, strategy, planning'
                },
                {
                    'url': 'https://images.unsplash.com/photo-1460925895917-afdab827c52f',
                    'description': 'Business analytics and charts',
                    'relevance': 'analytics, data, business'
                }
            ],
            "general": [
                {
                    'url': 'https://images.unsplash.com/photo-1497366216548-37526070297c',
                    'description': 'Modern minimalist office space',
                    'relevance': 'professional, clean, modern'
                },
                {
                    'url': 'https://images.unsplash.com/photo-1497366754035-f200968a6e72',
                    'description': 'Contemporary workspace design',
                    'relevance': 'workspace, design, professional'
                }
            ]
        }
        
        # Find matching category
        category_lower = category.lower()
        for key in image_sets:
            if key in category_lower or category_lower in key:
                return image_sets[key]
        
        return image_sets['general']
    
    def _rank_and_select_images(
        self,
        images: List[Dict[str, str]],
        keywords: List[str],
        count: int,
        color: Optional[str]
    ) -> List[Dict[str, str]]:
        """
        Rank images based on relevance and select top N
        """
        # Score each image based on keyword matches
        scored_images = []
        
        for img in images:
            score = 0
            relevance_text = img['relevance'].lower()
            description_text = img['description'].lower()
            
            # Score based on keyword matches
            for keyword in keywords:
                keyword_lower = keyword.lower()
                if keyword_lower in relevance_text:
                    score += 10
                if keyword_lower in description_text:
                    score += 5
            
            scored_images.append({
                'url': img['url'],
                'description': img['description'],
                'relevance': img['relevance'],
                'score': score
            })
        
        # Sort by score
        scored_images.sort(key=lambda x: x['score'], reverse=True)
        
        # Select top N
        selected = scored_images[:count]
        
        logger.info(f"✅ Selected {len(selected)} images with scores: {[img['score'] for img in selected]}")
        
        return selected
    
    def analyze_image_needs(
        self,
        problem_statement: str,
        context: str = ""
    ) -> Dict[str, Any]:
        """
        Analyze what kind of images are needed based on problem statement
        """
        # Simple keyword extraction
        keywords = []
        
        # Common patterns
        if any(word in problem_statement.lower() for word in ['hero', 'banner', 'landing']):
            keywords.append('hero')
        
        if any(word in problem_statement.lower() for word in ['tech', 'code', 'software', 'app']):
            keywords.append('technology')
        
        if any(word in problem_statement.lower() for word in ['business', 'corporate', 'professional']):
            keywords.append('business')
        
        if any(word in problem_statement.lower() for word in ['team', 'collaboration', 'people']):
            keywords.append('team')
        
        if not keywords:
            keywords.append('general')
        
        return {
            'problem_statement': problem_statement,
            'suggested_keywords': keywords,
            'recommended_count': 3,
            'recommended_orientation': 'landscape'
        }
    
    def generate_image_report(self, search_result: Dict[str, Any]) -> str:
        """
        Generate human-readable image selection report
        """
        if not search_result['success']:
            return f"❌ Image search failed: {search_result.get('error')}"
        
        lines = ["# 🖼️ Vision Expert - Image Selection Report\n"]
        
        lines.append(f"**Search Query**: {search_result['query']}")
        lines.append(f"**Keywords**: {', '.join(search_result['keywords'])}")
        lines.append(f"**Images Found**: {search_result['count']}\n")
        
        lines.append("## Selected Images")
        
        for i, img in enumerate(search_result['images'], 1):
            lines.append(f"\n### Image {i}")
            lines.append(f"**URL**: {img['url']}")
            lines.append(f"**Description**: {img['description']}")
            lines.append(f"**Relevance**: {img['relevance']}")
            if 'score' in img:
                lines.append(f"**Match Score**: {img['score']}")
        
        return "\n".join(lines)


# Global instance
vision_expert = VisionExpert()

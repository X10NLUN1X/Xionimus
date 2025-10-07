"""
PDF Generator Service
Generates rich PDFs from research history using WeasyPrint
Note: WeasyPrint requires GTK libraries on Windows which are difficult to install
"""
import os
import io
import logging
from typing import List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# Try to import WeasyPrint (optional on Windows)
try:
    from weasyprint import HTML, CSS
    from weasyprint.text.fonts import FontConfiguration
    WEASYPRINT_AVAILABLE = True
    logger.info("✅ WeasyPrint loaded successfully")
except (ImportError, OSError) as e:
    WEASYPRINT_AVAILABLE = False
    logger.warning(f"⚠️ WeasyPrint not available: {e}")
    logger.warning("⚠️ PDF export will not work. Install GTK libraries for Windows:")
    logger.warning("   https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases")


class PDFGenerator:
    """Generate PDFs from research results"""
    
    def __init__(self):
        if WEASYPRINT_AVAILABLE:
            self.font_config = FontConfiguration()
        else:
            self.font_config = None
            logger.warning("⚠️ PDF Generator initialized without WeasyPrint")
        
    def generate_research_pdf(
        self,
        query: str,
        content: str,
        citations: List[str],
        sources_count: int,
        related_questions: Optional[List[str]] = None,
        model_used: Optional[str] = None,
        duration_seconds: Optional[float] = None,
        timestamp: Optional[datetime] = None
    ) -> bytes:
        """
        Generate a single research result as PDF
        
        Args:
            query: Research query
            content: Research findings
            citations: List of source URLs
            sources_count: Number of sources
            related_questions: Related questions
            model_used: Model identifier
            duration_seconds: Time taken
            timestamp: When research was done
            
        Returns:
            PDF bytes
            
        Raises:
            RuntimeError: If WeasyPrint is not available
        """
        if not WEASYPRINT_AVAILABLE:
            raise RuntimeError(
                "PDF generation not available. WeasyPrint requires GTK libraries. "
                "Install from: https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases"
            )
        
        html_content = self._create_single_research_html(
            query=query,
            content=content,
            citations=citations,
            sources_count=sources_count,
            related_questions=related_questions,
            model_used=model_used,
            duration_seconds=duration_seconds,
            timestamp=timestamp
        )
        
        return self._html_to_pdf(html_content)
    
    def generate_bulk_research_pdf(
        self,
        research_items: List[dict],
        title: str = "Research Export",
        include_sources: bool = True,
        include_metadata: bool = True
    ) -> bytes:
        """
        Generate PDF from multiple research items
        
        Args:
            research_items: List of research history items
            title: Document title
            include_sources: Include source lists
            include_metadata: Include timestamps and metadata
            
        Returns:
            PDF bytes
            
        Raises:
            RuntimeError: If WeasyPrint is not available
        """
        if not WEASYPRINT_AVAILABLE:
            raise RuntimeError(
                "PDF generation not available. WeasyPrint requires GTK libraries. "
                "Install from: https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases"
            )
        
        html_content = self._create_bulk_research_html(
            research_items=research_items,
            title=title,
            include_sources=include_sources,
            include_metadata=include_metadata
        )
        
        return self._html_to_pdf(html_content)
    
    def _create_single_research_html(
        self,
        query: str,
        content: str,
        citations: List[str],
        sources_count: int,
        related_questions: Optional[List[str]] = None,
        model_used: Optional[str] = None,
        duration_seconds: Optional[float] = None,
        timestamp: Optional[datetime] = None
    ) -> str:
        """Create HTML for single research result"""
        
        # Format timestamp
        timestamp_str = timestamp.strftime("%B %d, %Y at %I:%M %p") if timestamp else datetime.now().strftime("%B %d, %Y at %I:%M %p")
        
        # Build HTML
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Research Results</title>
            <style>
                @page {{
                    size: A4;
                    margin: 2cm;
                }}
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                    line-height: 1.6;
                    color: #1a1a1a;
                }}
                .header {{
                    background: linear-gradient(135deg, #d4af37 0%, #f0d97c 100%);
                    color: white;
                    padding: 30px;
                    margin-bottom: 30px;
                    border-radius: 8px;
                }}
                .header h1 {{
                    margin: 0 0 10px 0;
                    font-size: 28px;
                    font-weight: 700;
                }}
                .metadata {{
                    font-size: 12px;
                    opacity: 0.9;
                    margin-top: 10px;
                }}
                .section {{
                    margin-bottom: 30px;
                }}
                .section-title {{
                    font-size: 20px;
                    font-weight: 600;
                    color: #d4af37;
                    margin-bottom: 15px;
                    padding-bottom: 8px;
                    border-bottom: 2px solid #d4af37;
                }}
                .query-box {{
                    background: #f9f9f9;
                    padding: 20px;
                    border-left: 4px solid #d4af37;
                    margin-bottom: 25px;
                    border-radius: 4px;
                }}
                .content {{
                    font-size: 14px;
                    line-height: 1.8;
                    white-space: pre-wrap;
                    color: #2d2d2d;
                }}
                .sources {{
                    background: #f5f5f5;
                    padding: 20px;
                    border-radius: 8px;
                }}
                .source-item {{
                    margin-bottom: 12px;
                    padding: 10px;
                    background: white;
                    border-left: 3px solid #d4af37;
                    font-size: 12px;
                }}
                .source-number {{
                    color: #d4af37;
                    font-weight: 600;
                    margin-right: 8px;
                }}
                .source-url {{
                    color: #4a5568;
                    word-break: break-all;
                }}
                .related-question {{
                    padding: 10px 15px;
                    background: #f0f9ff;
                    border-left: 3px solid #3b82f6;
                    margin-bottom: 10px;
                    font-size: 13px;
                }}
                .footer {{
                    margin-top: 40px;
                    padding-top: 20px;
                    border-top: 1px solid #e0e0e0;
                    text-align: center;
                    font-size: 11px;
                    color: #666;
                }}
                .badge {{
                    display: inline-block;
                    padding: 4px 10px;
                    background: #e8f4f8;
                    color: #0369a1;
                    border-radius: 12px;
                    font-size: 11px;
                    font-weight: 500;
                    margin-right: 8px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🔍 Xionimus AI Research</h1>
                <div class="metadata">
                    <div><strong>Generated:</strong> {timestamp_str}</div>
        """
        
        if model_used:
            html += f'<div><strong>Model:</strong> {model_used}</div>'
        if duration_seconds:
            html += f'<div><strong>Duration:</strong> {duration_seconds:.2f} seconds</div>'
        
        html += """
                </div>
            </div>
            
            <div class="query-box">
                <div style="font-size: 12px; text-transform: uppercase; color: #666; margin-bottom: 8px; font-weight: 600;">Research Query</div>
        """
        html += f'<div style="font-size: 16px; font-weight: 500; color: #1a1a1a;">{query}</div>'
        html += """
            </div>
            
            <div class="section">
                <div class="section-title">📄 Findings</div>
                <div class="content">
        """
        html += content
        html += """
                </div>
            </div>
        """
        
        # Sources section
        if citations and len(citations) > 0:
            html += f"""
            <div class="section">
                <div class="section-title">📚 Sources ({sources_count})</div>
                <div class="sources">
            """
            for idx, citation in enumerate(citations, 1):
                html += f"""
                    <div class="source-item">
                        <span class="source-number">[{idx}]</span>
                        <span class="source-url">{citation}</span>
                    </div>
                """
            html += """
                </div>
            </div>
            """
        
        # Related questions
        if related_questions and len(related_questions) > 0:
            html += """
            <div class="section">
                <div class="section-title">💡 Related Questions</div>
            """
            for question in related_questions:
                html += f'<div class="related-question">{question}</div>'
            html += """
            </div>
            """
        
        html += """
            <div class="footer">
                Generated by Xionimus AI Research Agent<br>
                https://xionimus.ai
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _create_bulk_research_html(
        self,
        research_items: List[dict],
        title: str,
        include_sources: bool,
        include_metadata: bool
    ) -> str:
        """Create HTML for bulk research export"""
        
        timestamp_str = datetime.now().strftime("%B %d, %Y at %I:%M %p")
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>{title}</title>
            <style>
                @page {{
                    size: A4;
                    margin: 2cm;
                }}
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                    line-height: 1.6;
                    color: #1a1a1a;
                }}
                .cover {{
                    background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
                    color: white;
                    padding: 60px 40px;
                    margin-bottom: 40px;
                    border-radius: 8px;
                    text-align: center;
                }}
                .cover h1 {{
                    margin: 0 0 20px 0;
                    font-size: 36px;
                    font-weight: 700;
                    color: #d4af37;
                }}
                .cover .subtitle {{
                    font-size: 16px;
                    opacity: 0.8;
                }}
                .research-item {{
                    page-break-inside: avoid;
                    margin-bottom: 40px;
                    padding-bottom: 30px;
                    border-bottom: 2px solid #e0e0e0;
                }}
                .research-item:last-child {{
                    border-bottom: none;
                }}
                .query {{
                    background: #f9f9f9;
                    padding: 15px 20px;
                    border-left: 4px solid #d4af37;
                    margin-bottom: 20px;
                    border-radius: 4px;
                }}
                .query-text {{
                    font-size: 18px;
                    font-weight: 600;
                    color: #1a1a1a;
                }}
                .metadata {{
                    font-size: 11px;
                    color: #666;
                    margin-top: 8px;
                }}
                .content {{
                    font-size: 13px;
                    line-height: 1.8;
                    white-space: pre-wrap;
                    margin: 20px 0;
                    color: #2d2d2d;
                }}
                .sources {{
                    background: #f5f5f5;
                    padding: 15px;
                    border-radius: 6px;
                    margin-top: 20px;
                }}
                .sources-title {{
                    font-size: 14px;
                    font-weight: 600;
                    color: #d4af37;
                    margin-bottom: 10px;
                }}
                .source-item {{
                    margin-bottom: 8px;
                    padding: 8px;
                    background: white;
                    border-left: 2px solid #d4af37;
                    font-size: 11px;
                }}
                .footer {{
                    margin-top: 60px;
                    padding-top: 20px;
                    border-top: 1px solid #e0e0e0;
                    text-align: center;
                    font-size: 11px;
                    color: #666;
                }}
            </style>
        </head>
        <body>
            <div class="cover">
                <h1>📚 {title}</h1>
                <div class="subtitle">Generated on {timestamp_str}</div>
                <div class="subtitle">Total Research Items: {len(research_items)}</div>
            </div>
        """
        
        for idx, item in enumerate(research_items, 1):
            html += f"""
            <div class="research-item">
                <div style="color: #d4af37; font-size: 12px; font-weight: 600; margin-bottom: 10px;">RESEARCH #{idx}</div>
                <div class="query">
                    <div class="query-text">{item.get('query', 'No query')}</div>
            """
            
            if include_metadata:
                timestamp = item.get('timestamp')
                if timestamp:
                    if isinstance(timestamp, str):
                        timestamp_str = timestamp
                    else:
                        timestamp_str = timestamp.strftime("%B %d, %Y") if hasattr(timestamp, 'strftime') else str(timestamp)
                    html += f'<div class="metadata">📅 {timestamp_str}'
                    
                    if item.get('duration_seconds'):
                        html += f' • ⏱️ {item["duration_seconds"]:.2f}s'
                    if item.get('result', {}).get('sources_count'):
                        html += f' • 📚 {item["result"]["sources_count"]} sources'
                    html += '</div>'
            
            html += """
                </div>
                <div class="content">
            """
            html += item.get('result', {}).get('content', 'No content available')
            html += """
                </div>
            """
            
            if include_sources:
                citations = item.get('result', {}).get('citations', [])
                if citations:
                    sources_count = item.get('result', {}).get('sources_count', len(citations))
                    html += f"""
                    <div class="sources">
                        <div class="sources-title">Sources ({sources_count})</div>
                    """
                    for source_idx, citation in enumerate(citations, 1):
                        html += f"""
                        <div class="source-item">
                            <span style="color: #d4af37; font-weight: 600;">[{source_idx}]</span> {citation}
                        </div>
                        """
                    html += """
                    </div>
                    """
            
            html += """
            </div>
            """
        
        html += f"""
            <div class="footer">
                Generated by Xionimus AI Research Agent<br>
                {len(research_items)} research items exported<br>
                https://xionimus.ai
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _html_to_pdf(self, html_content: str) -> bytes:
        """Convert HTML to PDF using WeasyPrint"""
        html = HTML(string=html_content)
        pdf_bytes = html.write_pdf(font_config=self.font_config)
        return pdf_bytes
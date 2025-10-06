"""
Sandbox Templates API
Provides code templates for all supported languages
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional
import logging

from ..core.code_templates import (
    get_template,
    get_all_templates,
    get_available_languages,
    get_available_template_types
)

logger = logging.getLogger(__name__)
router = APIRouter()


class TemplateResponse(BaseModel):
    language: str
    template_type: str
    code: str


class AllTemplatesResponse(BaseModel):
    language: str
    templates: Dict[str, str]


class LanguagesResponse(BaseModel):
    languages: List[str]


class TemplateTypesResponse(BaseModel):
    template_types: List[str]


@router.get("/template/{language}/{template_type}", response_model=TemplateResponse)
async def get_code_template(language: str, template_type: str = "hello_world"):
    """
    Get code template for specified language and type
    
    Available languages: python, javascript, typescript, java, cpp, c, csharp, go, php, ruby, perl, bash
    Available template types: hello_world, fibonacci, data_structures
    """
    try:
        code = get_template(language, template_type)
        
        if not code:
            raise HTTPException(
                status_code=404,
                detail=f"Template not found for language '{language}' and type '{template_type}'"
            )
        
        return TemplateResponse(
            language=language,
            template_type=template_type,
            code=code
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting template: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/templates/{language}", response_model=AllTemplatesResponse)
async def get_language_templates(language: str):
    """
    Get all available templates for a specific language
    """
    try:
        templates = get_all_templates(language)
        
        if not templates:
            raise HTTPException(
                status_code=404,
                detail=f"No templates found for language '{language}'"
            )
        
        return AllTemplatesResponse(
            language=language,
            templates=templates
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting templates: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/languages", response_model=LanguagesResponse)
async def get_template_languages():
    """
    Get list of all languages with available templates
    """
    return LanguagesResponse(languages=get_available_languages())


@router.get("/types", response_model=TemplateTypesResponse)
async def get_template_types():
    """
    Get list of all available template types
    """
    return TemplateTypesResponse(template_types=get_available_template_types())
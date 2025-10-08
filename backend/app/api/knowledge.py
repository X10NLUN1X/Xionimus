"""
Knowledge Graph API - Context Management
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, List
import logging

from ..core.knowledge_graph import knowledge_graph

logger = logging.getLogger(__name__)
router = APIRouter()

class Entity(BaseModel):
    name: str
    entityType: str
    observations: List[str]

class Relation(BaseModel):
    from_entity: str = Field(..., alias='from')
    to: str
    relationType: str
    
    class Config:
        populate_by_name = True

class CreateEntitiesRequest(BaseModel):
    entities: List[Entity]

class CreateRelationsRequest(BaseModel):
    relations: List[Relation]

class AddObservationsRequest(BaseModel):
    observations: List[Dict[str, Any]]

@router.post("/entities")
async def create_entities(request: CreateEntitiesRequest) -> Dict[str, Any]:
    """
    Create multiple entities
    """
    try:
        entities_data = [e.dict() for e in request.entities]
        result = knowledge_graph.create_entities(entities_data)
        return result
    except Exception as e:
        logger.error(f"Create entities error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/relations")
async def create_relations(request: CreateRelationsRequest) -> Dict[str, Any]:
    """
    Create multiple relations
    """
    try:
        relations_data = [
            {
                'from': r.from_entity,
                'to': r.to,
                'relationType': r.relationType
            }
            for r in request.relations
        ]
        result = knowledge_graph.create_relations(relations_data)
        return result
    except Exception as e:
        logger.error(f"Create relations error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/observations")
async def add_observations(request: AddObservationsRequest) -> Dict[str, Any]:
    """
    Add observations to entities
    """
    try:
        results = []
        for obs_data in request.observations:
            result = knowledge_graph.add_observations(
                entity_name=obs_data['entityName'],
                observations=obs_data['contents']
            )
            results.append(result)
        
        return {
            'success': all(r.get('success') for r in results),
            'results': results
        }
    except Exception as e:
        logger.error(f"Add observations error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/graph")
async def read_graph():
    """
    Read entire knowledge graph
    """
    try:
        return knowledge_graph.read_graph()
    except Exception as e:
        logger.error(f"Read graph error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search")
async def search_nodes(query: str):
    """
    Search for nodes in knowledge graph
    """
    try:
        results = knowledge_graph.search_entities(query)
        return {
            'query': query,
            'results': results,
            'count': len(results)
        }
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/entities/{name}")
async def get_entity(name: str):
    """
    Get entity by name
    """
    entity = knowledge_graph.get_entity(name)
    if not entity:
        raise HTTPException(status_code=404, detail=f"Entity not found: {name}")
    
    relations = knowledge_graph.get_entity_relations(name)
    
    return {
        'entity': entity,
        'relations': relations
    }

@router.delete("/entities/{name}")
async def delete_entity(name: str):
    """
    Delete entity
    """
    try:
        result = knowledge_graph.delete_entity(name)
        if not result['success']:
            raise HTTPException(status_code=404, detail=result['error'])
        return result
    except Exception as e:
        logger.error(f"Delete entity error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_statistics():
    """
    Get knowledge graph statistics
    """
    try:
        stats = knowledge_graph.get_statistics()
        report = knowledge_graph.generate_graph_report()
        
        return {
            'statistics': stats,
            'report': report
        }
    except Exception as e:
        logger.error(f"Statistics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

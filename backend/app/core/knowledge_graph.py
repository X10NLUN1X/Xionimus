"""
Knowledge Graph - Context Management System
Emergent-Style Entity and Relation Tracking
"""
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from collections import defaultdict

logger = logging.getLogger(__name__)

class KnowledgeGraph:
    """Manages entities, relations, and observations for context"""
    
    def __init__(self):
        self.entities: Dict[str, Dict[str, Any]] = {}
        self.relations: List[Dict[str, str]] = []
        self.entity_types = defaultdict(list)
    
    def create_entity(
        self, 
        name: str, 
        entity_type: str,
        observations: List[str]
    ) -> Dict[str, Any]:
        """
        Create a new entity with observations
        """
        if name in self.entities:
            logger.warning(f"Entity '{name}' already exists, updating observations")
            self.entities[name]['observations'].extend(observations)
            self.entities[name]['updated_at'] = datetime.now().isoformat()
        else:
            self.entities[name] = {
                'name': name,
                'type': entity_type,
                'observations': observations,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            self.entity_types[entity_type].append(name)
            logger.info(f"✅ Created entity: {name} ({entity_type})")
        
        return self.entities[name]
    
    def create_entities(self, entities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create multiple entities at once
        """
        results = []
        for entity_data in entities:
            result = self.create_entity(
                name=entity_data['name'],
                entity_type=entity_data['entityType'],
                observations=entity_data['observations']
            )
            results.append(result)
        
        return {
            'success': True,
            'count': len(results),
            'entities': results,
            'timestamp': datetime.now().isoformat()
        }
    
    def add_observations(self, entity_name: str, observations: List[str]) -> Dict[str, Any]:
        """
        Add observations to existing entity
        """
        if entity_name not in self.entities:
            return {
                'success': False,
                'error': f'Entity not found: {entity_name}'
            }
        
        self.entities[entity_name]['observations'].extend(observations)
        self.entities[entity_name]['updated_at'] = datetime.now().isoformat()
        
        logger.info(f"✅ Added {len(observations)} observations to: {entity_name}")
        
        return {
            'success': True,
            'entity': entity_name,
            'observations_added': len(observations),
            'total_observations': len(self.entities[entity_name]['observations'])
        }
    
    def create_relation(
        self, 
        from_entity: str,
        to_entity: str,
        relation_type: str
    ) -> Dict[str, Any]:
        """
        Create relation between entities (active voice)
        """
        if from_entity not in self.entities:
            return {
                'success': False,
                'error': f'Source entity not found: {from_entity}'
            }
        
        if to_entity not in self.entities:
            return {
                'success': False,
                'error': f'Target entity not found: {to_entity}'
            }
        
        relation = {
            'from': from_entity,
            'to': to_entity,
            'type': relation_type,
            'created_at': datetime.now().isoformat()
        }
        
        self.relations.append(relation)
        logger.info(f"✅ Created relation: {from_entity} --[{relation_type}]--> {to_entity}")
        
        return {
            'success': True,
            'relation': relation
        }
    
    def create_relations(self, relations: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Create multiple relations at once
        """
        results = []
        errors = []
        
        for rel_data in relations:
            result = self.create_relation(
                from_entity=rel_data['from'],
                to_entity=rel_data['to'],
                relation_type=rel_data['relationType']
            )
            
            if result['success']:
                results.append(result['relation'])
            else:
                errors.append(result)
        
        return {
            'success': len(errors) == 0,
            'count': len(results),
            'relations': results,
            'errors': errors,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_entity(self, name: str) -> Optional[Dict[str, Any]]:
        """Get entity by name"""
        return self.entities.get(name)
    
    def search_entities(self, query: str) -> List[Dict[str, Any]]:
        """
        Search entities by name, type, or observation content
        """
        query_lower = query.lower()
        results = []
        
        for entity in self.entities.values():
            # Match name
            if query_lower in entity['name'].lower():
                results.append(entity)
                continue
            
            # Match type
            if query_lower in entity['type'].lower():
                results.append(entity)
                continue
            
            # Match observations
            for obs in entity['observations']:
                if query_lower in obs.lower():
                    results.append(entity)
                    break
        
        logger.info(f"🔍 Search found {len(results)} entities for query: {query}")
        return results
    
    def get_entity_relations(self, entity_name: str) -> Dict[str, List[Dict[str, str]]]:
        """
        Get all relations for an entity (incoming and outgoing)
        """
        outgoing = [r for r in self.relations if r['from'] == entity_name]
        incoming = [r for r in self.relations if r['to'] == entity_name]
        
        return {
            'entity': entity_name,
            'outgoing': outgoing,
            'incoming': incoming,
            'total': len(outgoing) + len(incoming)
        }
    
    def delete_entity(self, name: str) -> Dict[str, Any]:
        """
        Delete entity and all its relations
        """
        if name not in self.entities:
            return {
                'success': False,
                'error': f'Entity not found: {name}'
            }
        
        # Remove entity
        entity = self.entities.pop(name)
        
        # Remove from type index
        self.entity_types[entity['type']].remove(name)
        
        # Remove all relations
        self.relations = [
            r for r in self.relations 
            if r['from'] != name and r['to'] != name
        ]
        
        logger.info(f"✅ Deleted entity: {name}")
        
        return {
            'success': True,
            'entity': name,
            'type': entity['type']
        }
    
    def read_graph(self) -> Dict[str, Any]:
        """
        Read entire knowledge graph
        """
        return {
            'entities': list(self.entities.values()),
            'relations': self.relations,
            'entity_count': len(self.entities),
            'relation_count': len(self.relations),
            'entity_types': dict(self.entity_types),
            'timestamp': datetime.now().isoformat()
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get graph statistics
        """
        return {
            'total_entities': len(self.entities),
            'total_relations': len(self.relations),
            'entity_types': {
                entity_type: len(entities)
                for entity_type, entities in self.entity_types.items()
            },
            'avg_observations_per_entity': (
                sum(len(e['observations']) for e in self.entities.values()) / len(self.entities)
                if self.entities else 0
            )
        }
    
    def generate_graph_report(self) -> str:
        """
        Generate human-readable graph report
        """
        stats = self.get_statistics()
        
        lines = ["# 🧠 Knowledge Graph Report\n"]
        
        lines.append(f"**Total Entities**: {stats['total_entities']}")
        lines.append(f"**Total Relations**: {stats['total_relations']}")
        lines.append(f"**Avg Observations**: {stats['avg_observations_per_entity']:.1f}\n")
        
        lines.append("## Entity Types")
        for entity_type, count in stats['entity_types'].items():
            lines.append(f"- **{entity_type}**: {count} entities")
        
        if self.entities:
            lines.append("\n## Recent Entities")
            recent = sorted(
                self.entities.values(),
                key=lambda x: x['created_at'],
                reverse=True
            )[:5]
            
            for entity in recent:
                lines.append(f"- **{entity['name']}** ({entity['type']})")
                lines.append(f"  - {len(entity['observations'])} observations")
        
        return "\n".join(lines)


# Global instance
knowledge_graph = KnowledgeGraph()

#!/usr/bin/env python3
"""
XIONIMUS AI - Demo-Programm
===========================

Ein Beispielprogramm, das die Zusammenarbeit aller Agenten und 
des Chatbots demonstriert. Dieses Programm zeigt die Fähigkeiten
von Xionimus AI in einem realistischen Szenario.

Funktionen:
- Multi-Agent Koordination
- Chatbot-Integration
- Projektmanagement
- Code-Generierung
- Dokumentation
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime
from typing import Dict, Any, List
from pathlib import Path

BACKEND_URL = "http://localhost:8001"
API_BASE = f"{BACKEND_URL}/api"

class XionimusDemoProgram:
    def __init__(self):
        self.session = None
        self.project_data = {}
        self.agent_interactions = []
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def log_interaction(self, agent: str, task: str, result: str, success: bool = True):
        """Protokolliere Agenten-Interaktionen"""
        interaction = {
            'timestamp': datetime.now().strftime("%H:%M:%S"),
            'agent': agent,
            'task': task,
            'result': result[:200] + "..." if len(result) > 200 else result,
            'success': success
        }
        self.agent_interactions.append(interaction)
        
        status = "✅" if success else "❌"
        print(f"{status} [{interaction['timestamp']}] {agent}: {task}")
        print(f"    📝 Ergebnis: {interaction['result']}")
        print()

    async def chat_with_agent(self, message: str, agent_preference: str = None, description: str = ""):
        """Chatte mit einem spezifischen Agenten"""
        try:
            chat_request = {
                "message": message,
                "use_agent": True,
                "language": "de"
            }
            
            if agent_preference:
                chat_request["agent_preference"] = agent_preference
            
            async with self.session.post(f"{API_BASE}/chat", json=chat_request) as response:
                if response.status == 200:
                    data = await response.json()
                    content = data.get('message', {}).get('content', '')
                    agent_used = data.get('metadata', {}).get('agent_used', 'Unknown Agent')
                    
                    self.log_interaction(agent_used, description or message[:50] + "...", content, True)
                    return {
                        'success': True,
                        'content': content,
                        'agent': agent_used,
                        'metadata': data.get('metadata', {})
                    }
                else:
                    error_msg = f"HTTP {response.status}"
                    try:
                        error_data = await response.json()
                        error_msg = error_data.get('detail', error_msg)
                    except:
                        pass
                    
                    self.log_interaction(agent_preference or "System", description or message[:50] + "...", 
                                       f"Fehler: {error_msg}", False)
                    return {
                        'success': False,
                        'error': error_msg,
                        'content': '',
                        'agent': 'None'
                    }
                    
        except Exception as e:
            self.log_interaction(agent_preference or "System", description or message[:50] + "...", 
                               f"Ausnahme: {str(e)}", False)
            return {
                'success': False,
                'error': str(e),
                'content': '',
                'agent': 'None'
            }

    async def demo_scenario_todo_app(self):
        """Demo-Szenario: Erstelle eine Todo-App mit allen Agenten"""
        print("🎬 DEMO-SZENARIO: TODO-APP ENTWICKLUNG")
        print("=" * 60)
        print("Demonstriert die Zusammenarbeit aller 8 Agenten bei der App-Entwicklung")
        print()
        
        # Schritt 1: Research Agent - Beste Praktiken recherchieren
        research_result = await self.chat_with_agent(
            "Recherchiere die besten Praktiken für Todo-App Entwicklung im Jahr 2024. Was sind die wichtigsten Features und Technologien?",
            "research",
            "Best Practices für Todo-Apps recherchieren"
        )
        
        await asyncio.sleep(1)
        
        # Schritt 2: Data Agent - Datenmodell entwerfen
        data_result = await self.chat_with_agent(
            "Entwerfe ein Datenmodell für eine Todo-Anwendung. Welche Entitäten und Beziehungen werden benötigt?",
            "data",
            "Datenmodell für Todo-App entwerfen"
        )
        
        await asyncio.sleep(1)
        
        # Schritt 3: Code Agent - Backend-Code generieren
        code_result = await self.chat_with_agent(
            "Erstelle Python Flask Code für eine Todo-App API mit CRUD-Operationen",
            "code", 
            "Flask Backend für Todo-App erstellen"
        )
        
        await asyncio.sleep(1)
        
        # Schritt 4: Writing Agent - Dokumentation erstellen
        doc_result = await self.chat_with_agent(
            "Schreibe eine technische Dokumentation für die Todo-App API mit Endpoints und Datenstrukturen",
            "writing",
            "API-Dokumentation schreiben"
        )
        
        await asyncio.sleep(1)
        
        # Schritt 5: QA Agent - Testfälle entwickeln
        qa_result = await self.chat_with_agent(
            "Erstelle einen umfassenden Testplan für die Todo-App mit Unit- und Integrationstests",
            "qa",
            "Testplan und Testfälle erstellen"
        )
        
        await asyncio.sleep(1)
        
        # Schritt 6: File Agent - Projektstruktur organisieren
        file_result = await self.chat_with_agent(
            "Wie sollte die Dateistruktur einer Python Flask Todo-App organisiert sein?",
            "file",
            "Projektstruktur organisieren"
        )
        
        await asyncio.sleep(1)
        
        # Schritt 7: GitHub Agent - Repository Setup
        github_result = await self.chat_with_agent(
            "Erkläre, wie man ein GitHub Repository für eine Todo-App einrichtet mit CI/CD",
            "github",
            "GitHub Repository und CI/CD Setup"
        )
        
        await asyncio.sleep(1)
        
        # Schritt 8: Session Agent - Session Management
        session_result = await self.chat_with_agent(
            "Implementiere Session Management für Benutzer-Authentication in der Todo-App",
            "session",
            "Benutzer-Session Management implementieren"
        )
        
        # Sammle Projekt-Daten
        self.project_data = {
            'name': 'Xionimus Todo-App',
            'research': research_result,
            'data_model': data_result,
            'backend_code': code_result,
            'documentation': doc_result,
            'testing': qa_result,
            'file_structure': file_result,
            'github_setup': github_result,
            'session_management': session_result
        }

    async def demo_multi_agent_conversation(self):
        """Demo einer Multi-Agent Konversation"""
        print("\n💬 MULTI-AGENT KONVERSATION DEMO")
        print("=" * 60)
        print("Zeigt, wie mehrere Agenten in einer Unterhaltung zusammenarbeiten")
        print()
        
        # Komplexe Anfrage, die mehrere Agenten involviert
        complex_request = """
        Ich möchte eine E-Commerce Website entwickeln. Kannst du mir helfen bei:
        1. Architektur-Recherche
        2. Datenbank-Design  
        3. Backend-Implementierung
        4. Dokumentation
        5. Testing-Strategie
        6. Deployment-Setup
        """
        
        result = await self.chat_with_agent(
            complex_request,
            None,  # Lass Xionimus den besten Agenten wählen
            "Multi-Agent E-Commerce Projekt"
        )
        
        return result

    async def evaluate_performance(self):
        """Bewerte die Leistung des Demo-Programms"""
        print("\n📊 LEISTUNGSBEWERTUNG")
        print("=" * 60)
        
        total_interactions = len(self.agent_interactions)
        successful_interactions = sum(1 for i in self.agent_interactions if i['success'])
        success_rate = (successful_interactions / total_interactions * 100) if total_interactions > 0 else 0
        
        print(f"📈 Gesamt-Interaktionen: {total_interactions}")
        print(f"✅ Erfolgreiche Interaktionen: {successful_interactions}")
        print(f"📊 Erfolgsrate: {success_rate:.1f}%")
        print()
        
        # Agenten-Verwendung analysieren
        agent_usage = {}
        for interaction in self.agent_interactions:
            agent = interaction['agent']
            if agent not in agent_usage:
                agent_usage[agent] = {'total': 0, 'successful': 0}
            agent_usage[agent]['total'] += 1
            if interaction['success']:
                agent_usage[agent]['successful'] += 1
        
        print("🤖 AGENTEN-NUTZUNGSSTATISTIK:")
        for agent, stats in agent_usage.items():
            rate = (stats['successful'] / stats['total'] * 100) if stats['total'] > 0 else 0
            print(f"  • {agent}: {stats['successful']}/{stats['total']} ({rate:.1f}%)")
        
        print()
        
        # Qualitätsbewertung
        quality_metrics = {
            'Vollständigkeit': success_rate >= 80,
            'Agent-Vielfalt': len(agent_usage) >= 6,
            'Response-Qualität': all(len(i['result']) > 50 for i in self.agent_interactions if i['success']),
            'Fehlerbehandlung': any(not i['success'] for i in self.agent_interactions)
        }
        
        print("🎯 QUALITÄTSMETRIKEN:")
        for metric, passed in quality_metrics.items():
            status = "✅" if passed else "❌"
            print(f"  {status} {metric}")
        
        overall_quality = sum(quality_metrics.values()) / len(quality_metrics) * 100
        
        print(f"\n🏆 GESAMTBEWERTUNG: {overall_quality:.1f}%")
        
        if overall_quality >= 90:
            print("🌟 Exzellent! Xionimus AI arbeitet hervorragend!")
        elif overall_quality >= 75:
            print("✅ Sehr gut! Starke Multi-Agent Performance!")
        elif overall_quality >= 60:
            print("⚠️ Gut, aber Verbesserungen möglich!")
        else:
            print("🔧 Optimierung erforderlich!")
        
        return {
            'total_interactions': total_interactions,
            'successful_interactions': successful_interactions,
            'success_rate': success_rate,
            'agent_usage': agent_usage,
            'quality_metrics': quality_metrics,
            'overall_quality': overall_quality
        }

    async def save_demo_results(self, performance_data: Dict):
        """Speichere Demo-Ergebnisse"""
        demo_report = {
            'timestamp': datetime.now().isoformat(),
            'project_data': self.project_data,
            'interactions': self.agent_interactions,
            'performance': performance_data
        }
        
        report_file = Path('xionimus_demo_results.json')
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(demo_report, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Demo-Ergebnisse gespeichert: {report_file}")
        return report_file

    async def run_complete_demo(self):
        """Führe das komplette Demo-Programm aus"""
        print("🎭 XIONIMUS AI - DEMO-PROGRAMM")
        print("=" * 80)
        print(f"🕐 Gestartet: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("📋 Demonstriert Multi-Agent Koordination und Chatbot-Integration")
        print()
        
        try:
            # Demo-Szenarien ausführen
            await self.demo_scenario_todo_app()
            await self.demo_multi_agent_conversation()
            
            # Leistung bewerten
            performance = await self.evaluate_performance()
            
            # Ergebnisse speichern
            await self.save_demo_results(performance)
            
            print("\n" + "=" * 80)
            print("✅ XIONIMUS DEMO-PROGRAMM ABGESCHLOSSEN")
            print(f"🕐 Beendet: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("=" * 80)
            
            return True
            
        except Exception as e:
            print(f"\n❌ DEMO-FEHLER: {str(e)}")
            return False

async def main():
    """Hauptfunktion für das Xionimus Demo-Programm"""
    try:
        async with XionimusDemoProgram() as demo:
            success = await demo.run_complete_demo()
            return 0 if success else 1
            
    except KeyboardInterrupt:
        print("\n⚠️ Demo durch Benutzer abgebrochen")
        return 2
    except Exception as e:
        print(f"\n❌ Unerwarteter Demo-Fehler: {str(e)}")
        return 3

if __name__ == "__main__":
    import sys
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
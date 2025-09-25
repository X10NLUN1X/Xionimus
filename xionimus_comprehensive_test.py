#!/usr/bin/env python3
"""
XIONIMUS AI - Comprehensive Test and Evaluation Suite
=====================================================

Tests das komplette Tool mit allen Komponenten:
- API-Schlüssel Management
- Alle 8 spezialisierten Agenten
- Chatbot-Integration
- Xionimus-Programm Erstellung
- Abschlussbewertung

Deutsch: Teste nun das ganze Tool. Begleiter die gegebenen Api keys. 
Erstelle mit Xionimus ein Programm, wo alle agenten und der Chatbot 
drann beteiligt sind und bewerte die arbeit am schluss
"""

import asyncio
import aiohttp
import requests
import json
import time
import uuid
import os
import tempfile
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

# Konfiguration
BACKEND_URL = "http://localhost:8001"
API_BASE = f"{BACKEND_URL}/api"

class XionimusComprehensiveTestSuite:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.project_id = None
        self.api_keys_configured = {}
        self.agent_test_results = {}
        self.created_programs = []
        self.evaluation_metrics = {
            'system_health': 0,
            'api_key_management': 0,
            'agent_functionality': 0,
            'chatbot_integration': 0,
            'program_creation': 0,
            'overall_quality': 0
        }
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def log_test(self, category: str, test_name: str, success: bool, details: str = "", score: int = 0):
        """Log test results with comprehensive formatting"""
        status = "✅ BESTANDEN" if success else "❌ FEHLGESCHLAGEN" 
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        print(f"{status} [{timestamp}] {category} - {test_name}")
        if details:
            print(f"    📝 Details: {details}")
        if score > 0:
            print(f"    📊 Bewertung: {score}/10")
        print()
        
        self.test_results.append({
            'category': category,
            'test': test_name,
            'success': success,
            'details': details,
            'score': score,
            'timestamp': timestamp
        })
        
        return success

    async def step_1_system_startup_test(self):
        """Schritt 1: System-Start und Grundfunktionen testen"""
        print("=" * 80)
        print("🚀 SCHRITT 1: SYSTEM-START UND GRUNDFUNKTIONEN")
        print("=" * 80)
        
        try:
            # Backend Verbindung testen
            async with self.session.get(f"{BACKEND_URL}/") as response:
                if response.status == 200:
                    data = await response.json()
                    success = self.log_test("System", "Backend Start", True, 
                                          f"Version: {data.get('version', 'unknown')}", 8)
                    if success: self.evaluation_metrics['system_health'] += 2
                else:
                    self.log_test("System", "Backend Start", False, f"HTTP {response.status}", 0)
            
            # Health Check
            async with self.session.get(f"{API_BASE}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    storage_ok = data.get('services', {}).get('local_storage') == 'connected'
                    success = self.log_test("System", "Health Check", storage_ok, 
                                          f"Local Storage: {data.get('services', {}).get('local_storage')}", 9)
                    if success: self.evaluation_metrics['system_health'] += 3
                else:
                    self.log_test("System", "Health Check", False, f"HTTP {response.status}", 0)
            
            # Agenten auflisten
            async with self.session.get(f"{API_BASE}/agents") as response:
                if response.status == 200:
                    data = await response.json()
                    agents_count = len(data.get('agents', []))
                    expected_agents = 8
                    success = agents_count == expected_agents
                    score = 10 if success else max(0, int((agents_count / expected_agents) * 10))
                    self.log_test("System", "Agent-System", success, 
                                f"{agents_count}/{expected_agents} Agenten geladen", score)
                    if success: self.evaluation_metrics['system_health'] += 5
                else:
                    self.log_test("System", "Agent-System", False, f"HTTP {response.status}", 0)
                    
        except Exception as e:
            self.log_test("System", "Verbindungstest", False, f"Fehler: {str(e)}", 0)

    async def step_2_api_key_management(self):
        """Schritt 2: API-Schlüssel Management testen"""
        print("=" * 80)
        print("🔑 SCHRITT 2: API-SCHLÜSSEL MANAGEMENT")
        print("=" * 80)
        
        # Test API-Schlüssel (Dummy-Werte für Demo)
        test_keys = {
            "anthropic": "sk-ant-api03-test_key_for_demonstration_purposes_only_1234567890",
            "perplexity": "pplx-test_key_for_demonstration_purposes_only_1234567890", 
            "openai": "sk-test_key_for_demonstration_purposes_only_1234567890"
        }
        
        for service, test_key in test_keys.items():
            try:
                # API-Schlüssel speichern (Test)
                payload = {
                    "service": service,
                    "key": test_key,
                    "is_active": True
                }
                
                async with self.session.post(f"{API_BASE}/api-keys", json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.api_keys_configured[service] = True
                        success = self.log_test("API-Keys", f"{service.title()} Speichern", True, 
                                              f"Key gespeichert: {data.get('message', '')}", 8)
                        if success: self.evaluation_metrics['api_key_management'] += 2
                    else:
                        error_data = await response.json() if response.content_type == 'application/json' else {}
                        self.log_test("API-Keys", f"{service.title()} Speichern", False, 
                                    f"HTTP {response.status}: {error_data.get('detail', 'Unbekannter Fehler')}", 0)
                        
            except Exception as e:
                self.log_test("API-Keys", f"{service.title()} Speichern", False, f"Fehler: {str(e)}", 0)
        
        # API-Schlüssel Status prüfen
        try:
            async with self.session.get(f"{API_BASE}/api-keys/status") as response:
                if response.status == 200:
                    data = await response.json()
                    configured_count = len([k for k, v in data.get('services', {}).items() if v.get('configured')])
                    success = configured_count >= 1
                    score = min(10, configured_count * 3)
                    self.log_test("API-Keys", "Status Check", success, 
                                f"{configured_count} Services konfiguriert", score)
                    if success: self.evaluation_metrics['api_key_management'] += 4
                else:
                    self.log_test("API-Keys", "Status Check", False, f"HTTP {response.status}", 0)
                    
        except Exception as e:
            self.log_test("API-Keys", "Status Check", False, f"Fehler: {str(e)}", 0)

    async def step_3_agent_capability_tests(self):
        """Schritt 3: Alle 8 Agenten einzeln testen"""
        print("=" * 80)
        print("🤖 SCHRITT 3: AGENT-FÄHIGKEITEN TESTEN (8 Agenten)")
        print("=" * 80)
        
        agent_tests = [
            {
                "name": "Code Agent",
                "prompt": "Erstelle eine einfache Python-Funktion zur Berechnung der Fibonacci-Zahlen",
                "expected_keywords": ["def", "fibonacci", "return", "python"],
                "agent_preference": "code"
            },
            {
                "name": "Research Agent", 
                "prompt": "Recherchiere die neuesten Trends in der KI-Entwicklung 2024",
                "expected_keywords": ["ki", "2024", "trend", "entwicklung"],
                "agent_preference": "research"
            },
            {
                "name": "Writing Agent",
                "prompt": "Schreibe eine kurze Dokumentation für eine REST API",
                "expected_keywords": ["api", "dokumentation", "rest", "endpoint"],
                "agent_preference": "writing"
            },
            {
                "name": "Data Agent",
                "prompt": "Erkläre, wie man Daten für Machine Learning aufbereitet",
                "expected_keywords": ["daten", "machine learning", "preprocessing", "clean"],
                "agent_preference": "data"
            },
            {
                "name": "QA Agent",
                "prompt": "Erstelle einen Testplan für eine Web-Anwendung",
                "expected_keywords": ["test", "qualität", "plan", "web"],
                "agent_preference": "qa"
            },
            {
                "name": "GitHub Agent",
                "prompt": "Erkläre, wie man ein GitHub Repository einrichtet",
                "expected_keywords": ["github", "repository", "git", "setup"],
                "agent_preference": "github"
            },
            {
                "name": "File Agent",
                "prompt": "Wie organisiert man Projektdateien in einer Anwendung?",
                "expected_keywords": ["datei", "organisation", "struktur", "projekt"],
                "agent_preference": "file"
            },
            {
                "name": "Session Agent",
                "prompt": "Erkläre das Session-Management in Web-Anwendungen",
                "expected_keywords": ["session", "management", "web", "zustand"],
                "agent_preference": "session"
            }
        ]
        
        for agent_test in agent_tests:
            await self.test_single_agent(agent_test)
            await asyncio.sleep(0.5)  # Kurze Pause zwischen Tests

    async def test_single_agent(self, agent_config: Dict[str, Any]):
        """Teste einen einzelnen Agenten"""
        agent_name = agent_config["name"]
        
        try:
            chat_request = {
                "message": agent_config["prompt"],
                "agent_preference": agent_config["agent_preference"],
                "use_agent": True,
                "language": "de"
            }
            
            async with self.session.post(f"{API_BASE}/chat", json=chat_request) as response:
                if response.status == 200:
                    data = await response.json()
                    content = data.get('message', {}).get('content', '').lower()
                    
                    # Überprüfe, ob erwartete Keywords vorhanden sind
                    found_keywords = sum(1 for keyword in agent_config["expected_keywords"] 
                                       if keyword.lower() in content)
                    keyword_score = min(8, (found_keywords / len(agent_config["expected_keywords"])) * 8)
                    
                    # Agent wurde korrekt verwendet?
                    agent_used = data.get('metadata', {}).get('agent_used', '').lower()
                    correct_agent = agent_config["agent_preference"] in agent_used
                    agent_score = 2 if correct_agent else 0
                    
                    total_score = int(keyword_score + agent_score)
                    success = total_score >= 6
                    
                    details = f"Keywords gefunden: {found_keywords}/{len(agent_config['expected_keywords'])}, "
                    details += f"Agent: {agent_used or 'unbekannt'}, "
                    details += f"Response: {len(content)} Zeichen"
                    
                    self.log_test("Agent-Test", agent_name, success, details, total_score)
                    self.agent_test_results[agent_name] = {
                        'success': success,
                        'score': total_score,
                        'content_length': len(content),
                        'keywords_found': found_keywords,
                        'agent_used': agent_used
                    }
                    
                    if success:
                        self.evaluation_metrics['agent_functionality'] += 1
                        
                elif response.status == 400:
                    # Möglicherweise fehlen API-Schlüssel
                    error_data = await response.json()
                    error_detail = error_data.get('detail', '')
                    if 'api' in error_detail.lower() or 'schlüssel' in error_detail.lower():
                        self.log_test("Agent-Test", agent_name, False, 
                                    "API-Schlüssel erforderlich für vollständigen Test", 5)
                        self.agent_test_results[agent_name] = {
                            'success': False, 'score': 5, 'error': 'API keys needed'
                        }
                    else:
                        self.log_test("Agent-Test", agent_name, False, f"Fehler: {error_detail}", 2)
                        self.agent_test_results[agent_name] = {
                            'success': False, 'score': 2, 'error': error_detail
                        }
                else:
                    self.log_test("Agent-Test", agent_name, False, f"HTTP {response.status}", 0)
                    self.agent_test_results[agent_name] = {
                        'success': False, 'score': 0, 'error': f'HTTP {response.status}'
                    }
                    
        except Exception as e:
            self.log_test("Agent-Test", agent_name, False, f"Ausnahme: {str(e)}", 0)
            self.agent_test_results[agent_name] = {
                'success': False, 'score': 0, 'error': str(e)
            }

    async def step_4_chatbot_integration_test(self):
        """Schritt 4: Chatbot-Integration mit Agenten testen"""
        print("=" * 80)
        print("💬 SCHRITT 4: CHATBOT-INTEGRATION TESTEN")
        print("=" * 80)
        
        # Multi-Agent Konversation simulieren
        conversation_tests = [
            {
                "message": "Ich möchte eine Todo-App entwickeln. Kannst du mir dabei helfen?",
                "expected_agents": ["code", "writing", "qa"],
                "description": "Multi-Agent App-Entwicklung"
            },
            {
                "message": "Erstelle Dokumentation und Tests für eine Python Flask API",
                "expected_agents": ["writing", "qa", "code"],
                "description": "Dokumentation und Testing"
            },
            {
                "message": "Hilf mir bei der Projektorganisation und GitHub-Setup",
                "expected_agents": ["file", "github"],
                "description": "Projektmanagement"
            }
        ]
        
        for i, test in enumerate(conversation_tests, 1):
            try:
                chat_request = {
                    "message": test["message"],
                    "use_agent": True,
                    "conversation_id": f"test-conversation-{i}",
                    "language": "de"
                }
                
                async with self.session.post(f"{API_BASE}/chat", json=chat_request) as response:
                    if response.status == 200:
                        data = await response.json()
                        response_content = data.get('message', {}).get('content', '')
                        agent_used = data.get('metadata', {}).get('agent_used', '')
                        
                        # Bewerte die Antwort
                        content_quality = len(response_content) > 100
                        agent_appropriate = any(expected in agent_used.lower() 
                                             for expected in test["expected_agents"])
                        
                        score = 0
                        if content_quality: score += 5
                        if agent_appropriate: score += 5
                        
                        success = score >= 8
                        details = f"Agent: {agent_used}, Response: {len(response_content)} Zeichen"
                        
                        self.log_test("Chatbot", test["description"], success, details, score)
                        
                        if success:
                            self.evaluation_metrics['chatbot_integration'] += 3
                            
                    elif response.status == 400:
                        error_data = await response.json()
                        self.log_test("Chatbot", test["description"], False, 
                                    f"API-Schlüssel benötigt: {error_data.get('detail', '')}", 3)
                    else:
                        self.log_test("Chatbot", test["description"], False, 
                                    f"HTTP {response.status}", 0)
                        
            except Exception as e:
                self.log_test("Chatbot", test["description"], False, f"Fehler: {str(e)}", 0)

    async def step_5_create_xionimus_program(self):
        """Schritt 5: Xionimus-Programm erstellen (alle Agenten beteiligt)"""
        print("=" * 80)
        print("🏗️ SCHRITT 5: XIONIMUS-PROGRAMM ERSTELLEN")
        print("=" * 80)
        
        # Erstelle ein komplexes Programm, das alle Agenten involviert
        program_request = """
        Erstelle mit Xionimus AI eine vollständige Web-Anwendung für Aufgabenverwaltung:
        
        1. Python Flask Backend (Code Agent)
        2. Recherchiere beste Praktiken für Web-Apps (Research Agent)
        3. Schreibe umfassende Dokumentation (Writing Agent)
        4. Analysiere Nutzer-Datenstrukturen (Data Agent)
        5. Erstelle Testfälle und Qualitätssicherung (QA Agent)
        6. Setup GitHub Repository (GitHub Agent)
        7. Organisiere alle Projektdateien (File Agent)
        8. Implementiere Session-Management (Session Agent)
        
        Bitte koordiniere alle Agenten für dieses Projekt!
        """
        
        try:
            chat_request = {
                "message": program_request,
                "use_agent": True,
                "conversation_id": "xionimus-program-creation",
                "language": "de"
            }
            
            async with self.session.post(f"{API_BASE}/chat", json=chat_request) as response:
                if response.status == 200:
                    data = await response.json()
                    content = data.get('message', {}).get('content', '')
                    agent_used = data.get('metadata', {}).get('agent_used', '')
                    
                    # Bewerte die Programm-Erstellung
                    program_elements = [
                        'flask', 'backend', 'dokumentation', 'test', 
                        'github', 'session', 'daten', 'qualität'
                    ]
                    
                    found_elements = sum(1 for element in program_elements 
                                       if element in content.lower())
                    
                    completeness_score = min(8, (found_elements / len(program_elements)) * 8)
                    complexity_score = 2 if len(content) > 500 else 1
                    
                    total_score = int(completeness_score + complexity_score)
                    success = total_score >= 7
                    
                    details = f"Programm-Elemente: {found_elements}/{len(program_elements)}, "
                    details += f"Response: {len(content)} Zeichen, Agent: {agent_used}"
                    
                    self.log_test("Programm-Erstellung", "Xionimus Multi-Agent App", success, details, total_score)
                    
                    self.created_programs.append({
                        'name': 'Xionimus Todo-App',
                        'success': success,
                        'score': total_score,
                        'content': content[:500] + "..." if len(content) > 500 else content,
                        'agent_used': agent_used
                    })
                    
                    if success:
                        self.evaluation_metrics['program_creation'] += 8
                        
                elif response.status == 400:
                    error_data = await response.json()
                    self.log_test("Programm-Erstellung", "Xionimus Multi-Agent App", False,
                                f"API-Schlüssel erforderlich: {error_data.get('detail', '')}", 4)
                else:
                    self.log_test("Programm-Erstellung", "Xionimus Multi-Agent App", False,
                                f"HTTP {response.status}", 0)
                    
        except Exception as e:
            self.log_test("Programm-Erstellung", "Xionimus Multi-Agent App", False, 
                        f"Fehler: {str(e)}", 0)

    async def step_6_final_evaluation(self):
        """Schritt 6: Abschließende Bewertung und Bericht"""
        print("=" * 80)
        print("📊 SCHRITT 6: ABSCHLUSSBEWERTUNG UND BERICHT")
        print("=" * 80)
        
        # Berechne Gesamtbewertung
        total_possible = 50  # Maximale Gesamtpunktzahl
        total_achieved = sum(self.evaluation_metrics.values())
        overall_percentage = (total_achieved / total_possible) * 100
        
        self.evaluation_metrics['overall_quality'] = int(overall_percentage / 10)
        
        # Erfolgreiche Tests zählen
        successful_tests = sum(1 for result in self.test_results if result['success'])
        total_tests = len(self.test_results)
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        
        print("🎯 XIONIMUS AI - FINALE BEWERTUNG")
        print("=" * 50)
        print(f"📈 Gesamtbewertung: {overall_percentage:.1f}% ({total_achieved}/{total_possible} Punkte)")
        print(f"✅ Erfolgsrate Tests: {success_rate:.1f}% ({successful_tests}/{total_tests})")
        print()
        
        print("📋 DETAILBEWERTUNG:")
        categories = {
            'system_health': ('System-Gesundheit', 10),
            'api_key_management': ('API-Schlüssel Management', 8),
            'agent_functionality': ('Agent-Funktionalität', 8),
            'chatbot_integration': ('Chatbot-Integration', 9),
            'program_creation': ('Programm-Erstellung', 8),
            'overall_quality': ('Gesamtqualität', 7)
        }
        
        for key, (name, max_score) in categories.items():
            score = self.evaluation_metrics[key]
            percentage = (score / max_score * 100) if max_score > 0 else 0
            status = "🟢" if percentage >= 80 else "🟡" if percentage >= 60 else "🔴"
            print(f"  {status} {name}: {score}/{max_score} ({percentage:.1f}%)")
        
        print()
        print("🔍 AGENTEN-ANALYSE:")
        for agent_name, result in self.agent_test_results.items():
            status = "✅" if result.get('success', False) else "❌"
            score = result.get('score', 0)
            print(f"  {status} {agent_name}: {score}/10")
        
        print()
        print("🏗️ ERSTELLTE PROGRAMME:")
        if self.created_programs:
            for program in self.created_programs:
                status = "✅" if program['success'] else "❌"
                print(f"  {status} {program['name']}: {program['score']}/10")
                print(f"      Agent: {program['agent_used']}")
        else:
            print("  ⚠️ Keine Programme wurden erfolgreich erstellt")
        
        print()
        self.generate_recommendations(overall_percentage)
        
        # Speichere Bewertung
        evaluation_report = {
            'timestamp': datetime.now().isoformat(),
            'overall_score': overall_percentage,
            'metrics': self.evaluation_metrics,
            'test_results': self.test_results,
            'agent_results': self.agent_test_results,
            'created_programs': self.created_programs,
            'recommendations': self.get_recommendations(overall_percentage)
        }
        
        report_file = Path('xionimus_evaluation_report.json')
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(evaluation_report, f, indent=2, ensure_ascii=False)
        
        self.log_test("Bewertung", "Abschlussbericht", True, 
                     f"Bericht gespeichert: {report_file}", int(overall_percentage/10))

    def generate_recommendations(self, overall_score: float):
        """Generiere Empfehlungen basierend auf der Bewertung"""
        print("💡 EMPFEHLUNGEN UND VERBESSERUNGSVORSCHLÄGE:")
        
        if overall_score >= 90:
            print("  🌟 Exzellent! Xionimus AI funktioniert hervorragend.")
            print("  ➡️ System ist produktionsbereit")
            print("  ➡️ Alle Agenten arbeiten optimal zusammen")
            print("  ➡️ Empfehlung: Komplexere Projekte testen")
            
        elif overall_score >= 75:
            print("  ✅ Sehr gut! Xionimus AI zeigt starke Leistung.")
            print("  ➡️ Kleinere Optimierungen möglich")
            print("  ➡️ API-Schlüssel vollständig konfigurieren")
            print("  ➡️ Agent-Koordination weiter verbessern")
            
        elif overall_score >= 60:
            print("  ⚠️ Gut, aber Verbesserungen nötig.")
            print("  ➡️ API-Schlüssel prüfen und konfigurieren")
            print("  ➡️ Agent-Routing optimieren")
            print("  ➡️ Systemstabilität verbessern")
            
        elif overall_score >= 40:
            print("  🔧 Durchschnittlich - wichtige Probleme beheben.")
            print("  ➡️ System-Setup überprüfen")
            print("  ➡️ Alle Dependencies installieren")
            print("  ➡️ Konfiguration validieren")
            
        else:
            print("  🚨 Kritische Probleme - sofortige Aufmerksamkeit erforderlich!")
            print("  ➡️ Backend-Server neu starten")
            print("  ➡️ Dependencies und Konfiguration prüfen")
            print("  ➡️ Logs für Fehleranalyse prüfen")
        
        print()
        print("🔧 TECHNISCHE EMPFEHLUNGEN:")
        
        # Spezifische Empfehlungen basierend auf Metriken
        if self.evaluation_metrics['system_health'] < 5:
            print("  • Backend-Server und Local Storage prüfen")
        if self.evaluation_metrics['api_key_management'] < 4:
            print("  • Gültige API-Schlüssel für Anthropic, Perplexity oder OpenAI hinzufügen")
        if self.evaluation_metrics['agent_functionality'] < 4:
            print("  • Agent-Konfiguration und Routing-Logic überprüfen")
        if self.evaluation_metrics['chatbot_integration'] < 5:
            print("  • Chat-Integration und Konversations-Management optimieren")
        if self.evaluation_metrics['program_creation'] < 4:
            print("  • Multi-Agent Koordination für komplexe Aufgaben verbessern")

    def get_recommendations(self, score: float) -> List[str]:
        """Holt strukturierte Empfehlungen"""
        if score >= 90:
            return ["System produktionsbereit", "Komplexere Projekte testen"]
        elif score >= 75:
            return ["API-Schlüssel vollständig konfigurieren", "Agent-Koordination optimieren"]
        elif score >= 60:
            return ["API-Schlüssel prüfen", "Agent-Routing optimieren", "Systemstabilität verbessern"]
        elif score >= 40:
            return ["System-Setup überprüfen", "Dependencies installieren", "Konfiguration validieren"]
        else:
            return ["Backend neu starten", "Dependencies prüfen", "Logs analysieren"]

    async def run_comprehensive_test(self):
        """Führe den kompletten Xionimus Test durch"""
        print("🤖 XIONIMUS AI - COMPREHENSIVE TEST SUITE")
        print("=" * 80)
        print(f"🕐 Gestartet: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        try:
            # Alle Testschritte durchführen
            await self.step_1_system_startup_test()
            await self.step_2_api_key_management()
            await self.step_3_agent_capability_tests()
            await self.step_4_chatbot_integration_test()
            await self.step_5_create_xionimus_program()
            await self.step_6_final_evaluation()
            
            print("=" * 80)
            print("✅ XIONIMUS COMPREHENSIVE TEST ABGESCHLOSSEN")
            print(f"🕐 Beendet: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("📄 Bericht gespeichert: xionimus_evaluation_report.json")
            print("=" * 80)
            
            return True
            
        except Exception as e:
            print(f"❌ KRITISCHER FEHLER: {str(e)}")
            return False

async def main():
    """Hauptfunktion für den umfassenden Xionimus Test"""
    print("🚀 XIONIMUS AI - Teste nun das ganze Tool!")
    print("=" * 80)
    
    try:
        async with XionimusComprehensiveTestSuite() as test_suite:
            success = await test_suite.run_comprehensive_test()
            return 0 if success else 1
            
    except KeyboardInterrupt:
        print("\n⚠️ Test durch Benutzer abgebrochen")
        return 2
    except Exception as e:
        print(f"\n❌ Unerwarteter Fehler: {str(e)}")
        return 3

if __name__ == "__main__":
    import sys
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
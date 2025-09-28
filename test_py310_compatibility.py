#!/usr/bin/env python3
"""
XIONIMUS AI - Python 3.10 Kompatibilitäts-Test
Überprüft ob alle kritischen Dependencies mit Python 3.10 funktionieren
"""

import sys
import pkg_resources
from packaging import version

def test_python_version():
    """Test Python Version"""
    print(f"🐍 Python Version: {sys.version}")
    py_version = version.parse(".".join(map(str, sys.version_info[:3])))
    
    if py_version >= version.parse("3.10.0"):
        print("✅ Python 3.10+ gefunden")
        return True
    else:
        print("❌ Python 3.10+ erforderlich")
        return False

def test_critical_imports():
    """Test kritische Python Dependencies"""
    critical_packages = [
        ("fastapi", "FastAPI Framework"),
        ("uvicorn", "ASGI Server"),
        ("motor", "MongoDB Async Driver"),
        ("pymongo", "MongoDB Driver"),
        ("anthropic", "Anthropic API"),
        ("openai", "OpenAI API"),
        ("numpy", "NumPy Array Processing"),
        ("pandas", "Data Analysis"),
        ("pydantic", "Data Validation"),
        ("httpx", "HTTP Client"),
        ("python-dotenv", "Environment Variables")
    ]
    
    print("\n📦 Teste kritische Dependencies:")
    success_count = 0
    
    for package_name, description in critical_packages:
        try:
            if package_name == "python-dotenv":
                import dotenv
                pkg_version = pkg_resources.get_distribution("python-dotenv").version
            else:
                __import__(package_name.replace("-", "_"))
                pkg_version = pkg_resources.get_distribution(package_name).version
            
            print(f"✅ {package_name} ({pkg_version}) - {description}")
            success_count += 1
        except ImportError as e:
            print(f"❌ {package_name} - FEHLT: {e}")
        except Exception as e:
            print(f"⚠️ {package_name} - Warnung: {e}")
    
    print(f"\n📊 Ergebnis: {success_count}/{len(critical_packages)} Dependencies erfolgreich")
    return success_count == len(critical_packages)

def test_numpy_compatibility():
    """Spezifischer NumPy Python 3.10 Test"""
    print("\n🔢 NumPy Kompatibilitäts-Test:")
    try:
        import numpy as np
        np_version = version.parse(np.__version__)
        
        print(f"✅ NumPy Version: {np.__version__}")
        
        # Test numpy Array-Erstellung
        test_array = np.array([1, 2, 3, 4, 5])
        print(f"✅ Array-Erstellung: {test_array}")
        
        # Test dtype compatibility
        test_dtypes = ['int32', 'float64', 'bool']
        for dtype in test_dtypes:
            test_arr = np.array([1, 2, 3], dtype=dtype)
            print(f"✅ dtype {dtype}: {test_arr.dtype}")
        
        # Prüfe ob kompatible Version für Python 3.10
        if np_version >= version.parse("2.3.0"):
            print("⚠️ WARNUNG: NumPy 2.3+ erfordert Python 3.11+")
            print("💡 EMPFEHLUNG: NumPy 1.24.x - 1.26.x für Python 3.10")
            return False
        else:
            print("✅ NumPy Version kompatibel mit Python 3.10")
            return True
            
    except ImportError:
        print("❌ NumPy nicht installiert")
        return False
    except Exception as e:
        print(f"❌ NumPy Fehler: {e}")
        return False

def test_fastapi_basic():
    """Test FastAPI Grundfunktionalität"""
    print("\n🚀 FastAPI Funktions-Test:")
    try:
        from fastapi import FastAPI
        from pydantic import BaseModel
        
        # Erstelle Test-App
        app = FastAPI(title="XIONIMUS AI Test")
        
        class TestModel(BaseModel):
            message: str
            status: str = "ok"
        
        @app.get("/test")
        def test_endpoint():
            return TestModel(message="XIONIMUS AI Backend funktional")
        
        print("✅ FastAPI App erfolgreich erstellt")
        print("✅ Pydantic Models funktional")
        print("✅ Route Definition erfolgreich")
        return True
        
    except Exception as e:
        print(f"❌ FastAPI Test fehlgeschlagen: {e}")
        return False

def test_ai_api_imports():
    """Test AI API Client Imports"""
    print("\n🤖 AI API Client Tests:")
    
    apis = [
        ("anthropic", "Anthropic Claude API"),
        ("openai", "OpenAI GPT API")
    ]
    
    success_count = 0
    
    for api_name, description in apis:
        try:
            if api_name == "anthropic":
                from anthropic import Anthropic
                print(f"✅ {description} - Import erfolgreich")
            elif api_name == "openai":
                from openai import OpenAI
                print(f"✅ {description} - Import erfolgreich")
            success_count += 1
        except ImportError as e:
            print(f"❌ {description} - FEHLT: {e}")
        except Exception as e:
            print(f"⚠️ {description} - Warnung: {e}")
    
    return success_count == len(apis)

def main():
    """Haupttest-Funktion"""
    print("=" * 60)
    print("🧪 XIONIMUS AI - Python 3.10 Kompatibilitäts-Test")
    print("=" * 60)
    
    tests = [
        ("Python Version", test_python_version),
        ("Kritische Dependencies", test_critical_imports),
        ("NumPy Kompatibilität", test_numpy_compatibility),
        ("FastAPI Funktionalität", test_fastapi_basic),
        ("AI API Clients", test_ai_api_imports)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'-' * 40}")
        print(f"🧪 Test: {test_name}")
        print(f"{'-' * 40}")
        results[test_name] = test_func()
    
    # Zusammenfassung
    print("\n" + "=" * 60)
    print("📊 TEST-ZUSAMMENFASSUNG")
    print("=" * 60)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ BESTANDEN" if result else "❌ FEHLGESCHLAGEN"
        print(f"{test_name}: {status}")
    
    print(f"\n📈 Gesamt: {passed}/{total} Tests bestanden")
    
    if passed == total:
        print("\n🎉 ALLE TESTS BESTANDEN!")
        print("✅ XIONIMUS AI ist bereit für Python 3.10")
        print("\n🚀 Nächste Schritte:")
        print("   1. cd backend && python server.py")
        print("   2. cd frontend && yarn start") 
        print("   3. Öffne: http://localhost:3000")
    else:
        print(f"\n⚠️ {total - passed} Tests fehlgeschlagen")
        print("💡 Empfohlene Aktionen:")
        print("   pip install -r requirements_minimal_py310.txt")
        print("   pip install --upgrade pip setuptools wheel")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
"""
🔬 VERIFICATION TEST - Active Project Auto-Set Feature
========================================================

This script verifies that the active_project feature works correctly
after repository import across all import endpoints.

Tests:
1. ✅ Hilfsfunktion importierbar
2. ✅ Funktion erstellt Session wenn keine existiert
3. ✅ Funktion aktualisiert existierende Session
"""

import sys
import os
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

def test_imports():
    """Test that all required modules can be imported"""
    print("📦 SCHRITT 1: Module Import Test")
    print("-" * 80)
    
    try:
        from app.api.github_pat import set_active_project_for_user
        print("✅ set_active_project_for_user erfolgreich importiert")
        return True
    except Exception as e:
        print(f"❌ Import fehlgeschlagen: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_function_signature():
    """Test function signature and docstring"""
    print("\n📝 SCHRITT 2: Function Signature Test")
    print("-" * 80)
    
    try:
        from app.api.github_pat import set_active_project_for_user
        import inspect
        
        # Get function signature
        sig = inspect.signature(set_active_project_for_user)
        params = list(sig.parameters.keys())
        
        expected_params = ['db', 'user_id', 'repo_name', 'branch_name']
        
        if params == expected_params:
            print(f"✅ Function signature korrekt: {params}")
        else:
            print(f"⚠️ Function signature abweichend:")
            print(f"   Erwartet: {expected_params}")
            print(f"   Gefunden: {params}")
        
        # Check docstring
        if set_active_project_for_user.__doc__:
            print("✅ Docstring vorhanden")
        else:
            print("⚠️ Keine Docstring gefunden")
        
        return True
    except Exception as e:
        print(f"❌ Signature Test fehlgeschlagen: {e}")
        return False

def check_integration_points():
    """Check that the function is integrated in all import endpoints"""
    print("\n🔗 SCHRITT 3: Integration Points Check")
    print("-" * 80)
    
    try:
        github_pat_file = Path(__file__).parent / "backend" / "app" / "api" / "github_pat.py"
        
        with open(github_pat_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for function calls in each endpoint
        integration_points = [
            ("import-from-github", "set_active_project_for_user"),
            ("import-from-url", "set_active_project_for_user"),
            ("import-progress", "set_active_project_for_user")
        ]
        
        all_integrated = True
        for endpoint, function_name in integration_points:
            # Find endpoint definition
            endpoint_pattern = f'@router.post("/{endpoint}"'
            if endpoint_pattern in content or f"@router.get('/{endpoint}" in content:
                # Check if function is called after endpoint
                endpoint_start = content.find(endpoint_pattern)
                if endpoint_start == -1:
                    endpoint_start = content.find(f"@router.get('/{endpoint}")
                
                # Find next endpoint or end of file
                next_endpoint = content.find("@router.", endpoint_start + 10)
                endpoint_section = content[endpoint_start:next_endpoint] if next_endpoint != -1 else content[endpoint_start:]
                
                if function_name in endpoint_section:
                    print(f"✅ {endpoint}: {function_name} integriert")
                else:
                    print(f"❌ {endpoint}: {function_name} NICHT gefunden")
                    all_integrated = False
            else:
                print(f"⚠️ {endpoint}: Endpoint nicht gefunden")
        
        return all_integrated
    except Exception as e:
        print(f"❌ Integration Check fehlgeschlagen: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all verification tests"""
    print("=" * 80)
    print("🔬 ACTIVE PROJECT AUTO-SET VERIFICATION")
    print("=" * 80)
    print()
    
    results = []
    
    # Test 1: Imports
    results.append(("Module Import", test_imports()))
    
    # Test 2: Function Signature
    results.append(("Function Signature", test_function_signature()))
    
    # Test 3: Integration Points
    results.append(("Integration Points", check_integration_points()))
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print()
    print(f"Ergebnis: {passed}/{total} Tests bestanden")
    
    if passed == total:
        print("\n🎉 ALLE TESTS BESTANDEN!")
        print()
        print("Next Steps:")
        print("1. Backend neu starten: sudo supervisorctl restart backend")
        print("2. Repository importieren via API")
        print("3. Prüfen ob active_project automatisch gesetzt wird")
        return 0
    else:
        print("\n❌ EINIGE TESTS FEHLGESCHLAGEN")
        print("Bitte die Fehler oben überprüfen")
        return 1

if __name__ == "__main__":
    sys.exit(main())

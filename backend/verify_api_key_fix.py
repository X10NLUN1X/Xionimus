"""
Verify that the API Key fix is correctly applied
"""
from pathlib import Path

chat_file = Path('app/api/chat.py')

if not chat_file.exists():
    print('❌ ERROR: chat.py not found')
    exit(1)

content = chat_file.read_text(encoding='utf-8')

# Check if the fix is applied
checks = {
    'AUTO_LOAD_API_KEYS marker': 'AUTO-LOAD' in content,
    'get_user_api_keys call': 'get_user_api_keys(db, current_user.user_id)' in content,
    'Loading log message': 'Loading API keys from database for user' in content,
    'Loaded success log': 'Loaded {len(request.api_keys)} API keys' in content,
}

print("=" * 70)
print("API Key Fix Verification")
print("=" * 70)

all_ok = True
for check_name, result in checks.items():
    status = "✅" if result else "❌"
    print(f"{status} {check_name}: {'PASS' if result else 'FAIL'}")
    if not result:
        all_ok = False

print("=" * 70)

if all_ok:
    print("✅ ALL CHECKS PASSED - Fix is correctly applied!")
    
    # Show the actual code snippet
    print("\nCode snippet:")
    print("-" * 70)
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if 'API KEYS AUTO-LOAD' in line:
            # Show 20 lines
            for j in range(max(0, i-2), min(len(lines), i+20)):
                print(f"{j+1:4d}: {lines[j]}")
            break
    print("-" * 70)
else:
    print("❌ SOME CHECKS FAILED - Fix may not be applied correctly!")
    print("\nPlease run: python fix_chat_api_keys.py")

print()

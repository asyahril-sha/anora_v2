import sys
import os

print("=== START TEST ===")
print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")
print(f"Files in current directory: {os.listdir('.')}")

try:
    print("Importing config...")
    from config import get_settings
    print("✅ Config imported")
    
    settings = get_settings()
    print(f"✅ Settings loaded: ADMIN_ID={settings.admin_id}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("=== END TEST ===")

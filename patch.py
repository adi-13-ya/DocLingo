#!/usr/bin/env python3
"""
Quick fix script for DocLingo query_engine imports
Run this in your project root: python fix_imports.py
"""

import os
import sys

def fix_router_imports():
    """Fix the imports in router.py"""
    router_path = "query_engine/router.py"
    
    if not os.path.exists(router_path):
        print(f"❌ {router_path} not found!")
        return False
    
    print(f"📝 Fixing {router_path}...")
    
    with open(router_path, 'r') as f:
        content = f.read()
    
    # Fix imports
    replacements = [
        ("from query_engine.intent_classifier import", "from .intent_classifier import"),
        ("from metadata_engine import", "from .metadata_engine import"),
        ("from aggregate_engine import", "from .aggregate_engine import"),
        ("from analytical_engine import", "from .analytical_engine import"),
        ("from content_engine import", "from .content_engine import"),
    ]
    
    for old, new in replacements:
        if old in content:
            content = content.replace(old, new)
            print(f"  ✓ Fixed: {old} → {new}")
    
    # Write back
    with open(router_path, 'w') as f:
        f.write(content)
    
    print(f"✅ {router_path} fixed!")
    return True


def create_init_file():
    """Create __init__.py in query_engine/"""
    init_path = "query_engine/__init__.py"
    
    if os.path.exists(init_path):
        print(f"✓ {init_path} already exists")
        return True
    
    print(f"📝 Creating {init_path}...")
    
    init_content = '''"""
Query Engine Package
Intelligent query routing system for DocLingo
"""

# Export main classes for easier imports
from .router import QueryRouter, route_query
from .intent_classifier import IntentClassifier, QueryIntent
from .metadata_engine import MetadataEngine
from .aggregate_engine import AggregateEngine
from .analytical_engine import AnalyticalEngine
from .content_engine import ContentEngine

__all__ = [
    'QueryRouter',
    'route_query',
    'IntentClassifier',
    'QueryIntent',
    'MetadataEngine',
    'AggregateEngine',
    'AnalyticalEngine',
    'ContentEngine',
]
'''
    
    with open(init_path, 'w') as f:
        f.write(init_content)
    
    print(f"✅ {init_path} created!")
    return True


def verify_files():
    """Verify all required files exist"""
    required_files = [
        "query_engine/__init__.py",
        "query_engine/intent_classifier.py",
        "query_engine/metadata_engine.py",
        "query_engine/aggregate_engine.py",
        "query_engine/analytical_engine.py",
        "query_engine/content_engine.py",
        "query_engine/router.py",
    ]
    
    print("\n🔍 Verifying files...")
    all_exist = True
    
    for file in required_files:
        if os.path.exists(file):
            print(f"  ✓ {file}")
        else:
            print(f"  ❌ {file} MISSING!")
            all_exist = False
    
    return all_exist


def test_imports():
    """Test if imports work"""
    print("\n🧪 Testing imports...")
    
    try:
        from query_engine.router import QueryRouter
        print("  ✓ QueryRouter import successful")
        
        from query_engine.intent_classifier import IntentClassifier, QueryIntent
        print("  ✓ IntentClassifier import successful")
        
        from query_engine import route_query
        print("  ✓ route_query import successful")
        
        print("\n✅ All imports working!")
        return True
    
    except Exception as e:
        print(f"\n❌ Import failed: {e}")
        return False


def main():
    print("="*60)
    print("DocLingo Import Fixer")
    print("="*60)
    
    # Step 1: Create __init__.py
    if not create_init_file():
        print("\n❌ Failed to create __init__.py")
        return
    
    # Step 2: Fix router.py imports
    if not fix_router_imports():
        print("\n❌ Failed to fix router.py")
        return
    
    # Step 3: Verify files
    if not verify_files():
        print("\n⚠️  Some files are missing!")
        print("Please ensure all query_engine files are present.")
        return
    
    # Step 4: Test imports
    test_imports()
    
    print("\n" + "="*60)
    print("✅ Fix complete! You can now run your app.")
    print("="*60)
    print("\nNext steps:")
    print("1. Set OPENAI_API_KEY: export OPENAI_API_KEY='your-key'")
    print("2. Run app: streamlit run app.py")


if __name__ == "__main__":
    main()
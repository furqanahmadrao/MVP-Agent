#!/usr/bin/env python3
"""
Test script for MVP Agent application
This script tests the basic functionality of the application without requiring API keys
"""

import os
import sys
import time
import threading
from typing import Dict, Any

# Add workspace to path
sys.path.insert(0, '/workspace')

def test_mcp_servers():
    """Test MCP server functionality"""
    print("🧪 Testing MCP Server Management...")
    try:
        from src.mcp_process_manager import MCPManager
        manager = MCPManager()
        print(f"✅ MCP Manager created successfully: {type(manager)}")
        
        # Check expected MCP processes
        if hasattr(manager, 'mcp_processes'):
            print(f"   Expected MCP processes: {len(manager.mcp_processes)}")
        else:
            print("   MCP processes attribute not directly accessible (this is normal)")
            
        # List expected MCP servers based on README
        expected_servers = [
            "file-manager-mcp (Port 8081)",
            "google-search-mcp (Port 8082)", 
            "markdownify-mcp (Port 8083 - assumed based on pattern)"
        ]
        print(f"   Expected MCP servers: {len(expected_servers)}")
        for server in expected_servers:
            print(f"     - {server}")
        
        return True
    except Exception as e:
        print(f"❌ MCP Server test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_core_components():
    """Test core application components"""
    print("\n🧪 Testing Core Components...")
    try:
        # Test imports
        from src.agent_brain import create_agent
        from src.ai_models import GeminiClient
        from src.file_manager import get_file_manager
        from src.validators import validate_idea, sanitize_idea
        from src.error_handler import get_error_handler
        
        print("✅ All core modules imported successfully")
        
        # Test idea validation
        test_ideas = [
            "A simple idea",
            "   Ideas with spaces   ",
            "",
            "x" * 500  # Very long idea
        ]
        
        print("   Testing idea validation:")
        for i, idea in enumerate(test_ideas):
            is_valid, error_msg = validate_idea(idea)
            print(f"     Test {i+1}: '{idea[:20]}...' -> Valid: {is_valid}")
            if not is_valid:
                print(f"               Error: {error_msg}")
        
        # Test idea sanitization
        print("   Testing idea sanitization:")
        test_sanitizations = [
            "  Test idea with spaces  ",
            "Test\tidea\nwith\nwhitespace",
            "Test<script>alert('xss')</script>idea"
        ]
        
        from src.validators import sanitize_idea
        for i, idea in enumerate(test_sanitizations):
            sanitized = sanitize_idea(idea)
            print(f"     Test {i+1}: '{idea[:30]}...' -> '{sanitized[:30]}...'")
        
        return True
    except Exception as e:
        print(f"❌ Core components test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_prompts():
    """Test prompt templates"""
    print("\n🧪 Testing Prompt Templates...")
    try:
        from src.prompts import PromptTemplates, SYSTEM_PROMPTS, get_system_prompt
        
        print("✅ Prompt templates imported successfully")
        print(f"   Available system prompts: {len(SYSTEM_PROMPTS)}")
        
        # Test getting system prompts
        for role in ['search_planner', 'research_analyst', 'mvp_architect', 'fallback_architect']:
            prompt = get_system_prompt(role)
            print(f"   - {role}: {len(prompt)} chars")
        
        # Check if PromptTemplates class has expected attributes
        attributes = [attr for attr in dir(PromptTemplates) if not attr.startswith('_')]
        print(f"   PromptTemplates attributes: {len(attributes)}")
        
        return True
    except Exception as e:
        print(f"❌ Prompt templates test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_file_manager():
    """Test file management functionality"""
    print("\n🧪 Testing File Management...")
    try:
        from src.file_manager import get_file_manager
        
        file_mgr = get_file_manager()
        print(f"✅ File manager created: {type(file_mgr)}")
        
        # Test basic functionality
        test_files = {
            "overview_md": "# Test Overview\nThis is a test overview document.",
            "features_md": "# Test Features\n- Feature 1\n- Feature 2",
            "architecture_md": "# Test Architecture\nSystem architecture details."
        }
        
        print("   Testing file operations (in memory)...")
        paths = file_mgr.save_mvp_files(test_files, "Test Idea")
        print(f"   Generated paths: {list(paths.keys())}")
        
        return True
    except Exception as e:
        print(f"❌ File management test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_application_structure():
    """Test overall application structure"""
    print("\n🧪 Testing Application Structure...")
    try:
        import app
        print("✅ App module structure is valid")
        
        # Check if UI components exist
        if hasattr(app, 'demo'):
            print("✅ Gradio interface exists")
        else:
            print("⚠️  Gradio interface not directly accessible")
        
        return True
    except Exception as e:
        print(f"❌ Application structure test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_comprehensive_test():
    """Run all tests"""
    print("🚀 Starting MVP Agent Application Tests\n")
    print("="*50)
    
    tests = [
        ("MCP Server Management", test_mcp_servers),
        ("Core Components", test_core_components),
        ("Prompt Templates", test_prompts),
        ("File Management", test_file_manager),
        ("Application Structure", test_application_structure)
    ]
    
    results = []
    for test_name, test_func in tests:
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "="*50)
    print("📊 TEST RESULTS SUMMARY")
    print("="*50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("\n🎉 All tests passed! The application structure is working correctly.")
        print("\n📝 To run the full application:")
        print("   1. Set your GEMINI_API_KEY in .env file")
        print("   2. Run: python app.py")
        print("   3. Access the UI in your browser")
        return True
    else:
        print(f"\n⚠️  {len(tests) - passed} test(s) failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)
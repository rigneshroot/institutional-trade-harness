"""
Institutional Trade Harness - Zero-Dependency Test Runner
Author: Rignesh P

Executes all unit tests in the tests/ directory without requiring pytest.
"""

import os
import sys
import importlib.util
import inspect

def discover_and_run_tests():
    print("="*60)
    print("RUNNING UNIT TEST SUITE (ZERO-DEPENDENCY RUNNER)")
    print("="*60)
    
    test_dir = "tests"
    if not os.path.exists(test_dir):
        print(f"Error: Test directory '{test_dir}' not found.")
        sys.exit(1)
        
    test_files = [f for f in os.listdir(test_dir) if f.startswith("test_") and f.endswith(".py")]
    
    total_run = 0
    total_passed = 0
    total_failed = 0
    
    # Insert current working dir to path to resolve modular imports
    sys.path.insert(0, os.getcwd())
    
    for file in sorted(test_files):
        module_name = file[:-3]
        file_path = os.path.join(test_dir, file)
        
        print(f"\nRunning tests in {file}...")
        
        try:
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        except Exception as e:
            print(f"  [ERROR] Failed to load module {file}: {e}")
            continue
            
        # Discover functions starting with 'test_'
        test_functions = [obj for name, obj in inspect.getmembers(module) 
                          if inspect.isfunction(obj) and name.startswith("test_")]
        
        for func in test_functions:
            total_run += 1
            try:
                func()
                print(f"  [PASS] {func.__name__}")
                total_passed += 1
            except AssertionError as ae:
                print(f"  [FAIL] {func.__name__} - Assertion Error: {ae}")
                total_failed += 1
            except Exception as e:
                print(f"  [FAIL] {func.__name__} - Unexpected Error: {e}")
                total_failed += 1
                
    print("\n" + "="*60)
    print("TEST EXECUTION SUMMARY")
    print("="*60)
    print(f"Total Tests Run: {total_run}")
    print(f"Passed:          {total_passed}")
    print(f"Failed:          {total_failed}")
    print("="*60)
    
    if total_failed > 0:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    discover_and_run_tests()

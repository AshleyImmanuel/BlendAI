import unittest
import sys
import os

# Ensure backend path is available for the test runner
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def run_all_tests():
    """
    Discovers and executes every test in the BlendAI backend.
    Coverage:
    - Unit Tests (Agent Logic)
    - Integration Tests (FastAPI Routing)
    - System Tests (End-to-End Persistence)
    """
    print("="*60)
    print("BLENDAI MASTER TEST ORCHESTRATOR")
    print("="*60)
    
    # Define the test directory
    test_dir = os.path.join(os.path.dirname(__file__), "tests")
    
    if not os.path.exists(test_dir):
        print(f"ERROR: Test directory not found at {test_dir}")
        sys.exit(1)
        
    # Discover all tests matching 'test_*.py'
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir=test_dir, pattern="test_*.py")
    
    # Run tests with a verbose runner
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "="*60)
    print("FINAL AUDIT SUMMARY")
    print(f"Tests Run: {result.testsRun}")
    print(f"Errors: {len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    
    if result.wasSuccessful():
        print("STATUS: ALL SYSTEMS GREEN. BLENDAI IS PRODUCTION READY.")
        sys.exit(0)
    else:
        print("STATUS: AUDIT FAILED. PLEASE RESOLVE THE ERRORS ABOVE.")
        sys.exit(1)

if __name__ == "__main__":
    run_all_tests()

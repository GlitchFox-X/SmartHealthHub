#!/usr/bin/env python3
"""
Smart Health Hub - Comprehensive Test Suite (Windows)

Run all tests without requiring Arduino or Raspberry Pi hardware.
Usage: python run_tests.py
"""

import sys
import subprocess
from pathlib import Path


def run_test_file(test_file):
    """Run a single test file and return success status."""
    print(f"\n{'='*70}")
    print(f"Running: {test_file.name}")
    print(f"{'='*70}")
    
    result = subprocess.run(
        [sys.executable, str(test_file)],
        cwd=test_file.parent,
        capture_output=False
    )
    
    return result.returncode == 0


def main():
    """Run all tests and report summary."""
    project_root = Path(__file__).parent
    
    print("\n" + "█"*70)
    print("█" + " "*68 + "█")
    print("█" + "  SMART HEALTH HUB - COMPREHENSIVE TEST SUITE (Windows)".center(68) + "█")
    print("█" + " "*68 + "█")
    print("█"*70)
    
    # List of test files to run
    test_files = [
        project_root / "test_database.py",
        project_root / "test_pdf.py",
        project_root / "test_serial.py",
    ]
    
    # Verify test files exist
    missing = [f for f in test_files if not f.exists()]
    if missing:
        print(f"\n✗ Missing test files:")
        for f in missing:
            print(f"  - {f}")
        return 1
    
    # Run each test
    results = {}
    for test_file in test_files:
        test_name = test_file.stem.replace("test_", "").upper()
        success = run_test_file(test_file)
        results[test_name] = success
    
    # Print summary
    print("\n" + "█"*70)
    print("█" + " TEST SUMMARY ".center(68, "=") + "█")
    print("█"*70)
    
    for test_name, success in results.items():
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"  {status}: {test_name}")
    
    total = len(results)
    passed = sum(1 for s in results.values() if s)
    
    print("█"*70)
    print(f"  Result: {passed}/{total} test suites passed")
    print("█"*70)
    
    if passed == total:
        print("\n█"*70)
        print("█" + "  ✓ ALL TESTS PASSED - APPLICATION READY FOR HARDWARE TESTING".center(68) + "█")
        print("█"*70 + "\n")
        return 0
    else:
        print("\n█"*70)
        print("█" + f"  ✗ {total - passed} TEST SUITE(S) FAILED".center(68) + "█")
        print("█"*70 + "\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())

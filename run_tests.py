#!/usr/bin/env python
"""
AAL Project Test Runner
Unified script to run all tests: Python (pytest), JavaScript (Jest), E2E (Playwright)

Usage:
    python run_tests.py              # Run all tests
    python run_tests.py --python     # Run only Python tests
    python run_tests.py --js         # Run only JavaScript tests
    python run_tests.py --e2e        # Run only E2E tests
    python run_tests.py --unit       # Run only unit tests
    python run_tests.py --integration # Run only integration tests
    python run_tests.py --coverage   # Run with coverage report
"""

import subprocess
import sys
import os
import argparse
from pathlib import Path
from datetime import datetime

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    """Print colored header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.END}\n")

def print_success(text):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_error(text):
    """Print error message"""
    print(f"{Colors.RED}✗ {text}{Colors.END}")

def print_info(text):
    """Print info message"""
    print(f"{Colors.BLUE}ℹ {text}{Colors.END}")

def run_python_tests(coverage=False, unit_only=False, integration_only=False):
    """
    Run Python tests using pytest
    
    Args:
        coverage: Whether to generate coverage report
        unit_only: Run only unit tests
        integration_only: Run only integration tests
    
    Returns:
        int: Return code (0 for success)
    """
    print_header("Running Python Tests (pytest)")
    
    cmd = [sys.executable, '-m', 'pytest']
    
    # Add test paths
    test_paths = ['server/tests', 'quote_backend/tests']
    
    # Filter by test type
    if unit_only:
        test_paths = ['server/tests/unit', 'quote_backend/tests/unit']
        cmd.extend(['-m', 'unit or not integration'])
    elif integration_only:
        test_paths = ['server/tests/integration', 'quote_backend/tests/integration']
        cmd.extend(['-m', 'integration'])
    
    cmd.extend(test_paths)
    
    # Add verbosity
    cmd.append('-v')
    
    # Add coverage if requested
    if coverage:
        cmd.extend([
            '--cov=server',
            '--cov=quote_backend',
            '--cov-report=html',
            '--cov-report=term-missing'
        ])
    
    # Add color output
    cmd.append('--color=yes')
    
    print_info(f"Command: {' '.join(cmd)}")
    
    result = subprocess.run(cmd, cwd=Path(__file__).parent)
    
    if result.returncode == 0:
        print_success("Python tests passed!")
    else:
        print_error(f"Python tests failed with code {result.returncode}")
    
    return result.returncode

def run_js_tests(coverage=False):
    """
    Run JavaScript tests using Jest
    
    Args:
        coverage: Whether to generate coverage report
    
    Returns:
        int: Return code (0 for success)
    """
    print_header("Running JavaScript Tests (Jest)")
    
    frontend_dir = Path(__file__).parent / 'frontend'
    
    # Check if node_modules exists
    if not (frontend_dir / 'node_modules').exists():
        print_info("Installing npm dependencies...")
        install_result = subprocess.run(
            ['npm', 'install'],
            cwd=frontend_dir,
            shell=True
        )
        if install_result.returncode != 0:
            print_error("Failed to install npm dependencies")
            return install_result.returncode
    
    cmd = ['npm', 'test']
    
    if coverage:
        cmd.append('--')
        cmd.append('--coverage')
    
    print_info(f"Command: {' '.join(cmd)}")
    
    result = subprocess.run(cmd, cwd=frontend_dir, shell=True)
    
    if result.returncode == 0:
        print_success("JavaScript tests passed!")
    else:
        print_error(f"JavaScript tests failed with code {result.returncode}")
    
    return result.returncode

def run_e2e_tests(headed=False):
    """
    Run E2E tests using Playwright
    
    Args:
        headed: Whether to run in headed mode (visible browser)
    
    Returns:
        int: Return code (0 for success)
    """
    print_header("Running E2E Tests (Playwright)")
    
    e2e_dir = Path(__file__).parent / 'e2e'
    
    # Check if node_modules exists
    if not (e2e_dir / 'node_modules').exists():
        print_info("Installing Playwright dependencies...")
        install_result = subprocess.run(
            ['npm', 'install'],
            cwd=e2e_dir,
            shell=True
        )
        if install_result.returncode != 0:
            print_error("Failed to install Playwright dependencies")
            return install_result.returncode
        
        # Install browsers
        print_info("Installing Playwright browsers...")
        subprocess.run(
            ['npx', 'playwright', 'install', 'chromium'],
            cwd=e2e_dir,
            shell=True
        )
    
    cmd = ['npx', 'playwright', 'test']
    
    if headed:
        cmd.append('--headed')
    
    print_info(f"Command: {' '.join(cmd)}")
    
    result = subprocess.run(cmd, cwd=e2e_dir, shell=True)
    
    if result.returncode == 0:
        print_success("E2E tests passed!")
    else:
        print_error(f"E2E tests failed with code {result.returncode}")
    
    return result.returncode

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='AAL Project Test Runner',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python run_tests.py              # Run all tests
    python run_tests.py --python     # Run only Python tests
    python run_tests.py --js         # Run only JavaScript tests
    python run_tests.py --e2e        # Run only E2E tests
    python run_tests.py --unit       # Run only unit tests
    python run_tests.py --coverage   # Run with coverage report
        """
    )
    
    parser.add_argument('--python', action='store_true', help='Run only Python tests')
    parser.add_argument('--js', action='store_true', help='Run only JavaScript tests')
    parser.add_argument('--e2e', action='store_true', help='Run only E2E tests')
    parser.add_argument('--unit', action='store_true', help='Run only unit tests')
    parser.add_argument('--integration', action='store_true', help='Run only integration tests')
    parser.add_argument('--coverage', action='store_true', help='Generate coverage report')
    parser.add_argument('--headed', action='store_true', help='Run E2E tests in headed mode')
    
    args = parser.parse_args()
    
    # Print start banner
    print(f"\n{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}  AAL Project Test Runner{Colors.END}")
    print(f"{Colors.BOLD}  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.END}")
    print(f"{Colors.BOLD}{'='*60}{Colors.END}")
    
    results = {}
    
    # Determine which tests to run
    run_all = not (args.python or args.js or args.e2e)
    
    # Run Python tests
    if run_all or args.python:
        results['python'] = run_python_tests(
            coverage=args.coverage,
            unit_only=args.unit,
            integration_only=args.integration
        )
    
    # Run JavaScript tests
    if run_all or args.js:
        results['javascript'] = run_js_tests(coverage=args.coverage)
    
    # Run E2E tests
    if run_all or args.e2e:
        results['e2e'] = run_e2e_tests(headed=args.headed)
    
    # Print summary
    print_header("Test Summary")
    
    total_passed = 0
    total_failed = 0
    
    for test_type, return_code in results.items():
        if return_code == 0:
            print_success(f"{test_type.capitalize()} Tests: PASSED")
            total_passed += 1
        else:
            print_error(f"{test_type.capitalize()} Tests: FAILED")
            total_failed += 1
    
    print(f"\n{Colors.BOLD}Total: {total_passed} passed, {total_failed} failed{Colors.END}")
    
    # Return overall exit code
    exit_code = 0 if total_failed == 0 else 1
    
    if exit_code == 0:
        print(f"\n{Colors.GREEN}{Colors.BOLD}All tests passed! ✓{Colors.END}")
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}Some tests failed! ✗{Colors.END}")
    
    return exit_code

if __name__ == '__main__':
    sys.exit(main())

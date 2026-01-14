"""
Minimal validation tests for Graph Mail MCP Server

Tests syntax and basic structure without requiring external dependencies.
"""

import ast
import os
import sys


def test_python_syntax():
    """Verify all Python files have valid syntax"""
    src_dir = os.path.join(os.path.dirname(__file__), 'src')
    files = [
        'config.py',
        'auth.py', 
        'graph_client.py',
        'server.py',
        '__init__.py',
        '__main__.py'
    ]
    
    errors = []
    for filename in files:
        filepath = os.path.join(src_dir, filename)
        try:
            with open(filepath, 'r') as f:
                ast.parse(f.read())
            print(f"✓ {filename}: Valid Python syntax")
        except SyntaxError as e:
            errors.append(f"✗ {filename}: Syntax Error: {e}")
            print(errors[-1])
    
    if errors:
        print(f"\n{len(errors)} file(s) with errors")
        sys.exit(1)
    else:
        print(f"\n✓ All {len(files)} files have valid Python syntax")


def test_design_principles():
    """Verify design principles are followed in code"""
    print("\nDesign Principles Check:")
    
    # Check for immutable data structures (frozen dataclasses)
    graph_client_path = os.path.join(os.path.dirname(__file__), 'src', 'graph_client.py')
    with open(graph_client_path, 'r') as f:
        content = f.read()
        if '@dataclass(frozen=True)' in content:
            print("✓ Using immutable data structures (@dataclass(frozen=True))")
        else:
            print("✗ Missing immutable data structures")
            sys.exit(1)
    
    # Check for separation of actions, calculations, and data
    auth_path = os.path.join(os.path.dirname(__file__), 'src', 'auth.py')
    with open(auth_path, 'r') as f:
        content = f.read()
        if '# Calculations' in content and '# Actions' in content:
            print("✓ Separates Actions and Calculations (Grokking Simplicity)")
        else:
            print("✗ Missing separation of Actions and Calculations")
            sys.exit(1)
    
    # Check for comprehensive logging
    server_path = os.path.join(os.path.dirname(__file__), 'src', 'server.py')
    with open(server_path, 'r') as f:
        content = f.read()
        log_count = content.count('logger.')
        if log_count >= 10:
            print(f"✓ Comprehensive logging ({log_count} log statements)")
        else:
            print(f"✗ Insufficient logging ({log_count} log statements)")
            sys.exit(1)


def test_required_files():
    """Verify all required files exist"""
    print("\nRequired Files Check:")
    
    required_files = [
        'Dockerfile',
        'requirements.txt',
        'pyproject.toml',
        '.python-version',
        'README.md',
        '.env.example',
        'src/__init__.py',
        'src/__main__.py',
        'src/config.py',
        'src/auth.py',
        'src/graph_client.py',
        'src/server.py',
        'test_e2e.py'
    ]
    
    errors = []
    for filename in required_files:
        filepath = os.path.join(os.path.dirname(__file__), filename)
        if os.path.exists(filepath):
            print(f"✓ {filename}: Found")
        else:
            errors.append(f"✗ {filename}: Missing")
            print(errors[-1])
    
    if errors:
        print(f"\n{len(errors)} file(s) missing")
        sys.exit(1)
    else:
        print(f"\n✓ All {len(required_files)} required files present")


def test_dockerfile():
    """Verify Dockerfile has correct structure"""
    print("\nDockerfile Validation:")
    
    dockerfile_path = os.path.join(os.path.dirname(__file__), 'Dockerfile')
    with open(dockerfile_path, 'r') as f:
        content = f.read()
        
        checks = [
            ('FROM python:', 'Uses Python base image'),
            ('COPY pyproject.toml', 'Copies pyproject.toml'),
            ('uv', 'Uses uv package manager'),
            ('EXPOSE 8080', 'Exposes port 8080'),
            ('CMD', 'Has CMD instruction')
        ]
        
        for check, description in checks:
            if check in content:
                print(f"✓ {description}")
            else:
                print(f"✗ Missing: {description}")
                sys.exit(1)


def test_requirements():
    """Verify requirements.txt and pyproject.toml have necessary dependencies"""
    print("\nRequirements Validation:")
    
    # Check requirements.txt
    req_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    with open(req_path, 'r') as f:
        req_content = f.read()
        
        required_deps = [
            ('mcp', 'MCP SDK'),
            ('msal', 'Microsoft Authentication Library'),
            ('httpx', 'HTTP client'),
            ('pydantic', 'Data validation')
        ]
        
        for dep, description in required_deps:
            if dep in req_content:
                print(f"✓ {description} ({dep})")
            else:
                print(f"✗ Missing: {description} ({dep})")
                sys.exit(1)
    
    # Check pyproject.toml
    pyproject_path = os.path.join(os.path.dirname(__file__), 'pyproject.toml')
    if os.path.exists(pyproject_path):
        with open(pyproject_path, 'r') as f:
            pyproject_content = f.read()
            
            if '[project]' in pyproject_content and 'dependencies' in pyproject_content:
                print(f"✓ pyproject.toml configured for uv")
            else:
                print(f"⚠ pyproject.toml exists but may be incomplete")
    else:
        print(f"✗ Missing: pyproject.toml for uv support")
        sys.exit(1)


if __name__ == '__main__':
    print("=" * 60)
    print("Graph Mail MCP Server - Validation Tests")
    print("=" * 60)
    
    test_required_files()
    test_python_syntax()
    test_design_principles()
    test_dockerfile()
    test_requirements()
    
    print("\n" + "=" * 60)
    print("✓ All validation tests passed!")
    print("=" * 60)

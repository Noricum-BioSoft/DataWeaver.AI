#!/usr/bin/env python3
"""
Validate OpenAPI specification files
"""

import yaml
import json
import sys
from pathlib import Path

def validate_yaml_spec():
    """Validate the YAML OpenAPI specification"""
    try:
        with open('docs/openapi.yaml', 'r') as f:
            spec = yaml.safe_load(f)
        
        # Basic validation
        required_fields = ['openapi', 'info', 'paths']
        for field in required_fields:
            if field not in spec:
                print(f"❌ Missing required field: {field}")
                return False
        
        # Check version
        if spec['openapi'] != '3.0.3':
            print(f"❌ Unexpected OpenAPI version: {spec['openapi']}")
            return False
        
        # Check info
        info = spec['info']
        if 'title' not in info or 'version' not in info:
            print("❌ Missing required info fields")
            return False
        
        # Check paths
        if not spec['paths']:
            print("❌ No paths defined")
            return False
        
        print("✅ YAML OpenAPI specification is valid")
        return True
        
    except Exception as e:
        print(f"❌ Error validating YAML spec: {e}")
        return False

def validate_json_spec():
    """Validate the JSON OpenAPI specification"""
    try:
        with open('docs/openapi.json', 'r') as f:
            spec = json.load(f)
        
        # Basic validation
        required_fields = ['openapi', 'info', 'paths']
        for field in required_fields:
            if field not in spec:
                print(f"❌ Missing required field: {field}")
                return False
        
        # Check version
        if spec['openapi'] != '3.0.3':
            print(f"❌ Unexpected OpenAPI version: {spec['openapi']}")
            return False
        
        # Check info
        info = spec['info']
        if 'title' not in info or 'version' not in info:
            print("❌ Missing required info fields")
            return False
        
        # Check paths
        if not spec['paths']:
            print("❌ No paths defined")
            return False
        
        print("✅ JSON OpenAPI specification is valid")
        return True
        
    except Exception as e:
        print(f"❌ Error validating JSON spec: {e}")
        return False

def check_spec_consistency():
    """Check if YAML and JSON specs are consistent"""
    try:
        with open('docs/openapi.yaml', 'r') as f:
            yaml_spec = yaml.safe_load(f)
        
        with open('docs/openapi.json', 'r') as f:
            json_spec = json.load(f)
        
        # Compare key fields
        yaml_paths = set(yaml_spec['paths'].keys())
        json_paths = set(json_spec['paths'].keys())
        
        if yaml_paths != json_paths:
            print("❌ Paths are not consistent between YAML and JSON")
            print(f"YAML paths: {yaml_paths}")
            print(f"JSON paths: {json_paths}")
            return False
        
        print("✅ YAML and JSON specifications are consistent")
        return True
        
    except Exception as e:
        print(f"❌ Error checking consistency: {e}")
        return False

def main():
    """Main validation function"""
    print("🔍 Validating OpenAPI specifications...")
    print()
    
    # Check if files exist
    yaml_path = Path('docs/openapi.yaml')
    json_path = Path('docs/openapi.json')
    
    if not yaml_path.exists():
        print("❌ docs/openapi.yaml not found")
        return False
    
    if not json_path.exists():
        print("❌ docs/openapi.json not found")
        return False
    
    # Validate specifications
    yaml_valid = validate_yaml_spec()
    json_valid = validate_json_spec()
    consistent = check_spec_consistency()
    
    print()
    if yaml_valid and json_valid and consistent:
        print("🎉 All OpenAPI specifications are valid and consistent!")
        return True
    else:
        print("❌ OpenAPI validation failed")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1) 
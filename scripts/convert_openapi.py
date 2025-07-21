#!/usr/bin/env python3
"""
Convert YAML OpenAPI specification to JSON format
"""

import yaml
import json
import sys
from pathlib import Path

def convert_yaml_to_json():
    """Convert YAML OpenAPI spec to JSON"""
    try:
        # Read YAML file
        with open('docs/openapi.yaml', 'r') as f:
            yaml_spec = yaml.safe_load(f)
        
        # Write JSON file
        with open('docs/openapi.json', 'w') as f:
            json.dump(yaml_spec, f, indent=2, default=str)
        
        print("✅ Successfully converted YAML to JSON")
        return True
        
    except Exception as e:
        print(f"❌ Error converting YAML to JSON: {e}")
        return False

def main():
    """Main conversion function"""
    print("🔄 Converting OpenAPI YAML to JSON...")
    
    # Check if YAML file exists
    yaml_path = Path('docs/openapi.yaml')
    if not yaml_path.exists():
        print("❌ docs/openapi.yaml not found")
        return False
    
    # Convert
    success = convert_yaml_to_json()
    
    if success:
        print("✅ Conversion completed successfully!")
        return True
    else:
        print("❌ Conversion failed")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1) 
#!/usr/bin/env python3
"""
Generate test files and datasets for DataWeaver.AI testing
"""

import csv
import json
import random
import string
from datetime import datetime, timedelta
from pathlib import Path
import os

def generate_random_string(length=8):
    """Generate a random string"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def generate_customer_data():
    """Generate customer data CSV"""
    customers = []
    for i in range(1, 101):
        customer = {
            'customer_id': f'CUST{i:03d}',
            'name': f'Customer {i}',
            'email': f'customer{i}@example.com',
            'phone': f'+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}',
            'city': random.choice(['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix']),
            'state': random.choice(['NY', 'CA', 'IL', 'TX', 'AZ']),
            'zip_code': f'{random.randint(10000, 99999)}',
            'registration_date': (datetime.now() - timedelta(days=random.randint(1, 365))).strftime('%Y-%m-%d'),
            'total_orders': random.randint(1, 50),
            'total_spent': round(random.uniform(100, 5000), 2)
        }
        customers.append(customer)
    
    return customers

def generate_sales_data():
    """Generate sales data CSV"""
    sales = []
    for i in range(1, 201):
        sale = {
            'order_id': f'ORD{i:04d}',
            'customer_id': f'CUST{random.randint(1, 100):03d}',
            'product_id': f'PROD{random.randint(1, 50):03d}',
            'product_name': f'Product {random.randint(1, 50)}',
            'quantity': random.randint(1, 10),
            'unit_price': round(random.uniform(10, 500), 2),
            'total_price': 0,  # Will be calculated
            'order_date': (datetime.now() - timedelta(days=random.randint(1, 365))).strftime('%Y-%m-%d'),
            'payment_method': random.choice(['Credit Card', 'Debit Card', 'PayPal', 'Cash']),
            'status': random.choice(['Completed', 'Pending', 'Cancelled'])
        }
        sale['total_price'] = sale['quantity'] * sale['unit_price']
        sales.append(sale)
    
    return sales

def generate_product_data():
    """Generate product data CSV"""
    products = []
    categories = ['Electronics', 'Clothing', 'Books', 'Home & Garden', 'Sports']
    
    for i in range(1, 51):
        product = {
            'product_id': f'PROD{i:03d}',
            'name': f'Product {i}',
            'category': random.choice(categories),
            'description': f'Description for product {i}',
            'price': round(random.uniform(10, 500), 2),
            'cost': round(random.uniform(5, 250), 2),
            'stock_quantity': random.randint(0, 100),
            'supplier_id': f'SUPP{random.randint(1, 20):02d}',
            'created_date': (datetime.now() - timedelta(days=random.randint(1, 365))).strftime('%Y-%m-%d'),
            'is_active': random.choice([True, False])
        }
        products.append(product)
    
    return products

def generate_employee_data():
    """Generate employee data CSV"""
    employees = []
    departments = ['Engineering', 'Sales', 'Marketing', 'HR', 'Finance', 'Operations']
    positions = ['Manager', 'Senior', 'Junior', 'Lead', 'Associate']
    
    for i in range(1, 51):
        employee = {
            'employee_id': f'EMP{i:03d}',
            'first_name': f'Employee{i}',
            'last_name': f'Last{i}',
            'email': f'employee{i}@company.com',
            'department': random.choice(departments),
            'position': random.choice(positions),
            'hire_date': (datetime.now() - timedelta(days=random.randint(30, 1095))).strftime('%Y-%m-%d'),
            'salary': random.randint(30000, 150000),
            'manager_id': f'EMP{random.randint(1, 10):03d}' if i > 10 else '',
            'location': random.choice(['HQ', 'Remote', 'Branch A', 'Branch B']),
            'is_active': random.choice([True, False])
        }
        employees.append(employee)
    
    return employees

def generate_inventory_data():
    """Generate inventory data CSV"""
    inventory = []
    warehouses = ['Warehouse A', 'Warehouse B', 'Warehouse C']
    
    for i in range(1, 101):
        item = {
            'item_id': f'ITEM{i:04d}',
            'product_id': f'PROD{random.randint(1, 50):03d}',
            'warehouse_id': random.choice(warehouses),
            'quantity': random.randint(0, 1000),
            'min_quantity': random.randint(10, 50),
            'max_quantity': random.randint(200, 1000),
            'last_updated': (datetime.now() - timedelta(days=random.randint(1, 30))).strftime('%Y-%m-%d'),
            'status': random.choice(['In Stock', 'Low Stock', 'Out of Stock', 'On Order']),
            'location': f'Aisle {random.randint(1, 20)}-{random.randint(1, 10)}',
            'cost_per_unit': round(random.uniform(5, 100), 2)
        }
        inventory.append(item)
    
    return inventory

def generate_website_analytics():
    """Generate website analytics data CSV"""
    analytics = []
    pages = ['/home', '/products', '/about', '/contact', '/blog', '/cart']
    sources = ['Google', 'Direct', 'Social Media', 'Email', 'Referral']
    
    for i in range(1, 1001):
        date = datetime.now() - timedelta(days=random.randint(1, 30))
        for hour in range(24):
            for _ in range(random.randint(1, 5)):  # Multiple records per hour
                record = {
                    'timestamp': date.replace(hour=hour).strftime('%Y-%m-%d %H:%M:%S'),
                    'page_url': random.choice(pages),
                    'visitor_id': f'VIS{random.randint(1, 1000):04d}',
                    'session_id': f'SESS{random.randint(1, 10000):05d}',
                    'source': random.choice(sources),
                    'device_type': random.choice(['Desktop', 'Mobile', 'Tablet']),
                    'browser': random.choice(['Chrome', 'Safari', 'Firefox', 'Edge']),
                    'country': random.choice(['US', 'CA', 'UK', 'DE', 'FR', 'JP']),
                    'time_on_page': random.randint(10, 600),
                    'bounce_rate': random.uniform(0, 1)
                }
                analytics.append(record)
    
    return analytics

def generate_biological_data():
    """Generate biological/assay data CSV"""
    assays = []
    assay_types = ['Activity', 'Binding', 'Toxicity', 'Stability', 'Expression']
    compounds = [f'Compound_{i:03d}' for i in range(1, 101)]
    
    for i in range(1, 201):
        assay = {
            'assay_id': f'ASSAY{i:04d}',
            'compound_id': random.choice(compounds),
            'assay_type': random.choice(assay_types),
            'concentration': round(random.uniform(0.1, 100), 3),
            'result_value': round(random.uniform(0, 100), 2),
            'unit': random.choice(['%', 'nM', 'μM', 'mM', 'IC50']),
            'technician': f'Tech_{random.randint(1, 10):02d}',
            'date_run': (datetime.now() - timedelta(days=random.randint(1, 365))).strftime('%Y-%m-%d'),
            'plate_id': f'PLATE{random.randint(1, 50):03d}',
            'well_position': f'{chr(65 + random.randint(0, 7))}{random.randint(1, 12)}',
            'quality_score': round(random.uniform(0.5, 1.0), 2),
            'notes': f'Test run {i}'
        }
        assays.append(assay)
    
    return assays

def generate_sequence_data():
    """Generate protein/DNA sequence data CSV"""
    sequences = []
    amino_acids = 'ACDEFGHIKLMNPQRSTVWY'
    nucleotides = 'ATCG'
    
    for i in range(1, 51):
        # Generate random protein sequence
        protein_seq = ''.join(random.choices(amino_acids, k=random.randint(50, 300)))
        # Generate random DNA sequence
        dna_seq = ''.join(random.choices(nucleotides, k=random.randint(100, 1000)))
        
        # Choose sequence type and corresponding sequence
        seq_type = random.choice(['Protein', 'DNA', 'RNA'])
        if seq_type == 'Protein':
            chosen_seq = protein_seq
        else:
            chosen_seq = dna_seq
        
        sequence = {
            'sequence_id': f'SEQ{i:03d}',
            'name': f'Sequence_{i}',
            'type': seq_type,
            'sequence': chosen_seq,
            'length': len(chosen_seq),
            'organism': random.choice(['Human', 'Mouse', 'Rat', 'E. coli', 'Yeast']),
            'accession': f'ACC{random.randint(100000, 999999)}',
            'created_date': (datetime.now() - timedelta(days=random.randint(1, 365))).strftime('%Y-%m-%d'),
            'description': f'Description for sequence {i}',
            'tags': ','.join(random.sample(['kinase', 'receptor', 'enzyme', 'transporter'], random.randint(1, 3)))
        }
        sequences.append(sequence)
    
    return sequences

def generate_json_dataset():
    """Generate a JSON dataset"""
    data = {
        'metadata': {
            'dataset_name': 'Test JSON Dataset',
            'created_date': datetime.now().isoformat(),
            'version': '1.0',
            'description': 'A test JSON dataset for DataWeaver'
        },
        'users': [
            {
                'id': i,
                'name': f'User {i}',
                'email': f'user{i}@example.com',
                'preferences': {
                    'theme': random.choice(['light', 'dark']),
                    'language': random.choice(['en', 'es', 'fr']),
                    'notifications': random.choice([True, False])
                },
                'stats': {
                    'login_count': random.randint(1, 100),
                    'last_login': (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat()
                }
            }
            for i in range(1, 21)
        ],
        'configurations': {
            'max_file_size': 10485760,
            'allowed_formats': ['csv', 'json', 'xlsx'],
            'auto_backup': True,
            'retention_days': 30
        }
    }
    return data

def write_csv_file(data, filename):
    """Write data to CSV file"""
    if not data:
        return
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = data[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

def write_json_file(data, filename):
    """Write data to JSON file"""
    with open(filename, 'w', encoding='utf-8') as jsonfile:
        json.dump(data, jsonfile, indent=2, default=str)

def main():
    """Generate all test files"""
    # Create test data directory
    test_data_dir = Path('test_data')
    test_data_dir.mkdir(exist_ok=True)
    
    print("Generating test files...")
    
    # Generate and write CSV files
    datasets = [
        ('customers.csv', generate_customer_data()),
        ('sales.csv', generate_sales_data()),
        ('products.csv', generate_product_data()),
        ('employees.csv', generate_employee_data()),
        ('inventory.csv', generate_inventory_data()),
        ('website_analytics.csv', generate_website_analytics()),
        ('biological_assays.csv', generate_biological_data()),
        ('sequences.csv', generate_sequence_data())
    ]
    
    for filename, data in datasets:
        filepath = test_data_dir / filename
        write_csv_file(data, filepath)
        print(f"Generated {filename} with {len(data)} records")
    
    # Generate JSON file
    json_data = generate_json_dataset()
    json_filepath = test_data_dir / 'test_dataset.json'
    write_json_file(json_data, json_filepath)
    print(f"Generated test_dataset.json")
    
    # Create a README file
    readme_content = """# Test Data Files

This directory contains test files and datasets for DataWeaver.AI testing.

## CSV Files

1. **customers.csv** - Customer information with IDs, contact details, and purchase history
2. **sales.csv** - Sales transactions with order details and pricing
3. **products.csv** - Product catalog with categories and pricing
4. **employees.csv** - Employee directory with departments and positions
5. **inventory.csv** - Inventory tracking with warehouse locations
6. **website_analytics.csv** - Website traffic and user behavior data
7. **biological_assays.csv** - Laboratory assay results and experimental data
8. **sequences.csv** - Protein/DNA sequences with metadata

## JSON Files

1. **test_dataset.json** - Structured JSON data with nested objects and arrays

## Usage

These files can be used to test:
- File upload functionality
- Data processing workflows
- Data merging and analysis
- Visualization features
- Workflow creation and execution

## File Sizes

- CSV files: 100-1000 records each
- JSON file: ~20KB with nested structure

All files are generated with realistic but synthetic data for testing purposes.
"""
    
    readme_filepath = test_data_dir / 'README.md'
    with open(readme_filepath, 'w') as f:
        f.write(readme_content)
    
    print(f"\nGenerated {len(datasets) + 1} test files in {test_data_dir}/")
    print("Files are ready for testing the DataWeaver frontend!")

if __name__ == '__main__':
    main() 
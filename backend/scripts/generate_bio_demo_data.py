#!/usr/bin/env python3
"""
Generate example CSV files for Bio-Matcher demo.

This script creates two CSV files:
1. sequences.csv - Contains ID, Sequence, Mutation columns with 96 rows
2. measurements.csv - Contains ID and 3 measurement columns with matching IDs
"""

import csv
import uuid
import random
import string
from typing import List, Tuple
import os

# Amino acid codes
AMINO_ACIDS = "ACDEFGHIKLMNPQRSTVWY"

def generate_random_protein_sequence(length: int = 150) -> str:
    """Generate a random protein sequence of given length."""
    return ''.join(random.choice(AMINO_ACIDS) for _ in range(length))

def generate_mutations(parent_sequence: str, num_mutations: int = 95) -> List[Tuple[str, str, str]]:
    """Generate mutations of the parent sequence."""
    mutations = []
    
    for i in range(num_mutations):
        # Generate unique ID
        sequence_id = str(uuid.uuid4())
        
        # Create a copy of parent sequence
        mutated_sequence = list(parent_sequence)
        
        # Generate 1-3 random mutations
        num_changes = random.randint(1, 3)
        mutation_descriptions = []
        
        for _ in range(num_changes):
            # Random position
            pos = random.randint(0, len(parent_sequence) - 1)
            # Random new amino acid
            new_aa = random.choice(AMINO_ACIDS)
            
            # Update sequence
            mutated_sequence[pos] = new_aa
            
            # Create mutation description (e.g., "A15G" for position 15, A->G)
            old_aa = parent_sequence[pos]
            mutation_desc = f"{old_aa}{pos+1}{new_aa}"
            mutation_descriptions.append(mutation_desc)
        
        # Join multiple mutations with comma
        mutation_str = ",".join(mutation_descriptions)
        mutations.append((sequence_id, ''.join(mutated_sequence), mutation_str))
    
    return mutations

def generate_measurements(sequence_ids: List[str]) -> List[Tuple[str, float, float, float]]:
    """Generate measurement data for each sequence ID."""
    measurements = []
    
    for seq_id in sequence_ids:
        # Generate 3 random measurements between 0 and 1
        measurement1 = round(random.uniform(0, 1), 4)
        measurement2 = round(random.uniform(0, 1), 4)
        measurement3 = round(random.uniform(0, 1), 4)
        
        measurements.append((seq_id, measurement1, measurement2, measurement3))
    
    return measurements

def create_sequences_csv(filename: str = "sequences.csv"):
    """Create the sequences CSV file."""
    print(f"Generating {filename}...")
    
    # Generate parent sequence
    parent_sequence = generate_random_protein_sequence(150)
    parent_id = str(uuid.uuid4())
    
    # Generate mutations
    mutations = generate_mutations(parent_sequence, 95)
    
    # Write to CSV
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        
        # Write header
        writer.writerow(['ID', 'Sequence', 'Mutation'])
        
        # Write parent sequence (first row)
        writer.writerow([parent_id, parent_sequence, ''])
        
        # Write mutations
        for seq_id, sequence, mutation in mutations:
            writer.writerow([seq_id, sequence, mutation])
    
    print(f"✓ Created {filename} with {len(mutations) + 1} rows")
    return [parent_id] + [seq_id for seq_id, _, _ in mutations]

def create_measurements_csv(sequence_ids: List[str], filename: str = "measurements.csv"):
    """Create the measurements CSV file."""
    print(f"Generating {filename}...")
    
    # Generate measurements
    measurements = generate_measurements(sequence_ids)
    
    # Write to CSV
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        
        # Write header
        writer.writerow(['ID', 'Activity_Score', 'Stability_Index', 'Expression_Level'])
        
        # Write measurements
        for seq_id, m1, m2, m3 in measurements:
            writer.writerow([seq_id, m1, m2, m3])
    
    print(f"✓ Created {filename} with {len(measurements)} rows")

def main():
    """Main function to generate both CSV files."""
    print("🚀 Generating Bio-Matcher Demo Data...")
    print("=" * 50)
    
    # Create output directory if it doesn't exist
    output_dir = "sample_data"
    os.makedirs(output_dir, exist_ok=True)
    
    # Change to output directory
    os.chdir(output_dir)
    
    # Generate sequences file
    sequence_ids = create_sequences_csv("sequences.csv")
    
    # Generate measurements file
    create_measurements_csv(sequence_ids, "measurements.csv")
    
    print("\n" + "=" * 50)
    print("✅ Demo data generation complete!")
    print(f"📁 Files created in: {os.path.abspath('.')}")
    print("📊 sequences.csv: 96 rows (1 parent + 95 mutations)")
    print("📊 measurements.csv: 96 rows (matching IDs)")
    print("\n🎯 Ready for Bio-Matcher demo!")

if __name__ == "__main__":
    main() 
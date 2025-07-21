#!/usr/bin/env python3
"""
Generate test files for bio data merging in DataWeaver.AI
"""
import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

random.seed(42)

# 1. Protein/DNA Sequences
sequences = []
for i in range(1, 21):
    seq_id = f"P{i:04d}"
    seq_type = random.choice(["Protein", "DNA"])
    if seq_type == "Protein":
        sequence = ''.join(random.choices("ACDEFGHIKLMNPQRSTVWY", k=random.randint(80, 200)))
    else:
        sequence = ''.join(random.choices("ATCG", k=random.randint(200, 1000)))
    sequences.append({
        "protein_id": seq_id,
        "name": f"Protein_{i}",
        "type": seq_type,
        "sequence": sequence,
        "organism": random.choice(["Human", "Mouse", "Yeast", "E. coli"]),
        "created": (datetime.now() - timedelta(days=random.randint(1, 1000))).strftime('%Y-%m-%d')
    })

# 2. Protein Expression Data
expression = []
for seq in sequences:
    for cond in ["Control", "Treated"]:
        expression.append({
            "protein_id": seq["protein_id"],
            "condition": cond,
            "expression_level": round(random.uniform(0.5, 10.0), 2),
            "replicate": random.randint(1, 3)
        })

# 3. Protein Abundance Data
abundance = []
for seq in sequences:
    abundance.append({
        "protein_id": seq["protein_id"],
        "sample": random.choice(["Liver", "Brain", "Heart", "Muscle"]),
        "abundance": round(random.uniform(100, 10000), 1),
        "unit": "ng/mg"
    })

# 4. SPR Binding Data
spr = []
for seq in sequences:
    for analyte in ["LigandA", "LigandB"]:
        spr.append({
            "protein_id": seq["protein_id"],
            "analyte": analyte,
            "kon": round(random.uniform(1e4, 1e6), 2),
            "koff": round(random.uniform(1e-4, 1e-2), 5),
            "KD": round(random.uniform(1e-9, 1e-6), 10),
            "RU_max": round(random.uniform(100, 1000), 1)
        })

# Write files
data_dir = Path("test_data")
data_dir.mkdir(exist_ok=True)

def write_csv(filename, rows, fieldnames):
    with open(data_dir / filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

write_csv("protein_sequences.csv", sequences, ["protein_id", "name", "type", "sequence", "organism", "created"])
write_csv("protein_expression.csv", expression, ["protein_id", "condition", "expression_level", "replicate"])
write_csv("protein_abundance.csv", abundance, ["protein_id", "sample", "abundance", "unit"])
write_csv("protein_spr.csv", spr, ["protein_id", "analyte", "kon", "koff", "KD", "RU_max"])

print("Test files generated in test_data/:\n- protein_sequences.csv\n- protein_expression.csv\n- protein_abundance.csv\n- protein_spr.csv") 
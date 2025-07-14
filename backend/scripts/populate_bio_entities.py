#!/usr/bin/env python3
"""
Script to populate the database with sample biological entities
for testing the Design-Build-Test workflow system.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.database import get_db
from models.bio_entities import Design, Build, Test
import uuid


def create_sample_designs(db: Session):
    """Create sample Design entities"""
    
    # Parent design (wild type)
    wt_design = Design(
        id=uuid.uuid4(),
        name="Wild Type Enzyme",
        alias="WT_Control",
        description="Wild type enzyme sequence",
        sequence="MGT...L72...K",  # Simplified sequence
        sequence_type="protein",
        mutation_list="",
        parent_design_id=None,
        generation=0
    )
    db.add(wt_design)
    db.flush()  # Flush to get the ID
    
    # L72F mutant design
    l72f_design = Design(
        id=uuid.uuid4(),
        name="L72F Mutant",
        alias="Clone_7",
        description="L72F mutation for improved activity",
        sequence="MGT...L72F...K",
        sequence_type="protein",
        mutation_list="L72F",
        parent_design_id=wt_design.id,
        generation=1
    )
    db.add(l72f_design)
    db.flush()
    
    # R80K mutant design
    r80k_design = Design(
        id=uuid.uuid4(),
        name="R80K Mutant",
        alias="Mutant_A",
        description="R80K mutation for stability",
        sequence="MGT...R80K...K",
        sequence_type="protein",
        mutation_list="R80K",
        parent_design_id=wt_design.id,
        generation=1
    )
    db.add(r80k_design)
    db.flush()
    
    # Double mutant design
    double_mutant_design = Design(
        id=uuid.uuid4(),
        name="L72F-R80K Double Mutant",
        alias="Double_Mutant",
        description="Combined L72F and R80K mutations",
        sequence="MGT...L72F...R80K...K",
        sequence_type="protein",
        mutation_list="L72F,R80K",
        parent_design_id=wt_design.id,
        generation=1
    )
    db.add(double_mutant_design)
    db.flush()
    
    # Triple mutant design
    triple_mutant_design = Design(
        id=uuid.uuid4(),
        name="L72F-R80K-E120A Triple Mutant",
        alias="Clone_12",
        description="Triple mutation for enhanced properties",
        sequence="MGT...L72F...R80K...E120A...K",
        sequence_type="protein",
        mutation_list="L72F,R80K,E120A",
        parent_design_id=wt_design.id,
        generation=1
    )
    db.add(triple_mutant_design)
    
    return {
        'wt_design': wt_design,
        'l72f_design': l72f_design,
        'r80k_design': r80k_design,
        'double_mutant_design': double_mutant_design,
        'triple_mutant_design': triple_mutant_design
    }


def create_sample_builds(db: Session, designs):
    """Create sample Build entities"""
    
    # Build for WT design
    wt_build = Build(
        id=uuid.uuid4(),
        name="WT Plasmid Construct",
        alias="WT_Build_1",
        description="Plasmid construct for wild type enzyme",
        sequence="MGT...L72...K",
        sequence_type="protein",
        mutation_list="",
        parent_build_id=None,
        design_id=designs['wt_design'].id,
        construct_type="plasmid",
        build_status="completed",
        generation=0
    )
    db.add(wt_build)
    db.flush()
    
    # Build for L72F design
    l72f_build = Build(
        id=uuid.uuid4(),
        name="L72F Plasmid Construct",
        alias="L72F_Build_1",
        description="Plasmid construct for L72F mutant",
        sequence="MGT...L72F...K",
        sequence_type="protein",
        mutation_list="L72F",
        parent_build_id=wt_build.id,
        design_id=designs['l72f_design'].id,
        construct_type="plasmid",
        build_status="completed",
        generation=1
    )
    db.add(l72f_build)
    db.flush()
    
    # Build for R80K design
    r80k_build = Build(
        id=uuid.uuid4(),
        name="R80K Plasmid Construct",
        alias="R80K_Build_1",
        description="Plasmid construct for R80K mutant",
        sequence="MGT...R80K...K",
        sequence_type="protein",
        mutation_list="R80K",
        parent_build_id=wt_build.id,
        design_id=designs['r80k_design'].id,
        construct_type="plasmid",
        build_status="completed",
        generation=1
    )
    db.add(r80k_build)
    db.flush()
    
    # Build for double mutant design
    double_mutant_build = Build(
        id=uuid.uuid4(),
        name="L72F-R80K Plasmid Construct",
        alias="Double_Mutant_Build_1",
        description="Plasmid construct for double mutant",
        sequence="MGT...L72F...R80K...K",
        sequence_type="protein",
        mutation_list="L72F,R80K",
        parent_build_id=wt_build.id,
        design_id=designs['double_mutant_design'].id,
        construct_type="plasmid",
        build_status="completed",
        generation=1
    )
    db.add(double_mutant_build)
    db.flush()
    
    # Build for triple mutant design
    triple_mutant_build = Build(
        id=uuid.uuid4(),
        name="L72F-R80K-E120A Plasmid Construct",
        alias="Triple_Mutant_Build_1",
        description="Plasmid construct for triple mutant",
        sequence="MGT...L72F...R80K...E120A...K",
        sequence_type="protein",
        mutation_list="L72F,R80K,E120A",
        parent_build_id=wt_build.id,
        design_id=designs['triple_mutant_design'].id,
        construct_type="plasmid",
        build_status="completed",
        generation=1
    )
    db.add(triple_mutant_build)
    
    return {
        'wt_build': wt_build,
        'l72f_build': l72f_build,
        'r80k_build': r80k_build,
        'double_mutant_build': double_mutant_build,
        'triple_mutant_build': triple_mutant_build
    }


def create_sample_tests(db: Session, designs, builds):
    """Create sample Test entities"""
    
    # Test for WT
    wt_test = Test(
        id=uuid.uuid4(),
        name="WT Activity Test",
        alias="WT_Activity_1",
        description="Activity test for wild type enzyme",
        test_type="activity",
        assay_name="Enzyme Activity Assay",
        protocol="Standard activity protocol",
        result_value=15.0,
        result_unit="μM/min",
        result_type="raw",
        design_id=designs['wt_design'].id,
        build_id=builds['wt_build'].id,
        match_confidence="high",
        match_method="sequence",
        match_score=1.0,
        technician="Dr. Smith"
    )
    db.add(wt_test)
    
    # Test for L72F
    l72f_test = Test(
        id=uuid.uuid4(),
        name="L72F Activity Test",
        alias="L72F_Activity_1",
        description="Activity test for L72F mutant",
        test_type="activity",
        assay_name="Enzyme Activity Assay",
        protocol="Standard activity protocol",
        result_value=25.0,
        result_unit="μM/min",
        result_type="raw",
        design_id=designs['l72f_design'].id,
        build_id=builds['l72f_build'].id,
        match_confidence="high",
        match_method="sequence",
        match_score=1.0,
        technician="Dr. Smith"
    )
    db.add(l72f_test)
    
    # Test for R80K
    r80k_test = Test(
        id=uuid.uuid4(),
        name="R80K Activity Test",
        alias="R80K_Activity_1",
        description="Activity test for R80K mutant",
        test_type="activity",
        assay_name="Enzyme Activity Assay",
        protocol="Standard activity protocol",
        result_value=8.5,
        result_unit="μM/min",
        result_type="raw",
        design_id=designs['r80k_design'].id,
        build_id=builds['r80k_build'].id,
        match_confidence="high",
        match_method="sequence",
        match_score=1.0,
        technician="Dr. Smith"
    )
    db.add(r80k_test)
    
    # Test for double mutant
    double_mutant_test = Test(
        id=uuid.uuid4(),
        name="Double Mutant Activity Test",
        alias="Double_Mutant_Activity_1",
        description="Activity test for double mutant",
        test_type="activity",
        assay_name="Enzyme Activity Assay",
        protocol="Standard activity protocol",
        result_value=2.1,
        result_unit="μM/min",
        result_type="raw",
        design_id=designs['double_mutant_design'].id,
        build_id=builds['double_mutant_build'].id,
        match_confidence="high",
        match_method="sequence",
        match_score=1.0,
        technician="Dr. Smith"
    )
    db.add(double_mutant_test)
    
    # Test for triple mutant
    triple_mutant_test = Test(
        id=uuid.uuid4(),
        name="Triple Mutant Activity Test",
        alias="Triple_Mutant_Activity_1",
        description="Activity test for triple mutant",
        test_type="activity",
        assay_name="Enzyme Activity Assay",
        protocol="Standard activity protocol",
        result_value=0.8,
        result_unit="μM/min",
        result_type="raw",
        design_id=designs['triple_mutant_design'].id,
        build_id=builds['triple_mutant_build'].id,
        match_confidence="high",
        match_method="sequence",
        match_score=1.0,
        technician="Dr. Johnson"
    )
    db.add(triple_mutant_test)


def main():
    """Main function to populate the database"""
    print("Populating database with sample biological entities...")
    
    # Get database session
    db = next(get_db())
    
    try:
        # Create sample designs
        print("Creating sample designs...")
        designs = create_sample_designs(db)
        
        # Create sample builds
        print("Creating sample builds...")
        builds = create_sample_builds(db, designs)
        
        # Create sample tests
        print("Creating sample tests...")
        create_sample_tests(db, designs, builds)
        
        # Commit all changes
        db.commit()
        
        print("Database populated successfully!")
        print(f"Created {len(designs)} designs, {len(builds)} builds, and 5 tests")
        
        # Print some sample data
        print("\nSample Design IDs:")
        for name, design in designs.items():
            print(f"  {name}: {design.id}")
        
    except Exception as e:
        print(f"Error populating database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main() 
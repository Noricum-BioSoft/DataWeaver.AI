from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, Boolean, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid
import hashlib
from .base import Base


class Design(Base):
    """Biological design entity - represents the initial design concept"""
    __tablename__ = "designs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    alias = Column(String(255), nullable=True, index=True)
    description = Column(Text, nullable=True)
    
    # Biological data
    sequence = Column(Text, nullable=False, index=True)
    sequence_type = Column(String(50), nullable=False, default='protein')  # 'protein' or 'dna'
    mutation_list = Column(Text, nullable=True)  # JSON string of mutations
    parent_design_id = Column(UUID(as_uuid=True), ForeignKey('designs.id'), nullable=True)
    
    # Lineage tracking
    lineage_hash = Column(String(64), nullable=False, index=True)
    generation = Column(Integer, default=0)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    
    # Relationships
    parent = relationship("Design", remote_side=[id], backref="children")
    builds = relationship("Build", back_populates="design")
    tests = relationship("Test", back_populates="design")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._compute_lineage_hash()
    
    def _compute_lineage_hash(self):
        """Compute lineage hash based on parent and mutations"""
        if self.parent_design_id:
            parent_hash = self.parent.lineage_hash if self.parent else ""
        else:
            parent_hash = ""
        
        mutation_str = self.mutation_list or ""
        content = f"{parent_hash}:{mutation_str}:{self.sequence}"
        self.lineage_hash = hashlib.sha256(content.encode()).hexdigest()
    
    def add_mutation(self, mutation):
        """Add a mutation to the design"""
        mutations = self.get_mutations()
        if mutation not in mutations:
            mutations.append(mutation)
            self.mutation_list = ",".join(mutations)
            self._compute_lineage_hash()
    
    def get_mutations(self):
        """Get list of mutations"""
        if not self.mutation_list:
            return []
        return [m.strip() for m in self.mutation_list.split(",") if m.strip()]


class Build(Base):
    """Biological build entity - represents a physical construct"""
    __tablename__ = "builds"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    alias = Column(String(255), nullable=True, index=True)
    description = Column(Text, nullable=True)
    
    # Biological data
    sequence = Column(Text, nullable=False, index=True)
    sequence_type = Column(String(50), nullable=False, default='protein')
    mutation_list = Column(Text, nullable=True)
    parent_build_id = Column(UUID(as_uuid=True), ForeignKey('builds.id'), nullable=True)
    
    # Design relationship
    design_id = Column(UUID(as_uuid=True), ForeignKey('designs.id'), nullable=False)
    
    # Lineage tracking
    lineage_hash = Column(String(64), nullable=False, index=True)
    generation = Column(Integer, default=0)
    
    # Build metadata
    construct_type = Column(String(100), nullable=True, default='plasmid')  # 'plasmid', 'protein', etc.
    build_status = Column(String(50), default='planned')  # 'planned', 'in_progress', 'completed', 'failed'
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    
    # Relationships
    parent = relationship("Build", remote_side=[id], backref="children")
    design = relationship("Design", back_populates="builds")
    tests = relationship("Test", back_populates="build")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._compute_lineage_hash()
    
    def _compute_lineage_hash(self):
        """Compute lineage hash based on parent and mutations"""
        if self.parent_build_id:
            parent_hash = self.parent.lineage_hash if self.parent else ""
        else:
            parent_hash = ""
        
        mutation_str = self.mutation_list or ""
        content = f"{parent_hash}:{mutation_str}:{self.sequence}"
        self.lineage_hash = hashlib.sha256(content.encode()).hexdigest()


class Test(Base):
    """Biological test entity - represents assay results"""
    __tablename__ = "tests"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    alias = Column(String(255), nullable=True, index=True)
    description = Column(Text, nullable=True)
    
    # Test metadata
    test_type = Column(String(100), nullable=False)  # 'activity', 'stability', 'expression', etc.
    assay_name = Column(String(255), nullable=True)
    protocol = Column(String(255), nullable=True)
    
    # Results
    result_value = Column(Float, nullable=True)
    result_unit = Column(String(50), nullable=True)
    result_type = Column(String(50), nullable=True)  # 'raw', 'normalized', 'fold_change'
    
    # Confidence and matching
    match_confidence = Column(String(20), nullable=True, default='none')  # 'high', 'medium', 'low', 'none'
    match_method = Column(String(100), nullable=True, default='none')  # 'sequence', 'mutation', 'alias', 'inferred', 'none'
    match_score = Column(Float, nullable=True, default=0.0)  # 0.0 to 1.0
    
    # Relationships
    design_id = Column(UUID(as_uuid=True), ForeignKey('designs.id'), nullable=True)
    build_id = Column(UUID(as_uuid=True), ForeignKey('builds.id'), nullable=True)
    
    # Test metadata
    test_date = Column(DateTime(timezone=True), nullable=True)
    technician = Column(String(255), nullable=True)
    lab_conditions = Column(Text, nullable=True)  # JSON string
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    
    # Relationships
    design = relationship("Design", back_populates="tests")
    build = relationship("Build", back_populates="tests")


# Indexes for performance
Index('idx_designs_sequence', Design.sequence)
Index('idx_designs_lineage_hash', Design.lineage_hash)
Index('idx_builds_sequence', Build.sequence)
Index('idx_builds_lineage_hash', Build.lineage_hash)
Index('idx_tests_design_id', Test.design_id)
Index('idx_tests_build_id', Test.build_id) 
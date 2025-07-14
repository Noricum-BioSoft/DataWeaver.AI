# Biological Entity Tracking System

## Overview

The Biological Entity Tracking System implements a Design-Build-Test (DBT) workflow for tracking biological entities across experimental pipelines. The system automatically links uploaded assay results to the correct biological entities based on sequences, mutations, and metadata.

## 🧬 Core Features

### Entity Model
- **Design**: Initial biological design concepts with sequences and mutations
- **Build**: Physical constructs (plasmids, proteins) derived from designs
- **Test**: Assay results linked to designs and builds

### Automatic Data Linking
- Parse CSV/Excel files with minimal labeling
- Match rows to correct Design/Build using:
  - Sequence matching (exact)
  - Mutation matching (with/without parent reference)
  - Alias matching (fallback)
- Create Test records with confidence scoring

### Confidence Scoring
- **High**: Exact sequence or lineage hash match
- **Medium**: Mutation signature with known parent
- **Low**: Label-only match or inferred by metadata

## 📊 Database Schema

### Design Entity
```sql
CREATE TABLE designs (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    alias VARCHAR(255),
    description TEXT,
    sequence TEXT NOT NULL,
    sequence_type VARCHAR(50) DEFAULT 'protein',
    mutation_list TEXT,
    parent_design_id UUID REFERENCES designs(id),
    lineage_hash VARCHAR(64) NOT NULL,
    generation INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);
```

### Build Entity
```sql
CREATE TABLE builds (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    alias VARCHAR(255),
    description TEXT,
    sequence TEXT NOT NULL,
    sequence_type VARCHAR(50) DEFAULT 'protein',
    mutation_list TEXT,
    parent_build_id UUID REFERENCES builds(id),
    design_id UUID NOT NULL REFERENCES designs(id),
    lineage_hash VARCHAR(64) NOT NULL,
    generation INTEGER DEFAULT 0,
    construct_type VARCHAR(100),
    build_status VARCHAR(50) DEFAULT 'planned',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);
```

### Test Entity
```sql
CREATE TABLE tests (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    alias VARCHAR(255),
    description TEXT,
    test_type VARCHAR(100) NOT NULL,
    assay_name VARCHAR(255),
    protocol VARCHAR(255),
    result_value FLOAT,
    result_unit VARCHAR(50),
    result_type VARCHAR(50),
    match_confidence VARCHAR(20),
    match_method VARCHAR(100),
    match_score FLOAT,
    design_id UUID REFERENCES designs(id),
    build_id UUID REFERENCES builds(id),
    test_date TIMESTAMP,
    technician VARCHAR(255),
    lab_conditions TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);
```

## 🚀 API Endpoints

### Design Management
- `POST /api/bio/designs` - Create new design
- `GET /api/bio/designs` - List designs with filtering
- `GET /api/bio/designs/{design_id}` - Get specific design

### Build Management
- `POST /api/bio/builds` - Create new build
- `GET /api/bio/builds` - List builds with filtering
- `GET /api/bio/builds/{build_id}` - Get specific build

### Test Management
- `GET /api/bio/tests` - List tests with filtering
- `GET /api/bio/tests/{test_id}` - Get specific test

### Upload and Matching
- `POST /api/bio/upload-test-results` - Upload file and auto-match
- `POST /api/bio/match-preview` - Preview matching without committing

### Lineage and Statistics
- `GET /api/bio/lineage/{design_id}` - Get complete lineage
- `GET /api/bio/stats` - Get system statistics

## 📁 File Upload Format

### Supported Formats
- CSV files
- Excel files (.xlsx, .xls)

### Expected Columns
```csv
name,alias,sequence,mutations,result_value,result_unit,test_type,assay_name,technician
Clone_7,Clone_7,MGT...L72F...K,L72F,25.0,μM/min,activity,Enzyme Activity Assay,Dr. Smith
```

### Column Descriptions
- `name`: Test name/identifier
- `alias`: Alternative identifier
- `sequence`: Biological sequence (protein/DNA)
- `mutations`: Comma-separated mutation list (e.g., "L72F,R80K")
- `result_value`: Numerical test result
- `result_unit`: Unit of measurement
- `test_type`: Type of assay (activity, stability, expression, etc.)
- `assay_name`: Name of the assay protocol
- `technician`: Person who performed the test

## 🔍 Matching Algorithm

### 1. Sequence Matching (High Confidence)
```python
# Exact sequence match
if sequence in database:
    return match_with_confidence(1.0)
```

### 2. Mutation Matching (Medium Confidence)
```python
# Parse mutations: "L72F,R80K" -> ["L72F", "R80K"]
mutations = parse_mutations(mutation_string)

# Find designs/builds with matching mutations
for entity in database:
    if entity.mutations == mutations:
        return match_with_confidence(0.8)
```

### 3. Alias Matching (Low Confidence)
```python
# Fuzzy name/alias matching
for entity in database:
    if alias in entity.name or alias in entity.alias:
        return match_with_confidence(0.7)
```

## 📈 Example Usage

### Upload Assay Results
```bash
curl -X POST "http://localhost:8000/api/bio/upload-test-results" \
  -F "file=@assay_results.csv" \
  -F "test_type=activity" \
  -F "assay_name=Enzyme Activity Assay"
```

### Response
```json
{
  "total_rows": 7,
  "matched_rows": 6,
  "unmatched_rows": 1,
  "high_confidence": 4,
  "medium_confidence": 2,
  "low_confidence": 0,
  "matches": [
    {
      "row_index": 0,
      "test_id": "uuid-here",
      "match_result": {
        "matched": true,
        "design_id": "design-uuid",
        "build_id": "build-uuid",
        "confidence": "high",
        "method": "sequence",
        "score": 1.0
      }
    }
  ],
  "errors": [
    {
      "row_index": 6,
      "error": "No match found",
      "data": {...}
    }
  ]
}
```

### Get Lineage Information
```bash
curl "http://localhost:8000/api/bio/lineage/{design_id}"
```

### Response
```json
{
  "design": {
    "id": "design-uuid",
    "name": "L72F Mutant",
    "sequence": "MGT...L72F...K",
    "mutations": "L72F"
  },
  "builds": [
    {
      "id": "build-uuid",
      "name": "L72F Plasmid Construct",
      "design_id": "design-uuid"
    }
  ],
  "tests": [
    {
      "id": "test-uuid",
      "name": "L72F Activity Test",
      "result_value": 25.0,
      "confidence": "high"
    }
  ]
}
```

## 🛠️ Setup and Installation

### 1. Database Migration
```bash
cd backend
alembic upgrade head
```

### 2. Populate Sample Data
```bash
python scripts/populate_bio_entities.py
```

### 3. Start the Server
```bash
uvicorn main:app --reload
```

## 🧪 Testing the System

### 1. Upload Sample Data
```bash
curl -X POST "http://localhost:8000/api/bio/upload-test-results" \
  -F "file=@sample_data/assay_results.csv" \
  -F "test_type=activity"
```

### 2. Check Statistics
```bash
curl "http://localhost:8000/api/bio/stats"
```

### 3. View Lineage
```bash
curl "http://localhost:8000/api/bio/lineage/{design_id}"
```

## 🔧 Configuration

### Environment Variables
- `DATABASE_URL`: PostgreSQL connection string
- `UPLOAD_DIR`: Directory for file uploads
- `MAX_FILE_SIZE`: Maximum file size in bytes

### Matching Parameters
- `SEQUENCE_MATCH_THRESHOLD`: Minimum sequence similarity (default: 1.0)
- `MUTATION_MATCH_THRESHOLD`: Minimum mutation similarity (default: 0.8)
- `ALIAS_MATCH_THRESHOLD`: Minimum alias similarity (default: 0.7)

## 📊 Performance Considerations

### Indexes
- Sequence indexes for fast matching
- Lineage hash indexes for lineage queries
- Foreign key indexes for joins

### Caching
- Redis cache for frequently accessed entities
- Query result caching for lineage data

### Batch Processing
- Process large files in batches
- Background task processing for large uploads

## 🔮 Future Enhancements

### Planned Features
- Graph database integration (Neo4j)
- Advanced sequence alignment algorithms
- Machine learning-based matching
- Real-time collaboration features
- Integration with lab equipment APIs

### Optional Features
- Web UI with drag-and-drop upload
- Dashboard for assay results visualization
- Export functionality for reports
- API rate limiting and authentication

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License. 
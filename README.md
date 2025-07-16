# DataWeaver.AI

A comprehensive data management system with AI-powered workflow automation, file processing, and visualization capabilities.

## 🚀 Features

- **AI Chat Interface**: Natural language data processing and analysis
- **Drag-and-Drop File Upload**: Seamless file handling with automatic format detection
- **Smart File Merging**: Automatic CSV merging with intelligent column matching
- **Data Visualization**: Generate scatter plots, histograms, correlation heatmaps, and boxplots
- **Workflow Session Management**: Persistent data storage between processing steps
- **Biological Entity Management**: Specialized support for protein sequences and assay data
- **Real File Processing**: Complete file upload, storage, and processing pipeline
- **Integration Testing**: Comprehensive test suite with PostgreSQL support
- **Scalable Architecture**: Support for large datasets and parallel workflows

## 🏗️ Architecture

- **Frontend**: React with TypeScript, Tailwind CSS
- **Backend**: FastAPI with Python
- **Database**: PostgreSQL with SQLAlchemy ORM
- **File Storage**: Structured file system with metadata tracking
- **Visualization**: Matplotlib/Seaborn for data plotting
- **Testing**: pytest with PostgreSQL integration tests

## 🚀 Quick Start

### Option 1: Automated Startup (Recommended)

**macOS/Linux:**
```bash
# Make script executable (first time only)
chmod +x start.sh

# Start all services
./start.sh

# Or start specific services
./start.sh backend    # Backend only
./start.sh frontend   # Frontend only
./start.sh status     # Check service status
./start.sh help       # Show all options
```

**Windows:**
```cmd
# Start all services
start.bat

# Or start specific services
start.bat backend    # Backend only
start.bat frontend   # Frontend only
start.bat status     # Check service status
start.bat help       # Show all options
```

### Option 2: Manual Setup

1. **Backend Setup**:
   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn main:app --reload
   ```

2. **Frontend Setup**:
   ```bash
   cd frontend
   npm install
   npm start
   ```

3. **Database Setup**:
   ```bash
   # Run database migrations
   cd backend
   alembic upgrade head
   ```

## 🧪 Testing

### Integration Tests

Run the comprehensive integration test suite:

```bash
cd backend

# Set up PostgreSQL test database
export TEST_DATABASE_URL="postgresql://username@localhost:5432/datweaver_test"
export USE_POSTGRES=true

# Run integration tests
python run_integration_tests.py --type integration
```

### Test Coverage

The integration test suite covers:
- ✅ Complete file upload workflow
- ✅ API endpoint integration
- ✅ Data processing pipeline
- ✅ Error handling and recovery
- ✅ Performance and scalability
- ✅ System monitoring and health checks
- ✅ Data export and import functionality

## 📁 File Processing

### Upload and Process Files

**Upload a CSV file:**
```bash
curl -X POST "http://localhost:8000/api/files/upload" \
  -F "file=@assay_results.csv"
```

**Process uploaded file for bio entities:**
```bash
curl -X POST "http://localhost:8000/api/bio-entities/process-file/{file_id}" \
  -H "Content-Type: application/json" \
  -d '{"process_type": "assay_results"}'
```

### Supported File Formats

- **CSV**: Comma-separated values with automatic column detection
- **Excel**: .xlsx and .xls files (planned)
- **JSON**: Structured data files (planned)

### File Processing Pipeline

1. **Upload**: Files are validated and stored with unique identifiers
2. **Metadata Extraction**: File properties and structure are analyzed
3. **Content Processing**: CSV parsing with intelligent column mapping
4. **Entity Creation**: Automatic creation of Design and Test records
5. **Relationship Mapping**: Links between entities based on data patterns

## 💬 AI Chat Interface

The AI Chat provides a natural language interface for data processing and analysis.

### Example Commands

#### File Upload and Processing
```
"Upload these CSV files and merge them"
"Drag and drop the sequence files and merge them"
"Upload the assay results and process them"
```

#### Data Visualization
```
"Visualize the data in a scatter plot"
"Create a histogram of the results"
"Show me a correlation heatmap"
"Generate a boxplot of the measurements"
```

#### Workflow Management
```
"Create a new workflow called Protein Analysis Pipeline"
"Start a new session for data processing"
"Show me the workflow history"
```

### Complete Workflow Example

1. **Upload Files**: Drag and drop two CSV files into the chat
2. **Merge Data**: Type "merge these files" - system automatically merges on ID column
3. **Visualize**: Type "visualize the data in a scatter plot" - generates interactive charts
4. **Download**: Click download buttons for merged data or visualizations

## 📊 Data Processing Examples

### File Merging

Upload two CSV files with matching ID columns:

**sequences.csv:**
```csv
id,name,sequence,length
1,WT_Protein,MGT...L72...K,150
2,Mutant_L72F,MGT...L72F...K,150
3,Mutant_R80K,MGT...R80K...K,150
```

**measurements.csv:**
```csv
id,activity,concentration,technician
1,15.0,0.5,Dr. Smith
2,25.0,0.5,Dr. Smith
3,8.5,0.5,Dr. Johnson
```

**Result**: Automatically merged on ID column with statistics:
- Total rows: 3
- Matched rows: 3
- Unmatched rows: 0

### Data Visualization

After merging, request visualizations:

```
"Create a scatter plot of activity vs concentration"
"Show me a histogram of activity values"
"Generate a correlation heatmap"
"Make a boxplot of activity by technician"
```

**Available Plot Types:**
- **Scatter Plot**: Relationship between two numeric variables
- **Histogram**: Distribution of a single variable
- **Correlation Heatmap**: Relationships between all numeric columns
- **Box Plot**: Distribution comparison across categories

## 🧬 Biological Entity Management

### Create Design Entity

```bash
curl -X POST "http://localhost:8000/api/bio-entities/designs" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "WT_Protein",
    "alias": "Wild_Type",
    "description": "Wild type protein sequence",
    "sequence": "MGT...L72...K",
    "sequence_type": "protein",
    "mutation_list": ""
  }'
```

### Create Build Entity

```bash
curl -X POST "http://localhost:8000/api/bio-entities/builds" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Mutant_L72F",
    "alias": "L72F_Mutant",
    "description": "L72F mutation variant",
    "sequence": "MGT...L72F...K",
    "sequence_type": "protein",
    "mutation_list": "L72F",
    "design_id": "design-uuid-here",
    "construct_type": "plasmid",
    "build_status": "completed"
  }'
```

### Upload and Process Test Results

Create `assay_results.csv`:

```csv
name,alias,sequence,mutations,result_value,result_unit,test_type,assay_name,technician
Clone_7,Clone_7,MGT...L72F...K,L72F,25.0,μM/min,activity,Enzyme Activity Assay,Dr. Smith
WT_Control,WT_Control,MGT...L72...K,,15.0,μM/min,activity,Enzyme Activity Assay,Dr. Smith
Mutant_A,Mutant_A,MGT...R80K...K,R80K,8.5,μM/min,activity,Enzyme Activity Assay,Dr. Smith
Double_Mutant,Double_Mutant,MGT...L72F...R80K...K,"L72F,R80K",2.1,μM/min,activity,Enzyme Activity Assay,Dr. Johnson
```

**Upload and process:**
```bash
# 1. Upload file
curl -X POST "http://localhost:8000/api/files/upload" \
  -F "file=@assay_results.csv"

# 2. Process for bio entities (use file_id from upload response)
curl -X POST "http://localhost:8000/api/bio-entities/process-file/{file_id}" \
  -H "Content-Type: application/json" \
  -d '{"process_type": "assay_results"}'
```

**Result**: Automatic creation of Design and Test entities with proper relationships.

## 🔄 Workflow Management

### Create Workflow

```bash
curl -X POST "http://localhost:8000/workflows/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Protein Analysis Pipeline",
    "description": "Complete workflow for protein sequence analysis and validation",
    "status": "draft"
  }'
```

### Add Workflow Steps

```bash
curl -X POST "http://localhost:8000/workflows/1/steps/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Sequence Upload",
    "description": "Upload protein sequence files",
    "step_type": "input",
    "order_index": 1
  }'

curl -X POST "http://localhost:8000/workflows/1/steps/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Sequence Analysis",
    "description": "Analyze protein sequences for mutations",
    "step_type": "processing",
    "order_index": 2,
    "external_provider": "bioinformatics_tool",
    "external_config": {
      "tool": "blast",
      "database": "nr"
    }
  }'
```
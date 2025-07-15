# DataWeaver.AI

A comprehensive data management system with AI-powered workflow automation, file processing, and visualization capabilities.

## 🚀 Features

- **AI Chat Interface**: Natural language data processing and analysis
- **Drag-and-Drop File Upload**: Seamless file handling with automatic format detection
- **Smart File Merging**: Automatic CSV merging with intelligent column matching
- **Data Visualization**: Generate scatter plots, histograms, correlation heatmaps, and boxplots
- **Workflow Session Management**: Persistent data storage between processing steps
- **Biological Entity Management**: Specialized support for protein sequences and assay data
- **Scalable Architecture**: Support for large datasets and parallel workflows

## 🏗️ Architecture

- **Frontend**: React with TypeScript, Tailwind CSS
- **Backend**: FastAPI with Python
- **Database**: PostgreSQL with SQLAlchemy ORM
- **File Storage**: Structured file system with metadata tracking
- **Visualization**: Matplotlib/Seaborn for data plotting

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
curl -X POST "http://localhost:8000/api/bio/designs" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "WT_Protein",
    "alias": "Wild_Type",
    "description": "Wild type protein sequence",
    "sequence": "MGT...L72...K",
    "sequence_type": "protein",
    "mutation_list": "",
    "generation": 0
  }'
```

### Create Build Entity

```bash
curl -X POST "http://localhost:8000/api/bio/builds" \
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

### Upload Test Results

Create `assay_results.csv`:

```csv
name,alias,sequence,mutations,result_value,result_unit,test_type,assay_name,technician
Clone_7,Clone_7,MGT...L72F...K,L72F,25.0,μM/min,activity,Enzyme Activity Assay,Dr. Smith
WT_Control,WT_Control,MGT...L72...K,,15.0,μM/min,activity,Enzyme Activity Assay,Dr. Smith
Mutant_A,Mutant_A,MGT...R80K...K,R80K,8.5,μM/min,activity,Enzyme Activity Assay,Dr. Smith
Double_Mutant,Double_Mutant,MGT...L72F...R80K...K,"L72F,R80K",2.1,μM/min,activity,Enzyme Activity Assay,Dr. Johnson
```

Upload via API:

```bash
curl -X POST "http://localhost:8000/api/bio/upload-test-results" \
  -F "file=@assay_results.csv" \
  -F "test_type=activity" \
  -F "assay_name=Enzyme Activity Assay"
```

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

## 📁 File Formats

### Supported File Types
- **CSV**: Comma-separated values (primary format)
- **Excel**: .xlsx, .xls files
- **FASTA**: Biological sequences
- **JSON**: Structured data
- **Text**: Plain text files

### CSV Format Examples

**Biological Data:**
```csv
name,alias,sequence,mutations,result_value,result_unit,test_type,assay_name,technician
Clone_7,Clone_7,MGT...L72F...K,L72F,25.0,μM/min,activity,Enzyme Activity Assay,Dr. Smith
WT_Control,WT_Control,MGT...L72...K,,15.0,μM/min,activity,Enzyme Activity Assay,Dr. Smith
```

**General Data:**
```csv
id,name,value,category,date
1,Sample_A,15.5,Group_1,2024-01-15
2,Sample_B,22.3,Group_2,2024-01-16
3,Sample_C,18.7,Group_1,2024-01-17
```

## 🏗️ Project Structure

```
DataWeaver.AI/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── models/         # Database models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── api/            # API routes
│   │   ├── services/       # Business logic
│   │   └── utils/          # Utilities
│   ├── alembic/            # Database migrations
│   ├── services/           # Core services
│   │   ├── bio_matcher.py  # Biological data matching
│   │   └── workflow_state.py # Session management
│   └── requirements.txt
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   │   ├── AIChatLayout.tsx    # AI Chat interface
│   │   │   ├── PromptBox.tsx       # Input with file upload
│   │   │   ├── ChatHistory.tsx     # Message display
│   │   │   └── ResultPanel.tsx     # Results and visualizations
│   │   ├── services/       # API services
│   │   └── types/          # TypeScript types
│   └── package.json
├── docs/                   # Documentation
├── start.sh               # Startup script (macOS/Linux)
├── start.bat              # Startup script (Windows)
└── setup.sh               # Initial setup script
```

## 🔧 Services

The application consists of the following services:

- **Frontend**: React development server (port 3000)
- **Backend**: FastAPI server (port 8000)
- **Database**: PostgreSQL (port 5432)
- **Cache**: Redis (port 6379)

## 🎯 Key Features

### AI Chat Interface
- Natural language processing for data operations
- Drag-and-drop file upload with visual feedback
- Smart command detection and routing
- Real-time processing status updates

### File Processing
- Automatic format detection and validation
- Intelligent CSV merging with column matching
- Progress tracking and error handling
- Download capabilities for processed data

### Data Visualization
- Multiple chart types (scatter, histogram, heatmap, boxplot)
- Interactive plot generation
- Column information and data statistics
- Download options for generated visualizations

### Session Management
- Persistent data storage between steps
- Workflow history tracking
- Session-based data isolation
- Automatic cleanup of old sessions

## 🚀 Getting Started

1. **Clone the repository**
2. **Run the startup script**: `./start.sh`
3. **Open the application**: http://localhost:3000
4. **Start with AI Chat**: Use natural language to upload and process data
5. **Try the examples**: Upload sample CSV files and request visualizations

## 📚 Example Workflows

### Basic Data Analysis
1. Upload two CSV files via drag-and-drop
2. Type "merge these files" in the chat
3. Type "visualize the data in a scatter plot"
4. Download the merged data and visualization

### Biological Data Processing
1. Upload sequence and measurement CSV files
2. Request "merge the files and show me a correlation heatmap"
3. Analyze the relationships between sequence properties and measurements
4. Download the analysis results

### Multi-Step Workflow
1. Create a new session: "Start a new data analysis session"
2. Upload files and merge: "Upload these files and merge them"
3. Generate multiple visualizations: "Create a histogram and a scatter plot"
4. Review workflow history and download results

The system is designed to be intuitive and powerful, allowing users to focus on data analysis rather than technical implementation details.
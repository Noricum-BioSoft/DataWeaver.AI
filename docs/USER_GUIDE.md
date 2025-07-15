# DataWeaver.AI User Guide

## 🚀 Getting Started

### First Time Setup

1. **Start the Application**
   ```bash
   # Make startup script executable
   chmod +x start.sh
   
   # Start all services
   ./start.sh
   ```

2. **Access the Application**
   - Open your browser to: http://localhost:3000
   - The AI Chat interface will be the default view

3. **Verify Services**
   - Backend API: http://localhost:8000
   - Frontend: http://localhost:3000
   - Database: PostgreSQL on port 5432

## 💬 AI Chat Interface

### Overview
The AI Chat provides a natural language interface for data processing and analysis. You can upload files, merge data, generate visualizations, and manage workflows using simple commands.

### Basic Commands

#### File Upload
```
"Upload these CSV files"
"Drag and drop the sequence files"
"Upload the assay results"
```

#### Data Processing
```
"Merge these files"
"Combine the data"
"Process the uploaded files"
```

#### Visualization
```
"Visualize the data in a scatter plot"
"Create a histogram of the results"
"Show me a correlation heatmap"
"Generate a boxplot of the measurements"
```

#### Workflow Management
```
"Create a new workflow called Protein Analysis"
"Start a new session for data processing"
"Show me the workflow history"
```

## 📊 Complete Workflow Example

### Step 1: Upload Files
1. **Drag and drop** two CSV files into the chat input area
2. **Wait for upload confirmation** - you'll see file names displayed
3. **Files are automatically validated** for format and content

### Step 2: Merge Data
1. **Type**: "Merge these files"
2. **System automatically**:
   - Identifies matching ID columns
   - Merges the data
   - Shows merge statistics
   - Provides download link

### Step 3: Visualize Data
1. **Type**: "Visualize the data in a scatter plot"
2. **System generates**:
   - Interactive plot
   - Column information
   - Download option

### Step 4: Download Results
1. **Click download buttons** for:
   - Merged CSV data
   - Generated visualizations
2. **Files are saved** to your local machine

## 🧬 Biological Data Processing

### Uploading Sequence Data
1. **Prepare CSV file** with columns:
   - `id`: Unique identifier
   - `name`: Sequence name
   - `sequence`: Protein/DNA sequence
   - `length`: Sequence length
   - `mutation_type`: Type of mutation (optional)

2. **Upload via AI Chat**:
   ```
   "Upload the sequence data"
   ```

### Uploading Assay Results
1. **Prepare CSV file** with columns:
   - `id`: Matching identifier
   - `name`: Sample name
   - `result_value`: Measurement value
   - `result_unit`: Unit of measurement
   - `test_type`: Type of test
   - `technician`: Person who performed test

2. **Upload and merge**:
   ```
   "Upload the assay results and merge with sequences"
   ```

### Biological Entity Management
1. **Create Design Entities**:
   - Use API endpoint: `POST /api/bio/designs`
   - Include sequence information
   - Specify mutation details

2. **Create Build Entities**:
   - Link to design entities
   - Include construct information
   - Track build status

3. **Upload Test Results**:
   - Use API endpoint: `POST /api/bio/upload-test-results`
   - Include assay metadata
   - Link to biological entities

## 📈 Data Visualization

### Available Plot Types

#### Scatter Plot
- **Use for**: Relationship between two numeric variables
- **Command**: "Create a scatter plot of X vs Y"
- **Example**: "Show me a scatter plot of activity vs concentration"

#### Histogram
- **Use for**: Distribution of a single variable
- **Command**: "Create a histogram of X"
- **Example**: "Show me a histogram of activity values"

#### Correlation Heatmap
- **Use for**: Relationships between all numeric columns
- **Command**: "Generate a correlation heatmap"
- **Example**: "Show me correlations between all variables"

#### Box Plot
- **Use for**: Distribution comparison across categories
- **Command**: "Create a boxplot of X by Y"
- **Example**: "Make a boxplot of activity by technician"

### Visualization Best Practices

1. **Data Requirements**:
   - Minimum 2 rows for visualization
   - Numeric columns for plotting
   - Categorical columns for grouping

2. **Column Selection**:
   - System automatically detects numeric columns
   - You can specify columns in commands
   - Invalid columns will show error message

3. **Plot Customization**:
   - System chooses optimal settings
   - Colors and styles are automatically selected
   - Download options for high-resolution images

## 🔄 Workflow Session Management

### Creating Sessions
1. **Start new session**:
   ```
   "Start a new data analysis session"
   ```

2. **Session features**:
   - Persistent data storage
   - Workflow history tracking
   - Automatic cleanup after inactivity

### Session Commands
```
"Show me the current session status"
"List the uploaded files"
"Show the workflow history"
"Clear the session data"
```

### Session Benefits
- **Data persistence**: Files and merged data stay available
- **Multi-step workflows**: Build complex analyses step by step
- **History tracking**: See what operations were performed
- **Download management**: Access all generated files

## 📁 File Format Requirements

### CSV Files
- **Encoding**: UTF-8
- **Delimiter**: Comma (,)
- **Header row**: Required with column names
- **Data types**: Consistent per column
- **Size limit**: 50MB maximum

### Required Columns for Merging
- **ID column**: Must be present in both files
- **Matching values**: IDs should match between files
- **Unique names**: Column names should be unique

### Example CSV Structure
```csv
id,name,value,category,date
1,Sample_A,15.5,Group_1,2024-01-15
2,Sample_B,22.3,Group_2,2024-01-16
3,Sample_C,18.7,Group_1,2024-01-17
```

## 🛠️ Troubleshooting

### Common Issues

#### File Upload Problems
- **Issue**: File not uploading
- **Solution**: Check file size (max 50MB) and format (CSV required)
- **Issue**: Upload stuck
- **Solution**: Refresh page and try again

#### Merge Problems
- **Issue**: "No matching columns found"
- **Solution**: Ensure both files have an ID column with matching values
- **Issue**: "Merge failed"
- **Solution**: Check CSV format and column consistency

#### Visualization Problems
- **Issue**: "No numeric columns found"
- **Solution**: Ensure data has numeric columns for plotting
- **Issue**: "Visualization failed"
- **Solution**: Check data quality and try different plot types

#### Session Problems
- **Issue**: Session expired
- **Solution**: Create new session and re-upload files
- **Issue**: Data not persisting
- **Solution**: Check session status and recreate if needed

### Error Messages

#### File Errors
- `FILE_TOO_LARGE`: Reduce file size below 50MB
- `INVALID_FORMAT`: Convert to CSV format
- `MISSING_HEADERS`: Add column headers to CSV

#### Merge Errors
- `NO_ID_COLUMN`: Add ID column to both files
- `NO_MATCHING_IDS`: Ensure ID values match between files
- `COLUMN_CONFLICT`: Rename duplicate column names

#### Visualization Errors
- `NO_NUMERIC_COLUMNS`: Add numeric data columns
- `INSUFFICIENT_DATA`: Ensure at least 2 rows of data
- `INVALID_COLUMN`: Check column names exist in data

## 📚 Advanced Features

### API Integration
- **Direct API access**: Use endpoints for programmatic access
- **Batch processing**: Upload multiple files via API
- **Custom workflows**: Build complex automation scripts

### Data Export
- **Merged data**: Download as CSV
- **Visualizations**: Download as PNG images
- **Session data**: Export complete workflow state

### Performance Optimization
- **Large files**: System handles up to 10,000 rows efficiently
- **Multiple sessions**: Run parallel workflows
- **Caching**: Results cached for faster access

## 🎯 Best Practices

### Data Preparation
1. **Clean your data** before uploading
2. **Use consistent formats** for dates and numbers
3. **Include meaningful column names**
4. **Validate data types** per column

### Workflow Design
1. **Plan your analysis** before starting
2. **Use descriptive file names**
3. **Document your workflow** steps
4. **Save important results** locally

### Visualization
1. **Choose appropriate plot types** for your data
2. **Consider your audience** when selecting visualizations
3. **Use clear column names** for better plot labels
4. **Download high-resolution images** for presentations

## 📞 Support

### Getting Help
- **Check the documentation**: Review this guide and API docs
- **Try sample data**: Use provided example files
- **Test with small files**: Start with simple examples
- **Check error messages**: Read detailed error descriptions

### Sample Data
- **Location**: `backend/sample_data/`
- **Files**: `sequences.csv`, `assay_results.csv`, `sales_data.csv`
- **Purpose**: Testing and learning system features

### System Status
- **Check services**: `./start.sh status`
- **View logs**: Check terminal output for error messages
- **Restart services**: `./start.sh restart`

The DataWeaver.AI system is designed to be intuitive and powerful, allowing you to focus on data analysis rather than technical implementation details. 
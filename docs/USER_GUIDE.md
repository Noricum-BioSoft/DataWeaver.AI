# DataWeaver.AI User Guide

## Introduction

DataWeaver.AI is an intelligent data processing platform that helps you upload, merge, analyze, and visualize your data through natural language interactions. Whether you're working with protein data, sales figures, or any other CSV datasets, DataWeaver.AI makes data analysis accessible and intuitive.

## Getting Started

### 1. Access the Application

1. **Start the application** using the provided scripts:
   ```bash
   # macOS/Linux
   ./start.sh
   
   # Windows
   start.bat
   ```

2. **Open your browser** and navigate to:
   ```
   http://localhost:3000
   ```

3. **You'll see the main interface** with:
   - AI Chat area (main interaction point)
   - File upload area (drag & drop)
   - Navigation sidebar
   - Status indicators

### 2. Your First Workflow

Let's walk through a complete example using protein data:

#### Step 1: Upload Files
1. **Prepare your CSV files** (e.g., protein_abundance.csv, protein_expression.csv)
2. **Drag and drop** them into the upload area
3. **Wait for confirmation** - you'll see a success message for each file

#### Step 2: Merge the Data
1. **Type in the chat**: "merge the files"
2. **Wait for processing** - the system will:
   - Identify common columns (like protein_id)
   - Merge all your files
   - Show you the results

#### Step 3: Analyze the Data
1. **Ask questions** like:
   - "What columns are in the data?"
   - "How many rows do we have?"
   - "Are there any missing values?"

#### Step 4: Create Visualizations
1. **Request charts** like:
   - "Create a scatter plot of abundance vs expression"
   - "Make a histogram of the abundance values"
   - "Show me a correlation matrix"

## Core Features

### File Upload

#### Supported Formats
- **CSV files** (primary format)
- **JSON files** (basic support)
- **Excel files** (limited support)

#### Upload Process
1. **Drag and drop** files into the upload area
2. **Multiple files** can be uploaded at once
3. **Automatic validation** checks file format and content
4. **Progress indicators** show upload status
5. **Success confirmation** for each file

#### File Requirements
- **Maximum size**: 10MB per file
- **Encoding**: UTF-8 recommended
- **Headers**: First row should contain column names
- **Data types**: Mixed data types supported

### Data Merging

#### How It Works
1. **Column Analysis**: System finds common columns across files
2. **ID Detection**: Identifies primary key columns (e.g., protein_id, customer_id)
3. **Smart Merging**: Performs outer join on common ID columns
4. **Result Summary**: Shows matched vs unmatched rows

#### Merge Strategy
- **Outer Join**: Keeps all rows from all files
- **ID Matching**: Uses common identifier columns
- **Column Preservation**: Keeps all columns from all files
- **Missing Data**: Fills with null values where data doesn't match

#### Example Merge
```
File 1: protein_abundance.csv
- protein_id, abundance, condition

File 2: protein_expression.csv  
- protein_id, expression_level, tissue

Result: Merged dataset
- protein_id, abundance, condition, expression_level, tissue
```

### Data Analysis

#### Asking Questions
You can ask natural language questions about your data:

**Basic Questions:**
- "What columns are in the data?"
- "How many rows do we have?"
- "Show me the first few rows"

**Statistical Questions:**
- "What's the average value in column X?"
- "Are there any outliers?"
- "What's the correlation between X and Y?"

**Data Quality Questions:**
- "Are there any missing values?"
- "How many unique values are in column X?"
- "What are the data types of each column?"

#### Getting Insights
The system provides:
- **Statistical summaries** (mean, median, standard deviation)
- **Data quality analysis** (missing values, duplicates)
- **Correlation analysis** (relationships between columns)
- **Outlier detection** (unusual data points)
- **Recommendations** (suggestions for further analysis)

### Visualization

#### Available Chart Types

**Scatter Plots**
- Use: "Create a scatter plot of X vs Y"
- Best for: Showing relationships between two variables
- Example: "Show abundance vs expression level"

**Histograms**
- Use: "Make a histogram of column X"
- Best for: Showing distribution of values
- Example: "Show the distribution of abundance values"

**Correlation Matrices**
- Use: "Create a correlation matrix"
- Best for: Showing relationships between all numeric columns
- Example: "Show correlations between all numeric columns"

**Box Plots**
- Use: "Create a box plot of X by Y"
- Best for: Comparing distributions across categories
- Example: "Show abundance by condition"

#### Chart Customization
- **Automatic column selection** based on data types
- **Smart defaults** for chart appearance
- **Interactive features** (zoom, pan, hover)
- **Export capabilities** (PNG, SVG)

### AI Chat Interface

#### Natural Language Processing
The AI understands various ways to express the same request:

**File Operations:**
- "merge the files" = "combine the datasets" = "join the data"

**Analysis Requests:**
- "what's in the data?" = "describe the dataset" = "summarize the data"

**Visualization Requests:**
- "create a scatter plot" = "plot X vs Y" = "show relationship between X and Y"

#### Context Awareness
The AI remembers:
- **Uploaded files** and their contents
- **Previous questions** and answers
- **Generated visualizations**
- **Session state** throughout your workflow

#### Suggestions
The system provides:
- **Follow-up questions** based on your data
- **Analysis suggestions** for deeper insights
- **Visualization recommendations** for your data type

## Advanced Features

### Session Management

#### Session Lifecycle
1. **Automatic creation** when you first upload files
2. **Persistent storage** of all uploaded data
3. **24-hour timeout** for automatic cleanup
4. **Manual clearing** available through chat

#### Session Data
- **Uploaded files** and their metadata
- **Merged datasets** and results
- **Generated visualizations** and charts
- **Analysis results** and insights
- **Chat history** and context

### Biological Data Support

#### Specialized Features
- **Protein sequence analysis**
- **Assay result processing**
- **Biological entity tracking**
- **Sequence matching algorithms**

#### Biological Workflows
1. **Upload assay results** (CSV with protein data)
2. **Automatic matching** to known sequences
3. **Confidence scoring** for matches
4. **Lineage tracking** for design-build-test workflows

### Data Export

#### Available Formats
- **CSV export** of merged data
- **PNG/SVG export** of visualizations
- **JSON export** of analysis results
- **PDF reports** (planned feature)

#### Export Process
1. **Request export** through chat
2. **Choose format** and options
3. **Download file** to your computer
4. **Share results** with colleagues

## Troubleshooting

### Common Issues

#### File Upload Problems
**Problem**: File upload fails
**Solutions**:
- Check file size (max 10MB)
- Ensure file is CSV format
- Verify UTF-8 encoding
- Check for valid headers

**Problem**: Files don't merge properly
**Solutions**:
- Ensure files have common ID columns
- Check column names match exactly
- Verify data types are consistent
- Look for missing values in ID columns

#### Analysis Issues
**Problem**: Can't generate visualizations
**Solutions**:
- Ensure you have numeric columns
- Check for sufficient data (min 2 rows)
- Verify column names are correct
- Try different chart types

**Problem**: AI doesn't understand your question
**Solutions**:
- Rephrase your question more simply
- Be specific about column names
- Use natural language
- Check the data context

#### Performance Issues
**Problem**: Slow processing
**Solutions**:
- Reduce file sizes
- Use fewer columns
- Close other browser tabs
- Check server status

### Getting Help

#### Built-in Help
- **Type "help"** in the chat for basic commands
- **Ask "what can I do?"** for feature overview
- **Use "show me the data"** to see current state

#### Error Messages
- **Read error messages** carefully for specific issues
- **Check file formats** if upload fails
- **Verify column names** if merge fails
- **Look at data preview** if analysis fails

#### Support Resources
- **Documentation**: Check the `/docs` folder
- **API Reference**: Visit `/docs` endpoint
- **GitHub Issues**: Report bugs and feature requests
- **Community**: Use GitHub Discussions

## Best Practices

### Data Preparation

#### Before Upload
1. **Clean your data** (remove duplicates, fix errors)
2. **Standardize column names** (consistent naming)
3. **Check data types** (numeric vs text)
4. **Handle missing values** (fill or remove)
5. **Validate file format** (CSV with headers)

#### File Organization
1. **Use descriptive filenames** (e.g., "protein_abundance_2024.csv")
2. **Include metadata** in column names
3. **Use consistent ID columns** across files
4. **Document your data** with clear descriptions

### Workflow Optimization

#### Efficient Analysis
1. **Start with overview** ("what's in the data?")
2. **Check data quality** ("are there missing values?")
3. **Explore relationships** ("show correlations")
4. **Create visualizations** ("plot X vs Y")
5. **Export results** for further analysis

#### Session Management
1. **Use one session** per analysis project
2. **Clear sessions** when starting new projects
3. **Export important results** before clearing
4. **Document your workflow** for reproducibility

### Collaboration

#### Sharing Results
1. **Export merged data** as CSV
2. **Save visualizations** as images
3. **Document your analysis** process
4. **Share session IDs** for team collaboration

#### Team Workflows
1. **Standardize file formats** across team
2. **Use consistent naming** conventions
3. **Document analysis steps** clearly
4. **Version control** your data files

## Examples

### Protein Analysis Workflow

```
1. Upload files:
   - protein_abundance.csv
   - protein_expression.csv
   - protein_sequences.csv
   - protein_spr.csv

2. Merge data:
   "merge the files"

3. Explore data:
   "What columns do we have?"
   "How many proteins are in the dataset?"
   "Are there any missing values?"

4. Create visualizations:
   "Create a scatter plot of abundance vs expression"
   "Show the distribution of SPR values"
   "Create a correlation matrix of all numeric columns"

5. Analyze relationships:
   "What's the correlation between abundance and expression?"
   "Are there any outliers in the SPR data?"
   "Which proteins have the highest expression?"

6. Export results:
   "Export the merged data as CSV"
   "Save the correlation plot as PNG"
```

### Sales Data Analysis

```
1. Upload files:
   - sales_2023.csv
   - customer_data.csv
   - product_catalog.csv

2. Merge data:
   "merge the files using customer_id"

3. Analyze performance:
   "What's the total sales for 2023?"
   "Which products sell best?"
   "Show sales by region"

4. Create visualizations:
   "Create a histogram of sales amounts"
   "Show sales trends over time"
   "Create a scatter plot of customer age vs sales"

5. Get insights:
   "What's the average order value?"
   "Which customers are most valuable?"
   "Are there seasonal patterns in sales?"
```

## Future Features

### Planned Enhancements
- **Advanced visualizations** (3D plots, interactive charts)
- **Machine learning integration** (predictive analytics)
- **Real-time collaboration** (shared sessions)
- **Advanced file formats** (Parquet, HDF5)
- **Cloud storage integration** (AWS S3, Google Cloud)
- **Workflow templates** (predefined analysis patterns)
- **Advanced data validation** (automated quality checks)
- **Export capabilities** (PDF reports, Excel exports)

### User Experience Improvements
- **Drag-and-drop interface** enhancements
- **Real-time preview** of data changes
- **Undo/redo functionality** for operations
- **Keyboard shortcuts** for power users
- **Custom themes** and personalization
- **Mobile responsiveness** improvements

---

**DataWeaver.AI** - Making data analysis accessible and intuitive for everyone. 
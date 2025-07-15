# Sample Data Files

This directory contains example CSV files for testing and demonstrating DataWeaver.AI features.

## 📊 File Descriptions

### Biological Data Examples

#### `sequences.csv`
Protein sequence data with mutations and properties.
- **Use Case**: Upload to test biological entity management
- **Columns**: id, name, sequence, length, mutation_type
- **Format**: CSV with protein sequences and mutation information

#### `assay_results.csv`
Laboratory assay results with measurements and metadata.
- **Use Case**: Upload to test data merging and visualization
- **Columns**: id, name, result_value, result_unit, test_type, technician
- **Format**: CSV with experimental results

### General Data Examples

#### `sales_data.csv`
Sample sales data for business analysis.
- **Use Case**: Test data visualization and analysis
- **Columns**: id, product, sales_amount, region, date
- **Format**: CSV with business metrics

#### `customer_data.csv`
Customer information for data merging examples.
- **Use Case**: Demonstrate CSV merging capabilities
- **Columns**: id, customer_name, email, subscription_type
- **Format**: CSV with customer records

## 🧪 Testing Scenarios

### 1. File Merging Test
1. Upload `sequences.csv` and `assay_results.csv`
2. Type "merge these files" in AI Chat
3. Verify automatic merging on ID column
4. Check merge statistics and preview

### 2. Data Visualization Test
1. Upload any CSV file with numeric columns
2. Request visualizations:
   - "Create a scatter plot"
   - "Show me a histogram"
   - "Generate a correlation heatmap"
   - "Make a boxplot"
3. Verify plot generation and download

### 3. Biological Data Processing
1. Upload `sequences.csv` to bio-entities endpoint
2. Upload `assay_results.csv` for test results
3. Use AI Chat to merge and visualize
4. Test biological entity matching

### 4. Multi-Step Workflow
1. Start new session
2. Upload multiple files
3. Merge data automatically
4. Generate multiple visualizations
5. Download results

## 📋 File Formats

All sample files are in CSV format with:
- UTF-8 encoding
- Comma-separated values
- Header row with column names
- Consistent data types per column

## 🔧 Usage Instructions

### Via AI Chat Interface
1. Drag and drop files into the chat input
2. Use natural language commands:
   - "Upload these files"
   - "Merge the data"
   - "Visualize in a scatter plot"

### Via API Endpoints
```bash
# Upload for bio entities
curl -X POST "http://localhost:8000/api/bio/upload-test-results" \
  -F "file=@assay_results.csv"

# Merge files
curl -X POST "http://localhost:8000/api/bio/merge-files" \
  -F "file1=@sequences.csv" \
  -F "file2=@assay_results.csv"

# Generate visualization
curl -X POST "http://localhost:8000/api/bio/generate-visualization" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "your-session-id",
    "plot_type": "scatter",
    "x_column": "activity",
    "y_column": "concentration"
  }'
```

## 📈 Expected Results

### Merge Results
- **Total Rows**: Varies by file combination
- **Matched Rows**: Based on ID column matching
- **Unmatched Rows**: Rows without matching IDs
- **Download**: Merged CSV file

### Visualization Results
- **Plot Types**: Scatter, histogram, heatmap, boxplot
- **Format**: Base64 PNG image
- **Metadata**: Column information and data statistics
- **Download**: PNG image file

## 🚀 Quick Start

1. **Start the application**: `./start.sh`
2. **Open AI Chat**: Navigate to http://localhost:3000
3. **Upload sample files**: Drag and drop CSV files
4. **Test commands**:
   - "Merge these files"
   - "Visualize the data in a scatter plot"
   - "Show me a histogram"
5. **Download results**: Use download buttons

## 📝 Notes

- Files are designed to work together for testing
- ID columns are consistent across related files
- Numeric columns are included for visualization testing
- Text columns provide categorical data for analysis
- All data is synthetic and for demonstration purposes only 
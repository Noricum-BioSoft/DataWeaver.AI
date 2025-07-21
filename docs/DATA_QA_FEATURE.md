# Data Q&A Feature

## Overview

The Data Q&A feature allows users to ask natural language questions about their data and receive intelligent answers powered by LLM (Large Language Model) integration. This feature enhances the user experience by providing conversational data analysis capabilities.

## Features

### 1. Natural Language Questions
Users can ask questions like:
- "How many rows are in my data?"
- "What columns are available?"
- "Are there any missing values?"
- "What is the average salary?"
- "Show me the unique cities in the data"

### 2. Intelligent Data Analysis
The system automatically:
- Analyzes data structure and content
- Identifies data types and patterns
- Detects missing values and outliers
- Provides statistical summaries
- Generates insights and recommendations

### 3. LLM Integration
- Uses OpenAI GPT-3.5-turbo for intelligent responses
- Falls back to rule-based responses when LLM is unavailable
- Provides confidence levels for answers
- Suggests follow-up questions

### 4. Context-Aware Suggestions
- Generates relevant question suggestions based on data characteristics
- Adapts suggestions to the specific dataset
- Provides contextual recommendations

## Architecture

### Backend Components

#### 1. DataQAService (`backend/app/services/data_qa_service.py`)
- Core service for data analysis and Q&A
- Integrates with OpenAI API
- Provides fallback rule-based responses
- Handles data preview and suggestions

#### 2. Data QA API (`backend/app/api/data_qa.py`)
- RESTful endpoints for Q&A functionality
- Handles question submission and response
- Provides data preview and suggestions
- Health check endpoint

#### 3. Database Integration
- Uses existing session management
- Stores data analysis results
- Tracks question history and responses

### Frontend Components

#### 1. DataQASuggestions (`frontend/src/components/DataQASuggestions.tsx`)
- Displays suggested questions
- Handles suggestion clicks
- Shows loading and error states

#### 2. Enhanced AIChatMain
- Integrates Q&A functionality into chat interface
- Handles data Q&A requests
- Shows suggestions after responses

#### 3. API Integration (`frontend/src/services/api.ts`)
- DataQaApi for backend communication
- Handles question submission and responses
- Manages data preview and suggestions

## API Endpoints

### POST `/api/data-qa/ask`
Ask a question about data in a session.

**Request:**
```json
{
  "session_id": "string",
  "question": "string"
}
```

**Response:**
```json
{
  "success": true,
  "answer": "string",
  "insights": ["string"],
  "confidence": "high|medium|low",
  "suggestions": ["string"],
  "data_summary": {}
}
```

### GET `/api/data-qa/preview/{session_id}`
Get a preview of data in a session.

**Response:**
```json
{
  "success": true,
  "preview": {
    "filename.csv": {
      "rows": 100,
      "columns": ["col1", "col2"],
      "sample": [...],
      "dtypes": {}
    }
  }
}
```

### GET `/api/data-qa/suggestions/{session_id}`
Get suggested questions based on data.

**Response:**
```json
{
  "suggestions": [
    "How many rows are in the data?",
    "What columns are available?",
    "Are there any missing values?"
  ]
}
```

## Configuration

### Environment Variables

Add to your `.env` file:

```bash
# OpenAI API configuration (optional)
OPENAI_API_KEY=your-openai-api-key-here
```

### Dependencies

The feature requires these additional dependencies:
```bash
pip install openai pandas
```

## Usage Examples

### 1. Basic Question
```
User: "How many rows are in my data?"
AI: "The dataset contains 1,247 total rows across 3 files."
```

### 2. Data Type Question
```
User: "What columns are available?"
AI: "The dataset has 15 unique columns: id, name, age, city, salary, department, hire_date, manager_id, location, is_active, product_id, category, price, stock_quantity, supplier_id"
```

### 3. Statistical Question
```
User: "What is the average salary?"
AI: "The average salary across all employees is $72,450. The salary range is from $45,000 to $120,000."
```

### 4. Data Quality Question
```
User: "Are there any missing values?"
AI: "Yes, I found missing values in several columns: city (12 missing), manager_id (8 missing), and location (5 missing)."
```

## Implementation Details

### Data Analysis Process

1. **File Discovery**: Scans session directory for data files
2. **Data Reading**: Reads CSV files using pandas
3. **Analysis**: Performs comprehensive data analysis:
   - Basic statistics (row count, column count)
   - Data type identification
   - Missing value detection
   - Numeric vs categorical classification
   - Statistical summaries

### LLM Integration

1. **Context Creation**: Builds context from data analysis
2. **Prompt Engineering**: Creates structured prompts for LLM
3. **Response Parsing**: Extracts insights and confidence levels
4. **Fallback Handling**: Uses rule-based responses when LLM unavailable

### Error Handling

- Graceful degradation when LLM is unavailable
- Comprehensive error messages
- Retry mechanisms for API failures
- Data validation and sanitization

## Testing

### Manual Testing
```bash
# Test the backend service
cd backend
python test_data_qa.py
```

### API Testing
```bash
# Test the API endpoints
curl -X POST http://localhost:8000/api/data-qa/ask \
  -H "Content-Type: application/json" \
  -d '{"session_id": "test", "question": "How many rows?"}'
```

## Future Enhancements

### 1. Advanced Analytics
- Correlation analysis
- Outlier detection
- Trend analysis
- Predictive insights

### 2. Visualization Integration
- Automatic chart generation
- Interactive visualizations
- Custom plot types

### 3. Multi-Modal Support
- Excel file support
- JSON data analysis
- Database connectivity

### 4. Enhanced LLM Features
- Conversation memory
- Context-aware responses
- Multi-language support
- Custom model fine-tuning

## Security Considerations

1. **API Key Management**: Secure storage of OpenAI API keys
2. **Data Privacy**: No data sent to external services without consent
3. **Rate Limiting**: Implement rate limits for API calls
4. **Input Validation**: Sanitize user questions and data
5. **Error Handling**: Don't expose sensitive information in errors

## Performance Considerations

1. **Caching**: Cache data analysis results
2. **Async Processing**: Handle long-running analyses
3. **File Size Limits**: Implement reasonable file size limits
4. **Memory Management**: Efficient handling of large datasets
5. **Response Time**: Optimize for sub-second response times

## Troubleshooting

### Common Issues

1. **OpenAI API Errors**
   - Check API key configuration
   - Verify network connectivity
   - Check rate limits

2. **Data Analysis Errors**
   - Verify file format (CSV)
   - Check file permissions
   - Ensure sufficient memory

3. **Frontend Issues**
   - Check browser console for errors
   - Verify API endpoint configuration
   - Test network connectivity

### Debug Mode

Enable debug logging:
```bash
export LOG_LEVEL=DEBUG
```

## Contributing

When contributing to the Data Q&A feature:

1. Follow the existing code style
2. Add comprehensive tests
3. Update documentation
4. Consider performance implications
5. Test with various data types and sizes 
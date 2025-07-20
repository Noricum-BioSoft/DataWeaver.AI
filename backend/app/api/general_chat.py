from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from pydantic import BaseModel
import openai
import os
import logging
from ..database import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/general-chat", tags=["general-chat"])

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    response: str
    suggestions: list[str]
    confidence: str
    context: Optional[Dict[str, Any]] = None

class GeneralChatService:
    """Service for handling general AI chat conversations"""
    
    def __init__(self):
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        if self.openai_api_key:
            openai.api_key = self.openai_api_key
    
    def generate_response(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate AI response for general chat"""
        
        if not self.openai_api_key:
            # Fallback to rule-based responses
            return self._generate_fallback_response(message)
        
        try:
            # Create system prompt
            system_prompt = """You are DataWeaver.AI, a helpful AI assistant for data management and analysis. 
            You help users with:
            - Understanding how to use the system
            - Data processing workflows
            - File uploads and management
            - Data visualization
            - Workflow creation and management
            - General data analysis questions
            
            Be helpful, concise, and provide actionable suggestions. If you don't know something, say so and suggest alternatives."""
            
            # Create user prompt with context
            user_prompt = f"User message: {message}"
            if context:
                user_prompt += f"\n\nContext: {context}"
            
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            llm_response = response.choices[0].message.content or ""
            
            # Extract suggestions from response
            suggestions = self._extract_suggestions(llm_response)
            
            return {
                "response": llm_response,
                "suggestions": suggestions,
                "confidence": "high",
                "context": context
            }
            
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {str(e)}")
            return self._generate_fallback_response(message)
    
    def _generate_fallback_response(self, message: str) -> Dict[str, Any]:
        """Generate fallback response when LLM is not available"""
        message_lower = message.lower()
        
        if 'how do i use' in message_lower or 'how to use' in message_lower:
            return {
                "response": "Welcome to DataWeaver.AI! I can help you with data management and analysis. Here's how to get started:\n\n1. **Upload Files**: Drag and drop CSV files or use the upload button\n2. **Merge Data**: Ask me to merge multiple CSV files\n3. **Visualize**: Request charts, plots, or visualizations\n4. **Analyze**: Ask questions about your data\n5. **Create Workflows**: Set up automated data processing pipelines\n\nWhat would you like to do first?",
                "suggestions": [
                    "Upload some CSV files",
                    "Show me how to merge data",
                    "Create a visualization",
                    "Ask about my data"
                ],
                "confidence": "medium",
                "context": None
            }
        elif 'upload' in message_lower and ('csv' in message_lower or 'file' in message_lower):
            return {
                "response": "Great! I can see you've uploaded CSV files. Here are some suggestions on what you can do next:\n\n## 📊 **Data Analysis Options**\n\n### 1. **Data Cleaning & Validation**\n- Check for missing values and duplicates\n- Validate data types and formats\n- Remove outliers and inconsistencies\n\n### 2. **Data Integration & Merging**\n- Combine multiple CSV files intelligently\n- Match columns across different datasets\n- Create comprehensive merged datasets\n\n### 3. **Statistical Analysis**\n- Generate descriptive statistics\n- Perform correlation analysis\n- Identify trends and patterns\n\n### 4. **Data Visualization**\n- Create scatter plots and line charts\n- Generate histograms and box plots\n- Build interactive dashboards\n\n### 5. **Export & Sharing**\n- Export processed data in various formats\n- Generate reports and summaries\n- Share results with your team\n\n**What specific analysis would you like to perform with your data?**",
                "suggestions": [
                    "Analyze the data structure",
                    "Merge multiple CSV files",
                    "Create visualizations",
                    "Generate statistics"
                ],
                "confidence": "high",
                "context": None
            }
        elif 'merge' in message_lower or 'combine' in message_lower:
            return {
                "response": "I can help you merge CSV files! Here's how:\n\n1. **Upload multiple CSV files** first\n2. **Ask me to merge them** - I'll automatically match columns\n3. **Review the results** and download the merged file\n\nThe system intelligently matches columns based on names and data types.",
                "suggestions": [
                    "Upload files to merge",
                    "Show me the merge process",
                    "Explain column matching",
                    "Download merged data"
                ],
                "confidence": "high",
                "context": None
            }
        elif 'visualize' in message_lower or 'plot' in message_lower or 'chart' in message_lower:
            return {
                "response": "I can create various visualizations from your data:\n\n1. **Scatter plots** - Show relationships between variables\n2. **Histograms** - Display data distributions\n3. **Correlation heatmaps** - Show correlations between columns\n4. **Box plots** - Compare groups and detect outliers\n\nJust upload your data and ask for the type of visualization you want!",
                "suggestions": [
                    "Create a scatter plot",
                    "Show me a histogram",
                    "Generate correlation heatmap",
                    "Make a box plot"
                ],
                "confidence": "high",
                "context": None
            }
        elif 'workflow' in message_lower:
            return {
                "response": "Workflows help you automate data processing steps. You can:\n\n1. **Create workflows** for repetitive tasks\n2. **Add steps** like data cleaning, merging, or analysis\n3. **Run workflows** automatically or on-demand\n4. **Monitor progress** and view results\n\nWould you like to create a new workflow?",
                "suggestions": [
                    "Create a new workflow",
                    "Show my existing workflows",
                    "Explain workflow steps",
                    "Run a workflow"
                ],
                "confidence": "high",
                "context": None
            }
        else:
            return {
                "response": "I'm here to help you with data management and analysis! I can assist with:\n\n• **File uploads and management**\n• **Data merging and processing**\n• **Creating visualizations and charts**\n• **Building automated workflows**\n• **Answering questions about your data**\n\nWhat would you like to work on?",
                "suggestions": [
                    "Upload some files",
                    "Show me how to merge data",
                    "Create a visualization",
                    "Ask about my data"
                ],
                "confidence": "medium",
                "context": None
            }
    
    def _extract_suggestions(self, response: str) -> list[str]:
        """Extract action suggestions from LLM response"""
        suggestions = []
        
        # Common action keywords
        action_keywords = [
            'upload', 'merge', 'visualize', 'plot', 'chart', 'analyze',
            'workflow', 'create', 'show', 'display', 'generate'
        ]
        
        # Simple extraction - look for action words in response
        response_lower = response.lower()
        for keyword in action_keywords:
            if keyword in response_lower:
                suggestions.append(f"Try to {keyword} data")
        
        # Add default suggestions if none found
        if not suggestions:
            suggestions = [
                "Upload some files",
                "Create a visualization",
                "Ask about my data"
            ]
        
        return suggestions[:3]  # Limit to 3 suggestions

# Initialize service
chat_service = GeneralChatService()

@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    """Chat with the AI assistant"""
    try:
        result = chat_service.generate_response(request.message, request.context)
        
        return ChatResponse(
            response=result["response"],
            suggestions=result["suggestions"],
            confidence=result["confidence"],
            context=result.get("context")
        )
        
    except Exception as e:
        logger.error(f"Error in general chat: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to generate response: {str(e)}"
        ) 
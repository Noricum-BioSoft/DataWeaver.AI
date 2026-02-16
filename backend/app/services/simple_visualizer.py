import csv
import json
import io
from typing import Dict, List, Any, Optional
from fastapi import HTTPException

class SimpleVisualizer:
    """Simple visualization service that doesn't require pandas/numpy"""
    
    def __init__(self):
        self.plotly_available = False
        try:
            import plotly.graph_objects as go
            import plotly.express as px
            import plotly.utils
            self.plotly_available = True
        except ImportError:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning("Plotly not available. Using fallback visualization.")
    
    def parse_csv(self, content: bytes) -> Dict[str, Any]:
        """Parse CSV content without pandas"""
        try:
            csv_text = content.decode('utf-8')
            csv_reader = csv.reader(io.StringIO(csv_text))
            
            # Read headers
            headers = next(csv_reader)
            
            # Read rows
            rows = []
            for row in csv_reader:
                if len(row) == len(headers):  # Skip malformed rows
                    # Convert to appropriate types
                    processed_row = []
                    for cell in row:
                        if cell.strip() == '':
                            processed_row.append(None)
                        else:
                            # Try to convert to number
                            try:
                                if '.' in cell:
                                    processed_row.append(float(cell))
                                else:
                                    processed_row.append(int(cell))
                            except ValueError:
                                processed_row.append(cell)
                    rows.append(processed_row)
            
            return {
                'headers': headers,
                'rows': rows,
                'total_rows': len(rows),
                'total_columns': len(headers)
            }
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error parsing CSV: {str(e)}")
    
    def get_numeric_columns(self, data: Dict[str, Any]) -> List[str]:
        """Identify numeric columns"""
        headers = data['headers']
        rows = data['rows']
        numeric_columns = []
        
        for col_idx, header in enumerate(headers):
            numeric_count = 0
            total_count = 0
            
            for row in rows:
                if col_idx < len(row):
                    cell = row[col_idx]
                    if cell is not None:
                        total_count += 1
                        if isinstance(cell, (int, float)):
                            numeric_count += 1
            
            # If more than 70% of values are numeric, consider it numeric
            if total_count > 0 and (numeric_count / total_count) > 0.7:
                numeric_columns.append(header)
        
        return numeric_columns
    
    def create_simple_plot(self, data: Dict[str, Any], plot_type: str = "scatter") -> Dict[str, Any]:
        """Create a simple plot without pandas/plotly"""
        if not self.plotly_available:
            return self._create_fallback_plot(data, plot_type)
        
        try:
            import plotly.graph_objects as go
            import plotly.express as px
            import plotly.utils
            
            headers = data['headers']
            rows = data['rows']
            numeric_cols = self.get_numeric_columns(data)
            
            if plot_type == "scatter" and len(numeric_cols) >= 2:
                x_col = numeric_cols[0]
                y_col = numeric_cols[1]
                
                x_idx = headers.index(x_col)
                y_idx = headers.index(y_col)
                
                x_values = []
                y_values = []
                
                for row in rows:
                    if (x_idx < len(row) and y_idx < len(row) and 
                        isinstance(row[x_idx], (int, float)) and 
                        isinstance(row[y_idx], (int, float))):
                        x_values.append(row[x_idx])
                        y_values.append(row[y_idx])
                
                if len(x_values) > 0:
                    fig = go.Figure(data=go.Scatter(
                        x=x_values,
                        y=y_values,
                        mode='markers',
                        marker=dict(size=8, opacity=0.6)
                    ))
                    fig.update_layout(
                        title=f'Scatter Plot: {x_col} vs {y_col}',
                        xaxis_title=x_col,
                        yaxis_title=y_col
                    )
                    
                    plot_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
                    return {
                        "plot_type": plot_type,
                        "plot_json": plot_json,
                        "columns": headers,
                        "numeric_columns": numeric_cols,
                        "data_shape": [len(rows), len(headers)]
                    }
            
            # Fallback to basic table visualization
            return self._create_fallback_plot(data, plot_type)
            
        except Exception as e:
            return self._create_fallback_plot(data, plot_type)
    
    def _create_fallback_plot(self, data: Dict[str, Any], plot_type: str) -> Dict[str, Any]:
        """Create a fallback plot when plotly is not available"""
        headers = data['headers']
        rows = data['rows']
        numeric_cols = self.get_numeric_columns(data)
        
        # Create a simple HTML table visualization
        table_html = "<table border='1' style='border-collapse: collapse;'>"
        table_html += "<tr>"
        for header in headers:
            table_html += f"<th style='padding: 8px;'>{header}</th>"
        table_html += "</tr>"
        
        # Show first 10 rows
        for i, row in enumerate(rows[:10]):
            table_html += "<tr>"
            for cell in row:
                cell_value = str(cell) if cell is not None else ""
                table_html += f"<td style='padding: 8px;'>{cell_value}</td>"
            table_html += "</tr>"
        
        if len(rows) > 10:
            table_html += "<tr><td colspan='" + str(len(headers)) + "' style='text-align: center; padding: 8px;'>... (" + str(len(rows) - 10) + " more rows)</td></tr>"
        
        table_html += "</table>"
        
        return {
            "plot_type": "table",
            "plot_html": table_html,
            "columns": headers,
            "numeric_columns": numeric_cols,
            "data_shape": [len(rows), len(headers)],
            "message": "Simple table view (advanced visualization requires pandas/plotly)"
        }

# Global instance
simple_visualizer = SimpleVisualizer() 
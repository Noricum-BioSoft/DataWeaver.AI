#!/usr/bin/env python3
"""
DataWeaver.AI Complete Workflow Demo

This script demonstrates the complete workflow:
1. Create a workflow session
2. Upload and merge two CSV files
3. Generate visualizations using the stored merged data
4. Show workflow history and status

This demonstrates the backend's ability to remember data from previous steps.
"""

import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000/api/bio"

def print_step(step_name, description):
    print(f"\n{'='*60}")
    print(f"STEP: {step_name}")
    print(f"DESCRIPTION: {description}")
    print(f"{'='*60}")

def demo_workflow():
    print("🚀 DataWeaver.AI Complete Workflow Demo")
    print("This demo shows how the backend remembers data between workflow steps")
    
    # Step 1: Create workflow session
    print_step("1. Create Workflow Session", "Initialize a new workflow session for data processing")
    
    response = requests.post(f"{BASE_URL}/create-workflow-session")
    if response.status_code != 200:
        print(f"❌ Failed to create session: {response.text}")
        return
    
    session_data = response.json()
    session_id = session_data['session_id']
    print(f"✅ Session created: {session_id}")
    print(f"📝 Message: {session_data['message']}")
    
    # Step 2: Merge files with session
    print_step("2. Merge CSV Files", "Upload and merge two CSV files, storing result in session")
    
    files = {
        'file1': ('measurements.csv', open('sample_data/use-case-merge/measurements.csv', 'rb')),
        'file2': ('sequences.csv', open('sample_data/use-case-merge/sequences.csv', 'rb')),
        'session_id': (None, session_id)
    }
    
    response = requests.post(f"{BASE_URL}/merge-files", files=files)
    if response.status_code != 200:
        print(f"❌ Failed to merge files: {response.text}")
        return
    
    merge_data = response.json()
    print(f"✅ Files merged successfully!")
    print(f"📊 Total rows: {merge_data['totalRows']}")
    print(f"🔗 Matched rows: {merge_data['matchedRows']}")
    print(f"❌ Unmatched rows: {merge_data['unmatchedRows']}")
    print(f"📋 Headers: {', '.join(merge_data['headers'])}")
    print(f"🆔 Session ID: {merge_data['session_id']}")
    print(f"⚙️ Workflow step: {merge_data['workflow_step']}")
    
    # Step 3: Generate visualization using session data
    print_step("3. Generate Visualization", "Create visualization using stored merged data (no file upload needed)")
    
    viz_data = {
        'session_id': session_id,
        'use_session_data': 'true',
        'plot_type': 'scatter'
    }
    
    response = requests.post(f"{BASE_URL}/generate-visualization", data=viz_data)
    if response.status_code != 200:
        print(f"❌ Failed to generate visualization: {response.text}")
        return
    
    viz_result = response.json()
    print(f"✅ Visualization generated successfully!")
    print(f"📈 Plot type: {viz_result['plot_type']}")
    print(f"📊 Data shape: {viz_result['data_shape']}")
    print(f"📋 Columns: {', '.join(viz_result['columns'])}")
    print(f"🔢 Numeric columns: {', '.join(viz_result['numeric_columns'])}")
    print(f"🆔 Session ID: {viz_result['session_id']}")
    print(f"⚙️ Workflow step: {viz_result['workflow_step']}")
    print(f"🖼️ Plot data: [Base64 encoded PNG - {len(viz_result['plot_data'])} characters]")
    
    # Step 4: Show workflow status
    print_step("4. Workflow Status", "Check the complete workflow status and history")
    
    response = requests.get(f"{BASE_URL}/workflow-status/{session_id}")
    if response.status_code != 200:
        print(f"❌ Failed to get workflow status: {response.text}")
        return
    
    status_data = response.json()
    print(f"✅ Workflow status retrieved!")
    print(f"🆔 Session ID: {status_data['session_id']}")
    print(f"📅 Created: {status_data['created_at']}")
    print(f"🔄 Last updated: {status_data['last_updated']}")
    print(f"📊 Has merged data: {status_data['has_merged_data']}")
    print(f"📈 Has visualization data: {status_data['has_visualization_data']}")
    print(f"📝 Steps completed: {len(status_data['steps'])}")
    
    for i, step in enumerate(status_data['steps'], 1):
        print(f"  {i}. {step['type']} at {step['timestamp']}")
        if 'data' in step:
            for key, value in step['data'].items():
                print(f"     {key}: {value}")
    
    # Step 5: Generate another visualization (correlation heatmap)
    print_step("5. Additional Visualization", "Generate a correlation heatmap using the same session data")
    
    viz_data = {
        'session_id': session_id,
        'use_session_data': 'true',
        'plot_type': 'correlation'
    }
    
    response = requests.post(f"{BASE_URL}/generate-visualization", data=viz_data)
    if response.status_code != 200:
        print(f"❌ Failed to generate correlation plot: {response.text}")
        return
    
    viz_result = response.json()
    print(f"✅ Correlation heatmap generated!")
    print(f"📈 Plot type: {viz_result['plot_type']}")
    print(f"📊 Data shape: {viz_result['data_shape']}")
    print(f"🆔 Session ID: {viz_result['session_id']}")
    print(f"⚙️ Workflow step: {viz_result['workflow_step']}")
    
    print_step("DEMO COMPLETE", "The backend successfully remembered and used data from previous workflow steps!")
    print("🎉 Key Features Demonstrated:")
    print("   • Workflow session management")
    print("   • Data persistence between steps")
    print("   • Multiple visualizations from same data")
    print("   • Complete workflow history tracking")
    print("   • No need to re-upload files for subsequent steps")

if __name__ == "__main__":
    try:
        demo_workflow()
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc() 
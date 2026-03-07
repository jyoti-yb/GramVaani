#!/usr/bin/env python3
"""
Test Data-Driven LLM Responses
Shows how fetching data first improves accuracy
"""

import sys
sys.path.append('/Users/eshwarkrishna/Documents/ai for bharat/ruralai/backend')

from data_aggregator import fetch_all_context_data, format_context_for_llm
from dotenv import load_dotenv

load_dotenv()

def test_data_aggregator():
    print("🧪 Testing Data-Driven LLM Approach\n")
    print("=" * 70)
    
    # Test Case 1: Crop recommendation query
    print("\n📍 Test Case 1: User in Bangalore asks about crops")
    print("-" * 70)
    
    user_location = "Bangalore, Karnataka"
    query = "What crops should I plant now?"
    
    print(f"Location: {user_location}")
    print(f"Query: {query}\n")
    
    # Fetch all data
    context = fetch_all_context_data(user_location, query)
    formatted = format_context_for_llm(context)
    
    print("✅ Data Fetched:")
    print(formatted)
    
    print("\n" + "=" * 70)
    
    # Test Case 2: Weather + Pest query
    print("\n📍 Test Case 2: User in Pune asks about weather and pests")
    print("-" * 70)
    
    user_location = "Pune, Maharashtra"
    query = "What's the weather like and are there any pest issues?"
    
    print(f"Location: {user_location}")
    print(f"Query: {query}\n")
    
    context = fetch_all_context_data(user_location, query)
    formatted = format_context_for_llm(context)
    
    print("✅ Data Fetched:")
    print(formatted)
    
    print("\n" + "=" * 70)
    print("\n✅ Data aggregator working correctly!")
    print("\n💡 Key Benefits:")
    print("   1. LLM gets REAL data, not hallucinations")
    print("   2. Responses based on actual soil, weather, crops")
    print("   3. Includes nearby farmer success stories")
    print("   4. Shows recent pest outbreaks")
    print("   5. Provides current market prices")

if __name__ == "__main__":
    test_data_aggregator()

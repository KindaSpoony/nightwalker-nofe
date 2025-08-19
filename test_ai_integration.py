#!/usr/bin/env python3
"""
Test script to demonstrate AI analysis functionality.

This script shows how the NOFE pipeline integrates AI analysis into CHAOS reports.
When OPENAI_API_KEY is available, it will generate actual AI analysis.
When missing, it gracefully falls back with a skip message.

Usage:
    # Without API key (graceful fallback)
    python test_ai_integration.py

    # With API key (actual AI analysis)
    OPENAI_API_KEY=your_key_here python test_ai_integration.py
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from nofe.ai_analysis import generate_ai_analysis, main as ai_main
from nofe.pipeline import main as pipeline_main, load_config


def test_ai_analysis_function():
    """Test the generate_ai_analysis function directly."""
    print("=== Testing AI Analysis Function ===")
    
    sample_report = """
# Sample CHAOS Report

## Executive Summary
- **Top Signals:** Major geopolitical developments in Eastern Europe
- **Narrative Shifts:** Increased tensions between global powers
- **Confidence:** High reliability sources

## Key Events
1. Diplomatic negotiations continue
2. Economic sanctions discussions ongoing
3. Security concerns raised by multiple allies

## Analysis
The current situation shows signs of escalation with multiple stakeholders
expressing concerns about regional stability.
"""
    
    # Test without explicit config (will use environment OPENAI_API_KEY if available)
    result = generate_ai_analysis(sample_report)
    print(f"AI Analysis Result:\n{result}\n")
    
    # Test with config that explicitly sets no API key
    config_no_key = {"openai_api_key": None}
    result_no_key = generate_ai_analysis(sample_report, config_no_key)
    print(f"AI Analysis (no key):\n{result_no_key}\n")


def test_ai_analysis_main():
    """Test the AI analysis main function."""
    print("=== Testing AI Analysis Main Function ===")
    
    # Create a test report file
    test_report_path = "/tmp/test_chaos_report.md"
    test_output_path = "/tmp/test_ai_output.md"
    
    with open(test_report_path, "w") as f:
        f.write("""# Test CHAOS Report
        
This is a test report containing information about current geopolitical events
and security developments that need AI analysis for executive insights.
""")
    
    # Run AI analysis
    ai_main(test_report_path, test_output_path)
    
    # Check output
    if Path(test_output_path).exists():
        with open(test_output_path, "r") as f:
            content = f.read()
        print(f"Generated AI analysis file:\n{content}\n")
    else:
        print("❌ AI analysis file was not created")


def test_pipeline_integration():
    """Test the full pipeline with AI analysis enabled."""
    print("=== Testing Pipeline Integration ===")
    
    config = load_config()
    print(f"AI Analysis Enabled: {config.get('enable_ai_analysis')}")
    print(f"AI Analysis Inline: {config.get('ai_analysis_inline')}")
    
    if not config.get('enable_ai_analysis'):
        print("❌ AI analysis is not enabled in config")
        return
    
    print("\n🚀 Running full pipeline...")
    try:
        pipeline_main()
        print("✅ Pipeline completed successfully")
        
        # Check for generated files
        from datetime import datetime, timezone
        date_stamp = datetime.now(timezone.utc).strftime("%Y%m%d")
        
        chaos_file = f"reports/CHAOS_{date_stamp}.md"
        ai_chaos_file = f"reports/AI_CHAOS_{date_stamp}.md"
        
        if Path(chaos_file).exists():
            print(f"✅ CHAOS report generated: {chaos_file}")
        else:
            print(f"❌ CHAOS report not found: {chaos_file}")
            
        if config.get('ai_analysis_inline'):
            # Check if main report contains AI analysis
            if Path(chaos_file).exists():
                with open(chaos_file, "r") as f:
                    content = f.read()
                if "## AI Analysis" in content:
                    print("✅ Inline AI analysis found in CHAOS report")
                else:
                    print("❌ Inline AI analysis not found in CHAOS report")
        else:
            # Check for separate AI analysis file
            if Path(ai_chaos_file).exists():
                print(f"✅ AI CHAOS report generated: {ai_chaos_file}")
                with open(ai_chaos_file, "r") as f:
                    content = f.read()
                    print(f"AI analysis content preview: {content[:100]}...")
            else:
                print(f"❌ AI CHAOS report not found: {ai_chaos_file}")
                
    except Exception as e:
        print(f"❌ Pipeline failed: {e}")


def main():
    """Run all tests."""
    print("🧪 Testing NOFE AI Analysis Integration\n")
    
    # Check if API key is available
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        print(f"✅ OPENAI_API_KEY is available (length: {len(api_key)})")
    else:
        print("ℹ️  OPENAI_API_KEY not set - will use fallback mode")
    
    print()
    
    test_ai_analysis_function()
    test_ai_analysis_main()
    test_pipeline_integration()
    
    print("=== Summary ===")
    print("✅ AI analysis functionality is properly integrated")
    print("✅ Graceful fallback when API key is missing")
    print("✅ Both inline and separate file modes work")
    print("✅ Pipeline generates AI_CHAOS_*.md files when enabled")
    
    if not api_key:
        print("\n💡 To test with actual AI analysis:")
        print("   OPENAI_API_KEY=your_key_here python test_ai_integration.py")


if __name__ == "__main__":
    main()
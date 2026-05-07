#!/usr/bin/env python3
"""
Test script to verify correlation analysis is working with varied results
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.api.routes.correlation import create_mock_correlation, calculate_risk_assessment, calculate_confidence_analysis

def test_dynamic_correlations():
    """Test that correlation analysis returns varied results"""
    print("🔍 Testing Dynamic Correlation Analysis...")
    
    # Test multiple correlations to ensure variety
    correlation_ids = ["test-1", "test-2", "test-3", "test-4", "test-5"]
    correlations = []
    
    for corr_id in correlation_ids:
        correlation = create_mock_correlation(corr_id)
        correlations.append(correlation)
        print(f"\n📊 Correlation {corr_id}:")
        print(f"  Type: {correlation['correlation_type']}")
        print(f"  Score: {correlation['correlation_score']}")
        print(f"  Confidence: {correlation['confidence']}")
        print(f"  Entities: {len(correlation['entities'])}")
        print(f"  Risk Level: {correlation['risk_assessment']['risk_level']}")
        print(f"  Confidence Level: {correlation['confidence_analysis']['confidence_level']}")
    
    # Check for variety in results
    scores = [c['correlation_score'] for c in correlations]
    confidences = [c['confidence'] for c in correlations]
    types = [c['correlation_type'] for c in correlations]
    
    print(f"\n📈 Analysis Results:")
    print(f"  Score Range: {min(scores):.1f} - {max(scores):.1f}")
    print(f"  Confidence Range: {min(confidences)} - {max(confidences)}")
    print(f"  Unique Types: {set(types)}")
    print(f"  Score Variance: {len(set(scores)) > 1}")
    print(f"  Confidence Variance: {len(set(confidences)) > 1}")
    print(f"  Type Variance: {len(set(types)) > 1}")
    
    # Test risk assessment variety
    risk_levels = [c['risk_assessment']['risk_level'] for c in correlations]
    print(f"  Risk Levels: {set(risk_levels)}")
    
    # Test confidence analysis variety
    confidence_levels = [c['confidence_analysis']['confidence_level'] for c in correlations]
    print(f"  Confidence Levels: {set(confidence_levels)}")
    
    # Overall variety check
    has_variety = (
        len(set(scores)) > 1 and 
        len(set(confidences)) > 1 and 
        len(set(types)) > 1
    )
    
    print(f"\n✅ Variety Test Result: {'PASSED' if has_variety else 'FAILED'}")
    
    if has_variety:
        print("🎉 Correlation analysis is now generating varied results!")
    else:
        print("❌ Correlation analysis is still returning similar results.")
    
    return has_variety

if __name__ == "__main__":
    test_dynamic_correlations()

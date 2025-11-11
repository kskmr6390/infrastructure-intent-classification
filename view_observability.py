#!/usr/bin/env python3
"""
Local Observability Dashboard Viewer
Quick CLI tool to view observability statistics
"""

import os
import sys
import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.core.local_observability import get_local_observability_store


def print_header(title):
    """Print a formatted header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def print_section(title):
    """Print a section header"""
    print(f"\n{title}")
    print("-" * len(title))


def view_statistics(time_range=None):
    """View comprehensive statistics"""
    local_obs = get_local_observability_store({'local_observability': {'enabled': True}})
    stats = local_obs.get_statistics(time_range=time_range)
    
    print_header("LOCAL OBSERVABILITY DASHBOARD")
    
    if not stats:
        print("\n⚠️  No data available yet. Start making predictions to see statistics.")
        return
    
    # Overall Statistics
    print_section(f"📊 Overall Statistics ({stats.get('time_range', 'all_time')})")
    print(f"Total Predictions: {stats.get('total_predictions', 0)}")
    print(f"Average Confidence: {stats.get('average_confidence', 0):.2%}")
    print(f"Out-of-Scope Rate: {stats.get('out_of_scope_rate', 0):.2%} ({stats.get('out_of_scope_count', 0)} queries)")
    print(f"Uncertain Rate: {stats.get('uncertain_rate', 0):.2%} ({stats.get('uncertain_count', 0)} predictions)")
    print(f"Total Feedback: {stats.get('total_feedback', 0)}")
    print(f"Feedback Accuracy: {stats.get('feedback_accuracy', 0):.2%}")
    
    # Confidence Distribution
    print_section("📈 Confidence Distribution")
    conf_dist = stats.get('confidence_distribution', {})
    total = sum(conf_dist.values()) if conf_dist else 1
    
    if conf_dist:
        print(f"Very High (≥90%): {conf_dist.get('very_high', 0):4d} ({conf_dist.get('very_high', 0)/total*100:5.1f}%)")
        print(f"High (70-90%):    {conf_dist.get('high', 0):4d} ({conf_dist.get('high', 0)/total*100:5.1f}%)")
        print(f"Medium (50-70%):  {conf_dist.get('medium', 0):4d} ({conf_dist.get('medium', 0)/total*100:5.1f}%)")
        print(f"Low (<50%):       {conf_dist.get('low', 0):4d} ({conf_dist.get('low', 0)/total*100:5.1f}%)")
    
    # Top Intents
    print_section("🎯 Top 10 Predicted Intents")
    top_intents = stats.get('top_intents', [])
    if top_intents:
        for i, intent_data in enumerate(top_intents, 1):
            intent = intent_data.get('predicted_intent', 'unknown')
            count = intent_data.get('count', 0)
            print(f"{i:2d}. {intent:40s} ({count:4d} predictions)")
    else:
        print("No predictions yet")


def view_recent_predictions(limit=20):
    """View recent predictions"""
    local_obs = get_local_observability_store({'local_observability': {'enabled': True}})
    predictions = local_obs.get_recent_predictions(limit=limit)
    
    print_header(f"RECENT PREDICTIONS (Last {limit})")
    
    if not predictions:
        print("\n⚠️  No predictions available yet.")
        return
    
    for i, pred in enumerate(predictions, 1):
        timestamp = pred.get('timestamp', '')[:19]  # Trim microseconds
        query = pred.get('query', '')[:50]  # Limit length
        intent = pred.get('predicted_intent', '')
        confidence = pred.get('confidence', 0)
        is_oos = pred.get('is_out_of_scope', 0)
        
        status = "🚫" if is_oos else "✅"
        print(f"\n{i:3d}. {status} [{timestamp}]")
        print(f"     Query: {query}")
        print(f"     Intent: {intent} ({confidence:.2%})")


def view_intent_performance():
    """View per-intent performance"""
    local_obs = get_local_observability_store({'local_observability': {'enabled': True}})
    performance = local_obs.get_intent_performance()
    
    print_header("PER-INTENT PERFORMANCE")
    
    if not performance:
        print("\n⚠️  No performance data available yet.")
        return
    
    # Sort by prediction count
    sorted_intents = sorted(performance.items(), 
                           key=lambda x: x[1].get('prediction_count', 0), 
                           reverse=True)
    
    print(f"\n{'Intent':<40} {'Count':>6} {'Avg Conf':>9} {'Uncertain':>10} {'Accuracy':>9}")
    print("-" * 85)
    
    for intent, perf in sorted_intents[:20]:  # Top 20
        count = perf.get('prediction_count', 0)
        avg_conf = perf.get('avg_confidence', 0)
        uncertain = perf.get('uncertain_rate', 0)
        accuracy = perf.get('feedback_accuracy', 0)
        
        acc_str = f"{accuracy:.2%}" if accuracy > 0 else "N/A"
        print(f"{intent:<40} {count:6d} {avg_conf:8.2%} {uncertain:9.2%} {acc_str:>9}")


def export_data():
    """Export all data"""
    local_obs = get_local_observability_store({'local_observability': {'enabled': True}})
    
    print_header("EXPORTING DATA")
    
    exported = local_obs.export_data()
    
    if exported:
        print("\n✅ Data exported successfully:")
        for data_type, file_path in exported.items():
            print(f"  • {data_type}: {file_path}")
    else:
        print("\n⚠️  No data to export or export failed.")


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='View Local Observability Data')
    parser.add_argument('command', nargs='?', default='stats',
                       choices=['stats', 'recent', 'intents', 'export'],
                       help='Command to run (default: stats)')
    parser.add_argument('--time-range', choices=['24h', '7d', '30d'],
                       help='Time range for statistics')
    parser.add_argument('--limit', type=int, default=20,
                       help='Limit for recent predictions (default: 20)')
    
    args = parser.parse_args()
    
    if args.command == 'stats':
        view_statistics(time_range=args.time_range)
    elif args.command == 'recent':
        view_recent_predictions(limit=args.limit)
    elif args.command == 'intents':
        view_intent_performance()
    elif args.command == 'export':
        export_data()
    
    print("\n" + "="*70)
    print("💡 Available commands:")
    print("  python view_observability.py stats [--time-range 24h|7d|30d]")
    print("  python view_observability.py recent [--limit 20]")
    print("  python view_observability.py intents")
    print("  python view_observability.py export")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()


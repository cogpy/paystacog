#!/usr/bin/env python3
"""
Health Badge Updater
Updates health status badges based on orchestration results.
"""

import argparse
import json
import os
from datetime import datetime
from typing import Dict, Any


class HealthBadgeUpdater:
    """Updates health status badges."""
    
    def __init__(self):
        self.badge_colors = {
            'excellent': 'brightgreen',
            'good': 'green', 
            'warning': 'yellow',
            'critical': 'red',
            'unknown': 'lightgrey'
        }
        
    def update_badge(self, results_dir: str, badge_path: str) -> Dict[str, Any]:
        """Update health badge based on results."""
        print("🏷️ Updating health status badge...")
        
        try:
            # Find the summary file
            summary_file = os.path.join(results_dir, 'summary.json')
            if os.path.exists(summary_file):
                with open(summary_file, 'r') as f:
                    summary = json.load(f)
            else:
                # Look for orchestration results
                results_file = os.path.join(results_dir, 'orchestration_results.json')
                if os.path.exists(results_file):
                    with open(results_file, 'r') as f:
                        results = json.load(f)
                    summary = self._extract_summary_from_results(results)
                else:
                    return {'success': False, 'error': 'No results found'}
            
            # Create badge data
            badge_data = self._create_badge_data(summary)
            
            # Ensure badge directory exists
            os.makedirs(os.path.dirname(badge_path), exist_ok=True)
            
            # Save badge data
            with open(badge_path, 'w') as f:
                json.dump(badge_data, f, indent=2)
            
            print(f"✅ Badge updated: {badge_data['message']} ({badge_data['color']})")
            return {'success': True, 'badge_data': badge_data}
            
        except Exception as e:
            print(f"❌ Failed to update badge: {e}")
            return {'success': False, 'error': str(e)}
    
    def _extract_summary_from_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Extract summary from full orchestration results."""
        exec_summary = results.get('executive_summary', {})
        return {
            'status': exec_summary.get('overall_status', 'UNKNOWN'),
            'success_rate': exec_summary.get('success_rate_percent', 0),
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _create_badge_data(self, summary: Dict[str, Any]) -> Dict[str, Any]:
        """Create badge data from summary."""
        status = summary.get('status', 'UNKNOWN').lower()
        success_rate = summary.get('success_rate', 0)
        
        # Map status to badge format
        if status == 'excellent':
            message = f'excellent ({success_rate:.0f}%)'
            color = self.badge_colors['excellent']
        elif status == 'good':
            message = f'good ({success_rate:.0f}%)'
            color = self.badge_colors['good']
        elif status == 'fair' or status == 'warning':
            message = f'warning ({success_rate:.0f}%)'
            color = self.badge_colors['warning']
        elif status == 'needs_attention' or status == 'critical':
            message = f'critical ({success_rate:.0f}%)'
            color = self.badge_colors['critical']
        else:
            message = 'unknown'
            color = self.badge_colors['unknown']
        
        return {
            'schemaVersion': 1,
            'label': 'health',
            'message': message,
            'color': color,
            'namedLogo': 'github',
            'logoColor': 'white',
            'style': 'flat',
            'cacheSeconds': 300,  # Cache for 5 minutes
            'lastUpdated': summary.get('timestamp', datetime.utcnow().isoformat())
        }


def main():
    parser = argparse.ArgumentParser(description='Update OpenCog Health Badge')
    parser.add_argument('--results-dir', required=True, help='Directory containing health results')
    parser.add_argument('--badge-path', required=True, help='Path to save badge JSON')
    
    args = parser.parse_args()
    
    updater = HealthBadgeUpdater()
    result = updater.update_badge(args.results_dir, args.badge_path)
    
    if not result.get('success'):
        print(f"❌ Badge update failed: {result.get('error')}")
        exit(1)


if __name__ == '__main__':
    main()
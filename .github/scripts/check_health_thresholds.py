#!/usr/bin/env python3
"""
Health Threshold Checker
Checks orchestration results against defined health thresholds.
"""

import argparse
import json
import os
import sys
import yaml
from datetime import datetime
from typing import Dict, List, Any, Optional


class HealthThresholdChecker:
    """Checks health metrics against defined thresholds."""
    
    def __init__(self, thresholds_file: str):
        with open(thresholds_file, 'r') as f:
            self.config = yaml.safe_load(f)
        self.thresholds = self.config.get('thresholds', {})
        
    def check_thresholds(self, results_file: str) -> Dict[str, Any]:
        """Check orchestration results against thresholds."""
        print("🔍 Checking health thresholds...")
        
        try:
            with open(results_file, 'r') as f:
                results = json.load(f)
        except Exception as e:
            return {'success': False, 'error': str(e)}
        
        # Extract metrics from results
        metrics = self._extract_metrics(results)
        
        # Check each threshold category
        threshold_results = {}
        overall_status = 'excellent'
        critical_issues = []
        
        for category, thresholds in self.thresholds.items():
            if category in metrics:
                result = self._check_category_threshold(category, metrics[category], thresholds)
                threshold_results[category] = result
                
                # Update overall status (worst case wins)
                if result['level'] == 'critical':
                    overall_status = 'critical'
                    critical_issues.append(result)
                elif result['level'] == 'warning' and overall_status != 'critical':
                    overall_status = 'warning'
                elif result['level'] == 'good' and overall_status not in ['critical', 'warning']:
                    overall_status = 'good'
        
        # Determine if critical issues exist
        has_critical = len(critical_issues) > 0
        
        # Set GitHub Actions output
        self._set_github_output('critical_issues', 'true' if has_critical else 'false')
        self._set_github_output('overall_status', overall_status)
        self._set_github_output('threshold_results', json.dumps(threshold_results))
        
        result = {
            'success': True,
            'overall_status': overall_status,
            'has_critical_issues': has_critical,
            'critical_issues': critical_issues,
            'threshold_results': threshold_results,
            'metrics': metrics,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Save detailed results
        with open('threshold_check_results.json', 'w') as f:
            json.dump(result, f, indent=2)
        
        print(f"🎯 Threshold check completed. Overall status: {overall_status}")
        if has_critical:
            print(f"⚠️ {len(critical_issues)} critical issues detected")
            
        return result
    
    def _extract_metrics(self, results: Dict[str, Any]) -> Dict[str, float]:
        """Extract relevant metrics from orchestration results."""
        exec_summary = results.get('executive_summary', {})
        
        metrics = {
            'success_rate': exec_summary.get('success_rate_percent', 0),
            'execution_time': exec_summary.get('execution_duration_seconds', 0)
        }
        
        # Extract repository activity metrics
        for result in results.get('results', []):
            if result.get('action_type') == 'check_activity_health' and 'activity_health' in result:
                activity = result['activity_health']
                metrics['repository_activity'] = activity.get('activity_score', 0)
                
            elif result.get('action_type') == 'check_documentation_health' and 'documentation_health' in result:
                docs = result['documentation_health'] 
                metrics['documentation_score'] = docs.get('documentation_score', 0)
        
        return metrics
    
    def _check_category_threshold(self, category: str, value: float, thresholds: Dict[str, float]) -> Dict[str, Any]:
        """Check a specific category against its thresholds."""
        
        if value >= thresholds.get('excellent', 95):
            level = 'excellent'
        elif value >= thresholds.get('good', 80):
            level = 'good'
        elif value >= thresholds.get('warning', 60):
            level = 'warning'
        else:
            level = 'critical'
        
        return {
            'category': category,
            'value': value,
            'level': level,
            'threshold_excellent': thresholds.get('excellent'),
            'threshold_good': thresholds.get('good'),
            'threshold_warning': thresholds.get('warning'),
            'threshold_critical': thresholds.get('critical'),
            'message': self._get_threshold_message(category, value, level)
        }
    
    def _get_threshold_message(self, category: str, value: float, level: str) -> str:
        """Generate a human-readable message for the threshold result."""
        category_names = {
            'success_rate': 'Orchestration Success Rate',
            'repository_activity': 'Repository Activity Score', 
            'documentation_score': 'Documentation Coverage',
            'execution_time': 'Execution Time'
        }
        
        category_name = category_names.get(category, category)
        
        if category == 'execution_time':
            # For execution time, lower is better
            if value <= 60:
                return f"{category_name} is excellent at {value:.1f} seconds"
            elif value <= 120:
                return f"{category_name} is good at {value:.1f} seconds"
            elif value <= 300:
                return f"{category_name} shows warning at {value:.1f} seconds"
            else:
                return f"{category_name} is critically slow at {value:.1f} seconds"
        else:
            # For other metrics, higher is better
            if level == 'excellent':
                return f"{category_name} is excellent at {value:.1f}%"
            elif level == 'good':
                return f"{category_name} is good at {value:.1f}%"
            elif level == 'warning':
                return f"{category_name} shows warning at {value:.1f}%"
            else:
                return f"{category_name} is critically low at {value:.1f}%"
    
    def _set_github_output(self, name: str, value: str) -> None:
        """Set GitHub Actions output variable."""
        output_file = os.environ.get('GITHUB_OUTPUT')
        if output_file:
            with open(output_file, 'a') as f:
                f.write(f"{name}={value}\n")
        else:
            print(f"Output: {name}={value}")


def main():
    parser = argparse.ArgumentParser(description='Check OpenCog Health Thresholds')
    parser.add_argument('--results-file', required=True, help='Orchestration results file')
    parser.add_argument('--thresholds-file', required=True, help='Thresholds configuration file')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.thresholds_file):
        print(f"❌ Thresholds file not found: {args.thresholds_file}")
        sys.exit(1)
    
    checker = HealthThresholdChecker(args.thresholds_file)
    result = checker.check_thresholds(args.results_file)
    
    if not result.get('success'):
        print(f"❌ Threshold check failed: {result.get('error')}")
        sys.exit(1)
    
    # Exit with error code if critical issues found
    if result.get('has_critical_issues'):
        sys.exit(2)


if __name__ == '__main__':
    main()
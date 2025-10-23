#!/usr/bin/env python3
"""
OpenCog Reporter
Generates intelligent reports and insights from orchestration execution results.

Implements OpenCog principles:
- Pattern recognition in execution data
- Adaptive learning from outcomes
- Intelligent summary generation
- Context-aware reporting
"""

import argparse
import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional


class OpenCogReporter:
    """
    Generates intelligent reports using OpenCog-inspired analysis.
    """
    
    def __init__(self, run_id: str, timestamp: str):
        self.run_id = run_id
        self.timestamp = timestamp
        
    def generate_report(self, results_file: str) -> Dict[str, Any]:
        """Generate comprehensive orchestration report."""
        print("📊 Generating OpenCog orchestration report...")
        
        try:
            with open(results_file, 'r') as f:
                results = json.load(f)
        except Exception as e:
            print(f"❌ Failed to load results: {e}")
            return {'error': str(e)}
        
        report = {
            'meta': {
                'run_id': self.run_id,
                'timestamp': self.timestamp,
                'generated_at': datetime.utcnow().isoformat(),
                'report_version': '1.0.0'
            },
            'executive_summary': self._generate_executive_summary(results),
            'performance_metrics': self._analyze_performance(results),
            'insights': self._extract_insights(results),
            'recommendations': self._generate_recommendations(results),
            'detailed_results': results
        }
        
        print("✅ Report generation completed")
        return report
    
    def _generate_executive_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate executive summary using OpenCog reasoning."""
        total_actions = results.get('total_actions', 0)
        successful = results.get('successful_actions', 0)
        failed = results.get('failed_actions', 0)
        duration = results.get('duration_seconds', 0)
        
        success_rate = (successful / total_actions * 100) if total_actions > 0 else 0
        
        # Determine overall status using OpenCog-style reasoning
        if success_rate >= 90:
            status = 'EXCELLENT'
            status_emoji = '🟢'
        elif success_rate >= 70:
            status = 'GOOD'
            status_emoji = '🟡'
        elif success_rate >= 50:
            status = 'FAIR'
            status_emoji = '🟠'
        else:
            status = 'NEEDS_ATTENTION'
            status_emoji = '🔴'
        
        summary = {
            'overall_status': status,
            'status_emoji': status_emoji,
            'success_rate_percent': round(success_rate, 1),
            'actions_executed': total_actions,
            'successful_actions': successful,
            'failed_actions': failed,
            'execution_duration_seconds': duration,
            'key_achievements': [],
            'critical_issues': []
        }
        
        # Extract key achievements and issues
        for result in results.get('results', []):
            if result.get('success') and 'analysis' in result:
                summary['key_achievements'].append(f"Completed {result.get('action_type', 'action')}")
            elif not result.get('success'):
                summary['critical_issues'].append({
                    'action': result.get('action_type', 'unknown'),
                    'error': result.get('error', 'Unknown error')
                })
        
        return summary
    
    def _analyze_performance(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze performance metrics using OpenCog pattern recognition."""
        action_performance = {}
        timing_analysis = {}
        
        for result in results.get('results', []):
            action_type = result.get('action_type', 'unknown')
            success = result.get('success', False)
            
            if action_type not in action_performance:
                action_performance[action_type] = {
                    'total': 0,
                    'successful': 0,
                    'failed': 0
                }
            
            action_performance[action_type]['total'] += 1
            if success:
                action_performance[action_type]['successful'] += 1
            else:
                action_performance[action_type]['failed'] += 1
        
        # Calculate success rates for each action type
        for action_type, stats in action_performance.items():
            if stats['total'] > 0:
                stats['success_rate'] = stats['successful'] / stats['total'] * 100
            else:
                stats['success_rate'] = 0
        
        performance = {
            'action_performance': action_performance,
            'timing_analysis': timing_analysis,
            'efficiency_score': self._calculate_efficiency_score(results),
            'reliability_score': self._calculate_reliability_score(results)
        }
        
        return performance
    
    def _extract_insights(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract intelligent insights using OpenCog pattern matching."""
        insights = []
        
        # Analyze organization health
        org_analysis = self._find_organization_analysis(results)
        if org_analysis:
            repo_count = org_analysis.get('total_repositories', 0)
            active_repos = org_analysis.get('repository_breakdown', {}).get('active_repos', 0)
            
            if repo_count > 0:
                activity_ratio = active_repos / repo_count
                if activity_ratio < 0.5:
                    insights.append({
                        'type': 'maintenance_concern',
                        'priority': 'high',
                        'title': 'Low Repository Activity Detected',
                        'description': f'Only {active_repos} out of {repo_count} repositories show recent activity',
                        'recommendation': 'Consider archiving inactive repositories or implementing maintenance schedules'
                    })
                elif activity_ratio > 0.8:
                    insights.append({
                        'type': 'positive_trend',
                        'priority': 'info',
                        'title': 'High Repository Activity',
                        'description': f'{active_repos} out of {repo_count} repositories are actively maintained',
                        'recommendation': 'Continue current maintenance practices'
                    })
        
        # Analyze documentation health
        docs_health = self._find_documentation_health(results)
        if docs_health:
            doc_score = docs_health.get('documentation_score', 0)
            if doc_score < 60:
                insights.append({
                    'type': 'documentation_gap',
                    'priority': 'medium',
                    'title': 'Documentation Needs Improvement',
                    'description': f'Documentation score is {doc_score:.1f}%',
                    'recommendation': 'Focus on improving repository descriptions and README files'
                })
        
        # Analyze security posture
        security_analysis = self._find_security_analysis(results)
        if security_analysis:
            recommendations = security_analysis.get('recommendations', [])
            if recommendations:
                insights.append({
                    'type': 'security_enhancement',
                    'priority': 'high',
                    'title': 'Security Improvements Available',
                    'description': f'{len(recommendations)} security recommendations identified',
                    'recommendation': 'Review and implement security recommendations'
                })
        
        return insights
    
    def _generate_recommendations(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate actionable recommendations using OpenCog planning."""
        recommendations = []
        
        # Performance-based recommendations
        success_rate = (results.get('successful_actions', 0) / 
                       max(results.get('total_actions', 1), 1) * 100)
        
        if success_rate < 80:
            recommendations.append({
                'category': 'orchestration',
                'priority': 'high',
                'title': 'Improve Action Success Rate',
                'description': f'Current success rate is {success_rate:.1f}%',
                'action_items': [
                    'Review failed actions and implement error handling',
                    'Add retry logic for transient failures',
                    'Improve action validation and prerequisites checking'
                ]
            })
        
        # Organization-specific recommendations
        org_analysis = self._find_organization_analysis(results)
        if org_analysis:
            outdated_count = org_analysis.get('repository_breakdown', {}).get('outdated_repos', 0)
            if outdated_count > 5:
                recommendations.append({
                    'category': 'maintenance',
                    'priority': 'medium',
                    'title': 'Repository Maintenance Needed',
                    'description': f'{outdated_count} repositories need attention',
                    'action_items': [
                        'Create maintenance schedule for inactive repositories',
                        'Consider archiving truly unused repositories',
                        'Implement automated dependency updates'
                    ]
                })
        
        # Documentation recommendations
        docs_health = self._find_documentation_health(results)
        if docs_health:
            needs_docs = len(docs_health.get('repositories_needing_docs', []))
            if needs_docs > 0:
                recommendations.append({
                    'category': 'documentation',
                    'priority': 'medium',
                    'title': 'Documentation Enhancement',
                    'description': f'{needs_docs} repositories need better documentation',
                    'action_items': [
                        'Add comprehensive descriptions to repositories',
                        'Ensure all repositories have proper README files',
                        'Implement documentation standards and templates'
                    ]
                })
        
        return recommendations
    
    def _find_organization_analysis(self, results: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find organization analysis in results."""
        for result in results.get('results', []):
            if result.get('action_type') == 'analyze_organization' and 'analysis' in result:
                return result['analysis']
        return None
    
    def _find_documentation_health(self, results: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find documentation health analysis in results."""
        for result in results.get('results', []):
            if result.get('action_type') == 'check_documentation_health' and 'documentation_health' in result:
                return result['documentation_health']
        return None
    
    def _find_security_analysis(self, results: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find security analysis in results."""
        for result in results.get('results', []):
            if result.get('action_type') == 'security_scan_organization' and 'security_analysis' in result:
                return result['security_analysis']
        return None
    
    def _calculate_efficiency_score(self, results: Dict[str, Any]) -> float:
        """Calculate efficiency score based on execution metrics."""
        duration = results.get('duration_seconds', 0)
        total_actions = results.get('total_actions', 1)
        
        # Ideal time per action (in seconds)
        ideal_time_per_action = 10
        actual_time_per_action = duration / total_actions if total_actions > 0 else duration
        
        # Calculate efficiency (higher is better, capped at 100)
        efficiency = min(100, (ideal_time_per_action / max(actual_time_per_action, 1)) * 100)
        return round(efficiency, 1)
    
    def _calculate_reliability_score(self, results: Dict[str, Any]) -> float:
        """Calculate reliability score based on success rates."""
        total_actions = results.get('total_actions', 0)
        successful_actions = results.get('successful_actions', 0)
        
        reliability = (successful_actions / max(total_actions, 1)) * 100
        return round(reliability, 1)


def main():
    parser = argparse.ArgumentParser(description='OpenCog Reporter for PaystackOSS')
    parser.add_argument('--run-id', required=True, help='Workflow run ID')
    parser.add_argument('--timestamp', required=True, help='Execution timestamp')
    parser.add_argument('--results-file', required=True, help='Results file from executor')
    
    args = parser.parse_args()
    
    # Initialize reporter
    reporter = OpenCogReporter(args.run_id, args.timestamp)
    
    # Generate report
    report = reporter.generate_report(args.results_file)
    
    # Save report
    report_filename = f'opencog_report_{args.timestamp}.json'
    with open(report_filename, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Also save a simplified summary
    summary_filename = f'opencog_summary_{args.timestamp}.json'
    summary = {
        'run_id': args.run_id,
        'timestamp': args.timestamp,
        'status': report.get('executive_summary', {}).get('overall_status', 'UNKNOWN'),
        'success_rate': report.get('executive_summary', {}).get('success_rate_percent', 0),
        'total_insights': len(report.get('insights', [])),
        'total_recommendations': len(report.get('recommendations', []))
    }
    
    with open(summary_filename, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"📋 Report saved as {report_filename}")
    print(f"📄 Summary saved as {summary_filename}")
    
    # Print executive summary to console
    exec_summary = report.get('executive_summary', {})
    print(f"\n{exec_summary.get('status_emoji', '❓')} Orchestration Status: {exec_summary.get('overall_status', 'UNKNOWN')}")
    print(f"📈 Success Rate: {exec_summary.get('success_rate_percent', 0)}%")
    print(f"⚡ Actions Executed: {exec_summary.get('actions_executed', 0)}")


if __name__ == '__main__':
    main()
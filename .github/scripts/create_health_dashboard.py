#!/usr/bin/env python3
"""
Health Dashboard Creator
Creates visual health dashboards from OpenCog orchestration results.
"""

import argparse
import json
import os
from datetime import datetime
from typing import Dict, List, Any


class HealthDashboardCreator:
    """Creates health dashboards and visualizations."""
    
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
    def create_dashboard(self, results_file: str) -> Dict[str, Any]:
        """Create comprehensive health dashboard."""
        print("📊 Creating OpenCog health dashboard...")
        
        try:
            with open(results_file, 'r') as f:
                results = json.load(f)
        except Exception as e:
            return {'success': False, 'error': str(e)}
        
        # Create HTML dashboard
        html_content = self._generate_html_dashboard(results)
        
        # Save dashboard
        dashboard_path = os.path.join(self.output_dir, 'index.html')
        with open(dashboard_path, 'w') as f:
            f.write(html_content)
            
        # Create summary JSON for badges
        summary_path = os.path.join(self.output_dir, 'summary.json')
        summary = self._create_summary(results)
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
            
        print(f"✅ Dashboard created at {dashboard_path}")
        return {'success': True, 'dashboard_path': dashboard_path}
    
    def _generate_html_dashboard(self, results: Dict[str, Any]) -> str:
        """Generate HTML dashboard content."""
        exec_summary = results.get('executive_summary', {})
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PaystackOSS Health Dashboard</title>
    <style>
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0; padding: 20px; background: #f6f8fa; color: #24292e;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .status-card {{ 
            background: white; border-radius: 8px; padding: 20px; margin: 15px 0;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1); border-left: 4px solid #28a745;
        }}
        .status-critical {{ border-left-color: #dc3545; }}
        .status-warning {{ border-left-color: #ffc107; }}
        .status-good {{ border-left-color: #28a745; }}
        .metric {{ display: inline-block; margin: 10px 20px 10px 0; }}
        .metric-value {{ font-size: 2em; font-weight: bold; color: #0366d6; }}
        .metric-label {{ color: #586069; font-size: 0.9em; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 PaystackOSS Health Dashboard</h1>
            <p>Powered by OpenCog Orchestration Engine</p>
            <p><strong>Last Updated:</strong> {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
        </div>
        
        <div class="status-card status-{self._get_status_class(exec_summary.get('overall_status', 'unknown'))}">
            <h2>{exec_summary.get('status_emoji', '❓')} Overall Status: {exec_summary.get('overall_status', 'UNKNOWN')}</h2>
            <div class="grid">
                <div class="metric">
                    <div class="metric-value">{exec_summary.get('success_rate_percent', 0)}%</div>
                    <div class="metric-label">Success Rate</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{exec_summary.get('actions_executed', 0)}</div>
                    <div class="metric-label">Actions Executed</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{exec_summary.get('execution_duration_seconds', 0)}s</div>
                    <div class="metric-label">Execution Time</div>
                </div>
            </div>
        </div>
        
        {self._generate_insights_section(results)}
        {self._generate_performance_section(results)}
        {self._generate_recommendations_section(results)}
    </div>
</body>
</html>"""
        return html
    
    def _get_status_class(self, status: str) -> str:
        """Get CSS class for status."""
        status_map = {
            'EXCELLENT': 'good',
            'GOOD': 'good', 
            'FAIR': 'warning',
            'NEEDS_ATTENTION': 'critical'
        }
        return status_map.get(status, 'warning')
    
    def _generate_insights_section(self, results: Dict[str, Any]) -> str:
        """Generate insights section HTML."""
        insights = results.get('insights', [])
        if not insights:
            return ""
            
        html = '<div class="status-card"><h2>💡 Key Insights</h2><ul>'
        for insight in insights[:5]:  # Show top 5 insights
            priority_emoji = {'high': '🔴', 'medium': '🟡', 'low': '🟢', 'info': 'ℹ️'}.get(insight.get('priority', 'info'), 'ℹ️')
            html += f"<li>{priority_emoji} <strong>{insight.get('title', 'Insight')}</strong>: {insight.get('description', '')}</li>"
        html += '</ul></div>'
        return html
    
    def _generate_performance_section(self, results: Dict[str, Any]) -> str:
        """Generate performance section HTML."""
        performance = results.get('performance_metrics', {})
        if not performance:
            return ""
            
        html = '<div class="status-card"><h2>📈 Performance Metrics</h2>'
        html += f'<p><strong>Efficiency Score:</strong> {performance.get("efficiency_score", 0)}</p>'
        html += f'<p><strong>Reliability Score:</strong> {performance.get("reliability_score", 0)}</p>'
        html += '</div>'
        return html
    
    def _generate_recommendations_section(self, results: Dict[str, Any]) -> str:
        """Generate recommendations section HTML."""
        recommendations = results.get('recommendations', [])
        if not recommendations:
            return ""
            
        html = '<div class="status-card"><h2>🎯 Recommendations</h2>'
        for rec in recommendations[:3]:  # Show top 3 recommendations
            html += f'<h3>{rec.get("title", "Recommendation")}</h3>'
            html += f'<p>{rec.get("description", "")}</p>'
            action_items = rec.get("action_items", [])
            if action_items:
                html += '<ul>'
                for item in action_items:
                    html += f'<li>{item}</li>'
                html += '</ul>'
        html += '</div>'
        return html
    
    def _create_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Create summary for external use."""
        exec_summary = results.get('executive_summary', {})
        return {
            'status': exec_summary.get('overall_status', 'UNKNOWN'),
            'success_rate': exec_summary.get('success_rate_percent', 0),
            'actions_executed': exec_summary.get('actions_executed', 0),
            'timestamp': datetime.utcnow().isoformat(),
            'insights_count': len(results.get('insights', [])),
            'recommendations_count': len(results.get('recommendations', []))
        }


def main():
    parser = argparse.ArgumentParser(description='Create OpenCog Health Dashboard')
    parser.add_argument('--results-file', required=True, help='Results file from orchestration')
    parser.add_argument('--output-dir', required=True, help='Output directory for dashboard')
    
    args = parser.parse_args()
    
    creator = HealthDashboardCreator(args.output_dir)
    result = creator.create_dashboard(args.results_file)
    
    if not result.get('success'):
        print(f"❌ Dashboard creation failed: {result.get('error')}")
        exit(1)


if __name__ == '__main__':
    main()
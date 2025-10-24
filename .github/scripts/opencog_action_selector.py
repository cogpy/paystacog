#!/usr/bin/env python3
"""
OpenCog Action Selector
Implements OpenCog-inspired action selection and planning for PaystackOSS orchestration.

Based on OpenCog principles:
- Goal-directed behavior selection
- Context-aware action planning
- Multi-objective optimization
- Adaptive learning from outcomes
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import requests


class OpenCogActionSelector:
    """
    OpenCog-inspired action selection engine for GitHub orchestration.
    Implements goal-directed planning and context-aware decision making.
    """
    
    def __init__(self, org_name: str, github_token: str):
        self.org_name = org_name
        self.github_token = github_token
        self.headers = {
            'Authorization': f'token {github_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        self.base_url = 'https://api.github.com'
        
    def get_organization_context(self) -> Dict[str, Any]:
        """Gather contextual information about the organization."""
        print("🧠 Analyzing organization context...")
        
        try:
            # Get organization info
            org_response = requests.get(f'{self.base_url}/orgs/{self.org_name}', 
                                      headers=self.headers)
            org_data = org_response.json() if org_response.status_code == 200 else {}
            
            # Get repositories
            repos_response = requests.get(f'{self.base_url}/orgs/{self.org_name}/repos',
                                        headers=self.headers, params={'per_page': 100})
            repos_data = repos_response.json() if repos_response.status_code == 200 else []
            
            context = {
                'organization': org_data,
                'repositories': repos_data,
                'total_repos': len(repos_data),
                'analysis_time': datetime.utcnow().isoformat(),
                'health_metrics': self._calculate_health_metrics(repos_data)
            }
            
            print(f"📊 Found {len(repos_data)} repositories in {self.org_name}")
            return context
            
        except Exception as e:
            print(f"❌ Error gathering context: {e}")
            return {'error': str(e), 'repositories': []}
    
    def _calculate_health_metrics(self, repos: List[Dict]) -> Dict[str, Any]:
        """Calculate health metrics for the organization."""
        if not repos:
            return {}
            
        metrics = {
            'total_repos': len(repos),
            'active_repos': 0,
            'outdated_repos': 0,
            'security_alerts': 0,
            'needs_documentation': 0,
            'languages': {},
            'last_activity_stats': {}
        }
        
        now = datetime.utcnow()
        
        for repo in repos:
            # Check if repo is active (updated in last 30 days)
            updated_at = datetime.fromisoformat(repo['updated_at'].replace('Z', '+00:00'))
            days_since_update = (now - updated_at.replace(tzinfo=None)).days
            
            if days_since_update <= 30:
                metrics['active_repos'] += 1
            elif days_since_update > 90:
                metrics['outdated_repos'] += 1
                
            # Track languages
            if repo.get('language'):
                lang = repo['language']
                metrics['languages'][lang] = metrics['languages'].get(lang, 0) + 1
                
            # Check for missing descriptions (documentation indicator)
            if not repo.get('description') or len(repo.get('description', '')) < 10:
                metrics['needs_documentation'] += 1
                
        return metrics
    
    def select_actions(self, action_type: str, target_repos: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        OpenCog-style action selection based on goals, context, and priorities.
        """
        print(f"🎯 Selecting actions for type: {action_type}")
        
        actions = []
        repos = context.get('repositories', [])
        health_metrics = context.get('health_metrics', {})
        
        if action_type == 'analyze':
            actions.extend(self._select_analysis_actions(repos, health_metrics))
        elif action_type == 'sync':
            actions.extend(self._select_sync_actions(repos, health_metrics))
        elif action_type == 'health_check':
            actions.extend(self._select_health_actions(repos, health_metrics))
        elif action_type == 'security_scan':
            actions.extend(self._select_security_actions(repos, health_metrics))
        else:
            # Default: comprehensive analysis
            actions.extend(self._select_comprehensive_actions(repos, health_metrics))
            
        # Apply target repository filter
        if target_repos != 'all':
            target_list = [repo.strip() for repo in target_repos.split(',')]
            actions = [action for action in actions 
                      if action.get('target_repo', 'all') in target_list or action.get('target_repo') == 'all']
        
        # Prioritize actions using OpenCog-style utility calculation
        prioritized_actions = self._prioritize_actions(actions, context)
        
        print(f"✅ Selected {len(prioritized_actions)} prioritized actions")
        return prioritized_actions
    
    def _select_analysis_actions(self, repos: List[Dict], metrics: Dict) -> List[Dict[str, Any]]:
        """Select actions for repository analysis."""
        actions = [
            {
                'type': 'analyze_organization',
                'priority': 1.0,
                'goal': 'understanding',
                'target_repo': 'all',
                'parameters': {
                    'include_metrics': True,
                    'include_trends': True
                }
            }
        ]
        
        # Analyze individual repositories that haven't been updated recently
        for repo in repos:
            updated_at = datetime.fromisoformat(repo['updated_at'].replace('Z', '+00:00'))
            days_since_update = (datetime.utcnow() - updated_at.replace(tzinfo=None)).days
            
            if days_since_update > 30:
                actions.append({
                    'type': 'analyze_repository',
                    'priority': 0.8,
                    'goal': 'maintenance',
                    'target_repo': repo['name'],
                    'parameters': {
                        'repo_name': repo['name'],
                        'days_since_update': days_since_update,
                        'check_issues': True,
                        'check_security': True
                    }
                })
                
        return actions
    
    def _select_sync_actions(self, repos: List[Dict], metrics: Dict) -> List[Dict[str, Any]]:
        """Select synchronization actions."""
        actions = [
            {
                'type': 'sync_organization_profile',
                'priority': 1.0,
                'goal': 'consistency',
                'target_repo': 'all',
                'parameters': {
                    'update_statistics': True,
                    'refresh_repo_list': True
                }
            }
        ]
        
        return actions
    
    def _select_health_actions(self, repos: List[Dict], metrics: Dict) -> List[Dict[str, Any]]:
        """Select health check actions."""
        actions = []
        
        # Check repositories needing documentation
        if metrics.get('needs_documentation', 0) > 0:
            actions.append({
                'type': 'check_documentation_health',
                'priority': 0.9,
                'goal': 'quality',
                'target_repo': 'all',
                'parameters': {
                    'missing_docs_count': metrics['needs_documentation']
                }
            })
        
        # Check for outdated repositories
        if metrics.get('outdated_repos', 0) > 0:
            actions.append({
                'type': 'check_activity_health',
                'priority': 0.7,
                'goal': 'maintenance',
                'target_repo': 'all',
                'parameters': {
                    'outdated_count': metrics['outdated_repos']
                }
            })
            
        return actions
    
    def _select_security_actions(self, repos: List[Dict], metrics: Dict) -> List[Dict[str, Any]]:
        """Select security-focused actions."""
        actions = [
            {
                'type': 'security_scan_organization',
                'priority': 1.0,
                'goal': 'security',
                'target_repo': 'all',
                'parameters': {
                    'scan_vulnerabilities': True,
                    'check_permissions': True,
                    'audit_access': True
                }
            }
        ]
        
        return actions
    
    def _select_comprehensive_actions(self, repos: List[Dict], metrics: Dict) -> List[Dict[str, Any]]:
        """Select comprehensive analysis actions."""
        actions = []
        actions.extend(self._select_analysis_actions(repos, metrics))
        actions.extend(self._select_sync_actions(repos, metrics))
        actions.extend(self._select_health_actions(repos, metrics))
        
        return actions
    
    def _prioritize_actions(self, actions: List[Dict[str, Any]], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        OpenCog-style action prioritization using utility theory.
        """
        # Calculate utility for each action based on multiple factors
        for action in actions:
            utility = action.get('priority', 0.5)
            
            # Boost utility for security-related actions
            if action.get('goal') == 'security':
                utility *= 1.3
                
            # Boost utility for maintenance actions if many repos are outdated
            health_metrics = context.get('health_metrics', {})
            if action.get('goal') == 'maintenance' and health_metrics.get('outdated_repos', 0) > 3:
                utility *= 1.2
                
            # Boost utility for understanding actions if this is a new run
            if action.get('goal') == 'understanding':
                utility *= 1.1
                
            action['calculated_utility'] = utility
        
        # Sort by calculated utility (descending)
        return sorted(actions, key=lambda x: x.get('calculated_utility', 0), reverse=True)


def main():
    parser = argparse.ArgumentParser(description='OpenCog Action Selector for PaystackOSS')
    parser.add_argument('--action-type', required=True, help='Type of action to select')
    parser.add_argument('--target-repos', default='all', help='Target repositories')
    parser.add_argument('--org', required=True, help='GitHub organization name')
    
    args = parser.parse_args()
    
    github_token = os.environ.get('GITHUB_TOKEN')
    if not github_token:
        print("❌ GITHUB_TOKEN environment variable is required")
        sys.exit(1)
    
    # Initialize OpenCog action selector
    selector = OpenCogActionSelector(args.org, github_token)
    
    # Gather organizational context
    context = selector.get_organization_context()
    
    # Select actions using OpenCog principles
    actions = selector.select_actions(args.action_type, args.target_repos, context)
    
    # Save actions and context for execution
    output_data = {
        'timestamp': datetime.utcnow().isoformat(),
        'context': context,
        'selected_actions': actions,
        'action_type': args.action_type,
        'target_repos': args.target_repos,
        'org_name': args.org
    }
    
    with open('opencog_actions.json', 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"🎯 Action selection completed. {len(actions)} actions selected and saved.")


if __name__ == '__main__':
    main()
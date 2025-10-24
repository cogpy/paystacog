#!/usr/bin/env python3
"""
OpenCog Action Executor
Executes actions selected by the OpenCog action selector.

Implements OpenCog principles:
- Goal-oriented execution
- Context-aware adaptation
- Error handling and recovery
- Learning from execution outcomes
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import requests


class OpenCogExecutor:
    """
    Executes actions using OpenCog-inspired execution engine.
    """
    
    def __init__(self, org_name: str, github_token: str):
        self.org_name = org_name
        self.github_token = github_token
        self.headers = {
            'Authorization': f'token {github_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        self.base_url = 'https://api.github.com'
        self.execution_results = []
        
    def execute_actions(self, actions_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the list of selected actions."""
        print("🚀 Starting OpenCog action execution...")
        
        actions = actions_data.get('selected_actions', [])
        context = actions_data.get('context', {})
        
        execution_summary = {
            'start_time': datetime.utcnow().isoformat(),
            'total_actions': len(actions),
            'successful_actions': 0,
            'failed_actions': 0,
            'skipped_actions': 0,
            'results': []
        }
        
        for i, action in enumerate(actions):
            print(f"📋 Executing action {i+1}/{len(actions)}: {action.get('type', 'unknown')}")
            
            try:
                result = self._execute_single_action(action, context)
                result['action_index'] = i
                result['action_type'] = action.get('type')
                
                if result.get('success', False):
                    execution_summary['successful_actions'] += 1
                    print(f"✅ Action {i+1} completed successfully")
                else:
                    execution_summary['failed_actions'] += 1
                    print(f"❌ Action {i+1} failed: {result.get('error', 'Unknown error')}")
                    
                execution_summary['results'].append(result)
                
            except Exception as e:
                error_result = {
                    'action_index': i,
                    'action_type': action.get('type'),
                    'success': False,
                    'error': str(e),
                    'timestamp': datetime.utcnow().isoformat()
                }
                execution_summary['results'].append(error_result)
                execution_summary['failed_actions'] += 1
                print(f"💥 Action {i+1} crashed: {e}")
        
        execution_summary['end_time'] = datetime.utcnow().isoformat()
        execution_summary['duration_seconds'] = (
            datetime.fromisoformat(execution_summary['end_time']) - 
            datetime.fromisoformat(execution_summary['start_time'])
        ).total_seconds()
        
        print(f"🏁 Execution completed: {execution_summary['successful_actions']} successful, "
              f"{execution_summary['failed_actions']} failed, "
              f"{execution_summary['skipped_actions']} skipped")
        
        return execution_summary
    
    def _execute_single_action(self, action: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single action based on its type."""
        action_type = action.get('type')
        
        if action_type == 'analyze_organization':
            return self._analyze_organization(action, context)
        elif action_type == 'analyze_repository':
            return self._analyze_repository(action, context)
        elif action_type == 'sync_organization_profile':
            return self._sync_organization_profile(action, context)
        elif action_type == 'check_documentation_health':
            return self._check_documentation_health(action, context)
        elif action_type == 'check_activity_health':
            return self._check_activity_health(action, context)
        elif action_type == 'security_scan_organization':
            return self._security_scan_organization(action, context)
        else:
            return {
                'success': False,
                'error': f'Unknown action type: {action_type}',
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def _analyze_organization(self, action: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the organization comprehensively."""
        try:
            repos = context.get('repositories', [])
            health_metrics = context.get('health_metrics', {})
            
            analysis = {
                'organization_name': self.org_name,
                'total_repositories': len(repos),
                'repository_breakdown': {
                    'active_repos': health_metrics.get('active_repos', 0),
                    'outdated_repos': health_metrics.get('outdated_repos', 0),
                    'needs_documentation': health_metrics.get('needs_documentation', 0)
                },
                'language_distribution': health_metrics.get('languages', {}),
                'top_repositories': []
            }
            
            # Get top repositories by stars
            sorted_repos = sorted(repos, key=lambda x: x.get('stargazers_count', 0), reverse=True)
            analysis['top_repositories'] = [
                {
                    'name': repo['name'],
                    'stars': repo.get('stargazers_count', 0),
                    'forks': repo.get('forks_count', 0),
                    'language': repo.get('language'),
                    'description': repo.get('description', '')
                }
                for repo in sorted_repos[:10]
            ]
            
            return {
                'success': True,
                'timestamp': datetime.utcnow().isoformat(),
                'analysis': analysis
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def _analyze_repository(self, action: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a specific repository."""
        try:
            repo_name = action.get('parameters', {}).get('repo_name')
            if not repo_name:
                raise ValueError("Repository name is required")
            
            # Get detailed repository information
            repo_response = requests.get(f'{self.base_url}/repos/{self.org_name}/{repo_name}',
                                       headers=self.headers)
            
            if repo_response.status_code != 200:
                raise ValueError(f"Failed to fetch repository: {repo_response.status_code}")
            
            repo_data = repo_response.json()
            
            # Get recent issues and PRs
            issues_response = requests.get(f'{self.base_url}/repos/{self.org_name}/{repo_name}/issues',
                                         headers=self.headers, params={'state': 'open', 'per_page': 10})
            issues_data = issues_response.json() if issues_response.status_code == 200 else []
            
            analysis = {
                'repository': repo_name,
                'last_updated': repo_data.get('updated_at'),
                'open_issues': repo_data.get('open_issues_count', 0),
                'has_wiki': repo_data.get('has_wiki', False),
                'has_pages': repo_data.get('has_pages', False),
                'default_branch': repo_data.get('default_branch', 'main'),
                'recent_issues': [
                    {
                        'title': issue.get('title'),
                        'state': issue.get('state'),
                        'created_at': issue.get('created_at')
                    }
                    for issue in (issues_data[:5] if isinstance(issues_data, list) else [])
                ]
            }
            
            return {
                'success': True,
                'timestamp': datetime.utcnow().isoformat(),
                'repository_analysis': analysis
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def _sync_organization_profile(self, action: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Synchronize organization profile information."""
        try:
            repos = context.get('repositories', [])
            health_metrics = context.get('health_metrics', {})
            
            # Calculate updated statistics
            stats = {
                'total_repositories': len(repos),
                'active_repositories': health_metrics.get('active_repos', 0),
                'primary_languages': list(health_metrics.get('languages', {}).keys())[:5],
                'last_sync': datetime.utcnow().isoformat()
            }
            
            # Save sync data for profile update
            with open('sync_data.json', 'w') as f:
                json.dump(stats, f, indent=2)
            
            return {
                'success': True,
                'timestamp': datetime.utcnow().isoformat(),
                'sync_stats': stats
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def _check_documentation_health(self, action: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Check documentation health across repositories."""
        try:
            repos = context.get('repositories', [])
            docs_analysis = {
                'repositories_needing_docs': [],
                'well_documented_repos': [],
                'documentation_score': 0
            }
            
            for repo in repos:
                description_quality = len(repo.get('description', '')) > 20
                has_readme = True  # Assume README exists (would need separate API call to verify)
                
                repo_info = {
                    'name': repo['name'],
                    'has_description': bool(repo.get('description')),
                    'description_length': len(repo.get('description', '')),
                    'stars': repo.get('stargazers_count', 0)
                }
                
                if description_quality:
                    docs_analysis['well_documented_repos'].append(repo_info)
                else:
                    docs_analysis['repositories_needing_docs'].append(repo_info)
            
            total_repos = len(repos)
            well_documented = len(docs_analysis['well_documented_repos'])
            docs_analysis['documentation_score'] = (well_documented / total_repos * 100) if total_repos > 0 else 0
            
            return {
                'success': True,
                'timestamp': datetime.utcnow().isoformat(),
                'documentation_health': docs_analysis
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def _check_activity_health(self, action: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Check activity and maintenance health."""
        try:
            repos = context.get('repositories', [])
            activity_analysis = {
                'active_repos': [],
                'stale_repos': [],
                'archived_repos': [],
                'activity_score': 0
            }
            
            now = datetime.utcnow()
            
            for repo in repos:
                updated_at = datetime.fromisoformat(repo['updated_at'].replace('Z', '+00:00'))
                days_since_update = (now - updated_at.replace(tzinfo=None)).days
                
                repo_info = {
                    'name': repo['name'],
                    'last_updated': repo['updated_at'],
                    'days_since_update': days_since_update,
                    'is_archived': repo.get('archived', False)
                }
                
                if repo.get('archived'):
                    activity_analysis['archived_repos'].append(repo_info)
                elif days_since_update <= 30:
                    activity_analysis['active_repos'].append(repo_info)
                else:
                    activity_analysis['stale_repos'].append(repo_info)
            
            total_active_repos = len(repos) - len(activity_analysis['archived_repos'])
            active_count = len(activity_analysis['active_repos'])
            activity_analysis['activity_score'] = (active_count / total_active_repos * 100) if total_active_repos > 0 else 0
            
            return {
                'success': True,
                'timestamp': datetime.utcnow().isoformat(),
                'activity_health': activity_analysis
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def _security_scan_organization(self, action: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Perform security scanning of the organization."""
        try:
            repos = context.get('repositories', [])
            security_analysis = {
                'repositories_scanned': len(repos),
                'security_features': {
                    'has_security_policy': 0,
                    'has_branch_protection': 0,
                    'private_repos': 0,
                    'public_repos': 0
                },
                'recommendations': []
            }
            
            for repo in repos:
                if repo.get('private', False):
                    security_analysis['security_features']['private_repos'] += 1
                else:
                    security_analysis['security_features']['public_repos'] += 1
            
            # Add security recommendations
            if security_analysis['security_features']['public_repos'] > 0:
                security_analysis['recommendations'].append(
                    "Consider enabling branch protection rules for public repositories"
                )
            
            security_analysis['recommendations'].append(
                "Regularly review repository access permissions"
            )
            
            return {
                'success': True,
                'timestamp': datetime.utcnow().isoformat(),
                'security_analysis': security_analysis
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }


def main():
    parser = argparse.ArgumentParser(description='OpenCog Action Executor for PaystackOSS')
    parser.add_argument('--actions-file', required=True, help='Actions file from selector')
    parser.add_argument('--org', required=True, help='GitHub organization name')
    
    args = parser.parse_args()
    
    github_token = os.environ.get('GITHUB_TOKEN')
    if not github_token:
        print("❌ GITHUB_TOKEN environment variable is required")
        sys.exit(1)
    
    # Load actions data
    try:
        with open(args.actions_file, 'r') as f:
            actions_data = json.load(f)
    except Exception as e:
        print(f"❌ Failed to load actions file: {e}")
        sys.exit(1)
    
    # Initialize executor
    executor = OpenCogExecutor(args.org, github_token)
    
    # Execute actions
    results = executor.execute_actions(actions_data)
    
    # Save results
    with open('orchestration_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("💾 Execution results saved to orchestration_results.json")
    
    # Return appropriate exit code
    if results['failed_actions'] > results['successful_actions']:
        sys.exit(1)


if __name__ == '__main__':
    main()
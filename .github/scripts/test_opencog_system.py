#!/usr/bin/env python3
"""
Test script for OpenCog orchestration system components.
Tests the system logic without requiring GitHub API access.
"""

import json
import os
import sys
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

# Add scripts directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from opencog_action_selector import OpenCogActionSelector
from opencog_executor import OpenCogExecutor
from opencog_reporter import OpenCogReporter
from create_health_dashboard import HealthDashboardCreator
from check_health_thresholds import HealthThresholdChecker


def create_mock_repo_data():
    """Create mock repository data for testing."""
    return [
        {
            'name': 'sample-react',
            'description': 'A sample React application for demonstrating Paystack integration',
            'language': 'JavaScript',
            'stargazers_count': 150,
            'forks_count': 45,
            'updated_at': datetime.utcnow().isoformat() + 'Z',
            'private': False,
            'archived': False,
            'open_issues_count': 5
        },
        {
            'name': 'paystack-python',
            'description': 'Python library for Paystack API',
            'language': 'Python',
            'stargazers_count': 320,
            'forks_count': 78,
            'updated_at': (datetime.utcnow() - timedelta(days=45)).isoformat() + 'Z',
            'private': False,
            'archived': False,
            'open_issues_count': 12
        },
        {
            'name': 'old-project',
            'description': '',
            'language': 'JavaScript',
            'stargazers_count': 5,
            'forks_count': 1,
            'updated_at': (datetime.utcnow() - timedelta(days=120)).isoformat() + 'Z',
            'private': False,
            'archived': False,
            'open_issues_count': 0
        }
    ]


def create_mock_context():
    """Create mock organizational context."""
    repos = create_mock_repo_data()
    return {
        'organization': {'login': 'PaystackOSS', 'public_repos': len(repos)},
        'repositories': repos,
        'total_repos': len(repos),
        'analysis_time': datetime.utcnow().isoformat(),
        'health_metrics': {
            'total_repos': len(repos),
            'active_repos': 1,
            'outdated_repos': 2,
            'needs_documentation': 1,
            'languages': {'JavaScript': 2, 'Python': 1}
        }
    }


def test_action_selector():
    """Test the OpenCog action selector."""
    print("🧪 Testing OpenCog Action Selector...")
    
    # Mock the GitHub API calls
    with patch('requests.get') as mock_get:
        # Mock organization response
        mock_org_response = MagicMock()
        mock_org_response.status_code = 200
        mock_org_response.json.return_value = {'login': 'PaystackOSS', 'public_repos': 3}
        
        # Mock repositories response  
        mock_repos_response = MagicMock()
        mock_repos_response.status_code = 200
        mock_repos_response.json.return_value = create_mock_repo_data()
        
        mock_get.side_effect = [mock_org_response, mock_repos_response]
        
        # Test action selector
        selector = OpenCogActionSelector('PaystackOSS', 'fake_token')
        context = selector.get_organization_context()
        actions = selector.select_actions('analyze', 'all', context)
        
        print(f"✅ Action selector returned {len(actions)} actions")
        print(f"✅ Context includes {context.get('total_repos', 0)} repositories")
        
        assert len(actions) > 0, "Should select at least one action"
        assert context['total_repos'] == 3, "Should have 3 repositories"
        
        return context, actions


def test_executor(context, actions):
    """Test the OpenCog executor."""
    print("🧪 Testing OpenCog Executor...")
    
    # Create actions data structure
    actions_data = {
        'timestamp': datetime.utcnow().isoformat(),
        'context': context,
        'selected_actions': actions,
        'action_type': 'analyze',
        'target_repos': 'all',
        'org_name': 'PaystackOSS'
    }
    
    # Mock the GitHub API calls for executor
    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = create_mock_repo_data()[0]  # Return first repo
        mock_get.return_value = mock_response
        
        # Test executor
        executor = OpenCogExecutor('PaystackOSS', 'fake_token')
        results = executor.execute_actions(actions_data)
        
        print(f"✅ Executor completed {results.get('successful_actions', 0)} successful actions")
        print(f"✅ Execution took {results.get('duration_seconds', 0):.2f} seconds")
        
        assert results['total_actions'] == len(actions), "Should track all actions"
        assert 'results' in results, "Should include detailed results"
        
        return results


def test_reporter(results):
    """Test the OpenCog reporter."""
    print("🧪 Testing OpenCog Reporter...")
    
    reporter = OpenCogReporter('test_run_123', datetime.utcnow().strftime('%Y%m%d_%H%M%S'))
    
    # Save results to temporary file
    results_file = '/tmp/test_results.json'
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    # Generate report
    report = reporter.generate_report(results_file)
    
    print(f"✅ Report generated with status: {report.get('executive_summary', {}).get('overall_status', 'UNKNOWN')}")
    print(f"✅ Report includes {len(report.get('insights', []))} insights")
    print(f"✅ Report includes {len(report.get('recommendations', []))} recommendations")
    
    assert 'executive_summary' in report, "Should include executive summary"
    assert 'insights' in report, "Should include insights"
    assert 'recommendations' in report, "Should include recommendations"
    
    # Clean up
    os.remove(results_file)
    
    return report


def test_health_dashboard(results):
    """Test the health dashboard creator."""
    print("🧪 Testing Health Dashboard Creator...")
    
    # Create temporary results file
    results_file = '/tmp/test_dashboard_results.json'
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    # Test dashboard creator
    creator = HealthDashboardCreator('/tmp/test_dashboard')
    result = creator.create_dashboard(results_file)
    
    print(f"✅ Dashboard creation: {'Success' if result.get('success') else 'Failed'}")
    
    assert result.get('success'), "Dashboard creation should succeed"
    assert os.path.exists('/tmp/test_dashboard/index.html'), "Should create HTML dashboard"
    
    # Clean up
    os.remove(results_file)
    
    return result


def test_threshold_checker(results):
    """Test the health threshold checker."""
    print("🧪 Testing Health Threshold Checker...")
    
    # Create temporary results file
    results_file = '/tmp/test_threshold_results.json'
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    # Test threshold checker
    thresholds_file = '.github/config/health_thresholds.yml'
    if os.path.exists(thresholds_file):
        checker = HealthThresholdChecker(thresholds_file)
        result = checker.check_thresholds(results_file)
        
        print(f"✅ Threshold check: {'Success' if result.get('success') else 'Failed'}")
        print(f"✅ Overall status: {result.get('overall_status', 'UNKNOWN')}")
        
        assert result.get('success'), "Threshold check should succeed"
    else:
        print("⚠️ Skipping threshold check - config file not found")
    
    # Clean up
    os.remove(results_file)


def run_integration_test():
    """Run full integration test of the OpenCog orchestration system."""
    print("🚀 Running OpenCog Orchestration Integration Test\n")
    
    try:
        # Test action selector
        context, actions = test_action_selector()
        print()
        
        # Test executor
        results = test_executor(context, actions)
        print()
        
        # Test reporter
        report = test_reporter(results)
        print()
        
        # Test health dashboard
        test_health_dashboard(results)
        print()
        
        # Test threshold checker
        test_threshold_checker(results)
        print()
        
        print("🎉 All OpenCog orchestration tests passed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = run_integration_test()
    sys.exit(0 if success else 1)
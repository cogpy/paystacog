#!/usr/bin/env python3
"""
Profile Update Script
Updates the PaystackOSS organization profile based on OpenCog orchestration results.

Implements OpenCog principles:
- Context-aware content generation
- Intelligent information synthesis
- Adaptive profile optimization
"""

import argparse
import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional
import re


class ProfileUpdater:
    """
    Updates organization profile using OpenCog-inspired intelligence.
    """
    
    def __init__(self):
        self.timestamp = datetime.utcnow()
        
    def update_profile(self, results_file: str, profile_path: str) -> Dict[str, Any]:
        """Update organization profile based on orchestration results."""
        print("🔄 Updating organization profile with OpenCog insights...")
        
        try:
            # Load orchestration results
            with open(results_file, 'r') as f:
                results = json.load(f)
                
            # Read current profile
            with open(profile_path, 'r') as f:
                current_profile = f.read()
                
        except Exception as e:
            print(f"❌ Failed to load files: {e}")
            return {'success': False, 'error': str(e)}
        
        # Extract insights from results
        insights = self._extract_profile_insights(results)
        
        # Generate updated profile content
        updated_profile = self._generate_updated_profile(current_profile, insights)
        
        # Save updated profile if changes were made
        if updated_profile != current_profile:
            try:
                with open(profile_path, 'w') as f:
                    f.write(updated_profile)
                print("✅ Profile updated successfully")
                return {
                    'success': True,
                    'changes_made': True,
                    'insights_applied': len(insights),
                    'timestamp': self.timestamp.isoformat()
                }
            except Exception as e:
                print(f"❌ Failed to save profile: {e}")
                return {'success': False, 'error': str(e)}
        else:
            print("ℹ️ No profile updates needed")
            return {
                'success': True,
                'changes_made': False,
                'insights_applied': 0,
                'timestamp': self.timestamp.isoformat()
            }
    
    def _extract_profile_insights(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Extract insights relevant for profile updates."""
        insights = {
            'repository_stats': {},
            'activity_metrics': {},
            'language_distribution': {},
            'top_repositories': [],
            'health_score': 0,
            'last_analysis': self.timestamp.isoformat()
        }
        
        # Find organization analysis
        for result in results.get('results', []):
            if result.get('action_type') == 'analyze_organization' and 'analysis' in result:
                analysis = result['analysis']
                insights['repository_stats'] = {
                    'total': analysis.get('total_repositories', 0),
                    'active': analysis.get('repository_breakdown', {}).get('active_repos', 0),
                    'outdated': analysis.get('repository_breakdown', {}).get('outdated_repos', 0)
                }
                insights['language_distribution'] = analysis.get('language_distribution', {})
                insights['top_repositories'] = analysis.get('top_repositories', [])
                
            elif result.get('action_type') == 'check_activity_health' and 'activity_health' in result:
                activity = result['activity_health']
                insights['activity_metrics'] = {
                    'activity_score': activity.get('activity_score', 0),
                    'active_count': len(activity.get('active_repos', [])),
                    'stale_count': len(activity.get('stale_repos', []))
                }
                
        # Calculate overall health score
        if insights['repository_stats'].get('total', 0) > 0:
            active_ratio = insights['repository_stats'].get('active', 0) / insights['repository_stats']['total']
            insights['health_score'] = round(active_ratio * 100, 1)
            
        return insights
    
    def _generate_updated_profile(self, current_profile: str, insights: Dict[str, Any]) -> str:
        """Generate updated profile content using OpenCog reasoning."""
        
        # If no meaningful insights, return current profile
        if not insights.get('repository_stats') or insights['repository_stats'].get('total', 0) == 0:
            return current_profile
        
        updated_profile = current_profile
        
        # Update repository statistics if found in the profile
        stats_section = self._find_stats_section(current_profile)
        if stats_section:
            updated_stats = self._generate_stats_section(insights)
            updated_profile = updated_profile.replace(stats_section, updated_stats)
        else:
            # Add stats section if not present
            stats_section = self._generate_stats_section(insights)
            # Insert after the main description
            lines = updated_profile.split('\n')
            insert_pos = self._find_insertion_point(lines)
            lines.insert(insert_pos, '')
            lines.insert(insert_pos + 1, '## 📊 Organization Metrics')
            lines.insert(insert_pos + 2, stats_section)
            updated_profile = '\n'.join(lines)
        
        # Update language information if present
        if insights.get('language_distribution'):
            updated_profile = self._update_language_info(updated_profile, insights['language_distribution'])
        
        # Add timestamp comment for tracking
        timestamp_comment = f'<!-- Last updated by OpenCog orchestrator: {insights["last_analysis"]} -->'
        if timestamp_comment not in updated_profile:
            updated_profile = updated_profile + '\n\n' + timestamp_comment
        else:
            # Update existing timestamp
            pattern = r'<!-- Last updated by OpenCog orchestrator: .* -->'
            updated_profile = re.sub(pattern, timestamp_comment, updated_profile)
        
        return updated_profile
    
    def _find_stats_section(self, content: str) -> Optional[str]:
        """Find existing statistics section in the profile."""
        # Look for patterns that might indicate a stats section
        patterns = [
            r'## 📊 Organization Metrics.*?(?=\n##|\n$)',
            r'## Statistics.*?(?=\n##|\n$)',
            r'## Metrics.*?(?=\n##|\n$)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
            if match:
                return match.group(0)
        
        return None
    
    def _generate_stats_section(self, insights: Dict[str, Any]) -> str:
        """Generate a statistics section based on insights."""
        stats = insights.get('repository_stats', {})
        languages = insights.get('language_distribution', {})
        health_score = insights.get('health_score', 0)
        
        section = []
        
        if stats.get('total', 0) > 0:
            section.append(f"- **Total Repositories**: {stats['total']}")
            section.append(f"- **Active Repositories**: {stats.get('active', 0)}")
            section.append(f"- **Health Score**: {health_score}%")
        
        if languages:
            top_languages = sorted(languages.items(), key=lambda x: x[1], reverse=True)[:5]
            lang_list = ', '.join([f"{lang} ({count})" for lang, count in top_languages])
            section.append(f"- **Primary Languages**: {lang_list}")
        
        section.append(f"- **Last Updated**: {datetime.utcnow().strftime('%B %Y')}")
        
        return '\n'.join(section)
    
    def _find_insertion_point(self, lines: List[str]) -> int:
        """Find the best place to insert new content."""
        # Look for the end of the main description
        for i, line in enumerate(lines):
            if line.startswith('## ') and i > 5:  # First section header after intro
                return i
        
        # If no section headers found, insert near the end
        return max(0, len(lines) - 3)
    
    def _update_language_info(self, content: str, languages: Dict[str, int]) -> str:
        """Update language information in the content."""
        top_languages = sorted(languages.items(), key=lambda x: x[1], reverse=True)[:3]
        
        # If there's already language info, try to update it
        lang_pattern = r'(Primary Languages?[:\s]+)([^\n]+)'
        match = re.search(lang_pattern, content, re.IGNORECASE)
        
        if match and top_languages:
            lang_list = ', '.join([lang for lang, _ in top_languages])
            new_lang_text = f"{match.group(1)}{lang_list}"
            content = content.replace(match.group(0), new_lang_text)
        
        return content


def main():
    parser = argparse.ArgumentParser(description='Update PaystackOSS profile with OpenCog insights')
    parser.add_argument('--results-file', required=True, help='Orchestration results file')
    parser.add_argument('--profile-path', required=True, help='Path to profile README file')
    
    args = parser.parse_args()
    
    # Initialize updater
    updater = ProfileUpdater()
    
    # Update profile
    result = updater.update_profile(args.results_file, args.profile_path)
    
    # Save update result
    with open('profile_update_result.json', 'w') as f:
        json.dump(result, f, indent=2)
    
    if result.get('success'):
        if result.get('changes_made'):
            print(f"✅ Profile updated with {result.get('insights_applied', 0)} insights")
        else:
            print("ℹ️ Profile is up to date")
    else:
        print(f"❌ Profile update failed: {result.get('error', 'Unknown error')}")
        sys.exit(1)


if __name__ == '__main__':
    main()
import os
import sys
import pytz
import argparse
from utils.apiHandler import api_call
from datetime import datetime, timedelta

# example
# python timezone_targeting.py --feature-flag-key='wealthManagement' --release-date='2025-07-01'

'''
Set your LaunchDarkly instance information here
'''
PROJECT_KEY = "nteixeira-ld-demo" # can be moved to call vs static
SOURCE_ENVIRONMENT = "test" # can be moved to call vs static

def create_timezone_targeting_rules(feature_flag_key, release_date):
    # Get API key from environment variable
    api_key = os.getenv('LD_API_KEY')
    if not api_key:
        print("Error: LD_API_KEY environment variable is not set")
        sys.exit(1)

    # First, get the existing flag to preserve other settings
    url = f"https://app.launchdarkly.com/api/v2/flags/{PROJECT_KEY}/{feature_flag_key}"
    headers = {
        'Authorization': api_key,
        'Content-Type': 'application/json'
    }
    
    try:
        # Get current flag configuration
        response = api_call('GET', url, headers=headers)
        if response.status_code == 404:
            print(f"Error: Feature flag '{feature_flag_key}' not found")
            sys.exit(1)
        elif response.status_code != 200:
            print(f"Error getting feature flag: {response.status_code}")
            print(response.text)
            sys.exit(1)
            
        # Create rules for UTC-12 to UTC+12
        rules = []
        for offset in range(-12, 13):
            # Skip UTC+0 to avoid duplicate rules since we'll match on both +0000 and -0000
            if offset == 0:
                continue
                
            # Format offset string like "+0100" or "-0500"
            offset_str = f"{'+' if offset >= 0 else '-'}{abs(offset):02d}00"
            
            # Set target time to 4 AM on the release date
            target_time = release_date.replace(hour=4, minute=0, second=0, microsecond=0)
            
            # Adjust target time for the timezone offset
            target_time_utc = target_time.astimezone(pytz.UTC) + timedelta(hours=-offset)
            
            rule = {
                "description": f"Schedule for GMT{'+' if offset >= 0 else ''}{offset} at 4 AM local on {release_date.strftime('%Y-%m-%d')}",
                "clauses": [
                    {
                        "attribute": "timezone",
                        "op": "matches",
                        "values": [offset_str],
                        "negate": False
                    }
                ],
                "variation": 0,  # Assuming 0 is the "true" variation
                "scheduleKind": "custom",
                "schedule": {
                    "startDate": target_time_utc.isoformat(),
                    "endDate": None,
                    "startTime": "04:00",
                    "endTime": None,
                    "timezone": f"Etc/GMT{'-' if offset >= 0 else '+'}{abs(offset)}"  # Note: Etc/GMT uses opposite signs
                }
            }
            rules.append(rule)

        # Create patch document to update just the rules
        patch = [
            {
                "op": "replace",
                "path": f"/environments/{SOURCE_ENVIRONMENT}/rules",
                "value": rules
            }
        ]
        
        # Make PATCH request to update the flag
        patch_url = f"https://app.launchdarkly.com/api/v2/flags/{PROJECT_KEY}/{feature_flag_key}"
        headers['Content-Type'] = 'application/json-patch+json'  # Change content type for PATCH
        response = api_call('PATCH', patch_url, headers=headers, json=patch)
        
        if response.status_code == 200:
            print(f"Successfully updated feature flag {feature_flag_key} with {len(rules)} timezone rules")
        else:
            print(f"Error updating feature flag: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create timezone-based targeting rules for a LaunchDarkly feature flag')
    parser.add_argument('--feature-flag-key', required=True, help='Feature flag key to update')
    parser.add_argument('--release-date', required=True, help='Release date in YYYY-MM-DD format')
    
    args = parser.parse_args()
    
    try:
        # Parse the release date string into a datetime object
        release_date = datetime.strptime(args.release_date, '%Y-%m-%d')
        # Make it timezone-aware using the local timezone
        release_date = release_date.replace(tzinfo=datetime.now().astimezone().tzinfo)
    except ValueError:
        print("Error: Release date must be in YYYY-MM-DD format")
        sys.exit(1)
        
    create_timezone_targeting_rules(args.feature_flag_key, release_date) 
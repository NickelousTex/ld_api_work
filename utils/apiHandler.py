import time
import requests
from requests.exceptions import HTTPError
import json
# pip install requests


BASE_URL = "https://app.launchdarkly.com/api/v2"
CALL_THRESHOLD = 1 # If the API call limit falls below this number, the calls will pause and retry once the limit is reset.


class RateLimitError(Exception):
    '''Exception used by the main function when the rate limit is too low'''
    pass

def api_call(method, url, headers=None, json=None, params=None):
    """
    A generic API call function with rate limit handling for LaunchDarkly's API.
    
    Args:
        method (str): HTTP method ("GET", "POST", "PATCH", "DELETE")
        url (str): Full URL for the API endpoint
        headers (dict): Request headers
        json (dict): JSON body for the request
        params (dict): URL parameters
    
    Returns:
        requests.Response: The response from the API
    """
    MAX_RETRIES = 3
    RETRY_DELAY = 3  # seconds
    RATE_LIMIT_THRESHOLD = 1

    for attempt in range(MAX_RETRIES):
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                json=json,
                params=params
            )
            
            # Check rate limits if the headers are present
            remaining = response.headers.get('X-Ratelimit-Auth-Token-Remaining')
            if remaining and int(remaining) <= RATE_LIMIT_THRESHOLD:
                reset_time = int(response.headers.get('X-Ratelimit-Reset', 0))
                current_time = round(time.time() * 1000)
                wait_time = max((reset_time - current_time) // 1000, 1)
                
                print(f'Rate limit low ({remaining} remaining). Waiting {wait_time} seconds...')
                time.sleep(wait_time)
                continue
                
            # Raise an error for bad responses
            print(response.text)
            response.raise_for_status()
            return response

        except HTTPError as e:
            if attempt == MAX_RETRIES - 1:  # Last attempt
                print(f"HTTP Error after {MAX_RETRIES} attempts: {str(e)}")
                raise
            print(f"HTTP Error (attempt {attempt + 1}/{MAX_RETRIES}): {str(e)}")
            time.sleep(RETRY_DELAY)
            
        except Exception as e:
            if attempt == MAX_RETRIES - 1:  # Last attempt
                print(f"Error after {MAX_RETRIES} attempts: {str(e)}")
                raise
            print(f"Error (attempt {attempt + 1}/{MAX_RETRIES}): {str(e)}")
            time.sleep(RETRY_DELAY)

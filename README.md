# LaunchDarkly Timezone Targeting Script

This script creates targeting rules for a LaunchDarkly feature flag based on different timezones. It will create rules that activate the feature flag at 4 AM local time for each timezone.

## Prerequisites

- Python 3.6 or higher
- LaunchDarkly API Key (set as environment variable)
- Feature Flag Key from your LaunchDarkly project

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Set your LaunchDarkly API key as an environment variable:
```bash
export LD_API_KEY="your-api-key-here"
```

## Usage

Run the script with your feature flag key:

```bash
python timezone_targeting.py --feature-flag-key="your-feature-flag-key" --release_date="YYYY-MM-DD"
```

## What it does

1. Creates targeting rules for each unique timezone offset
2. Sets up rules to activate the feature flag at 4 AM local time for each timezone
3. Updates the specified feature flag with the new targeting rules

## Notes

- The script assumes that variation 0 is the "true" variation in your feature flag
- Make sure your feature flag is already created in LaunchDarkly before running this script
- The script requires the "timezone" user attribute to be available in your LaunchDarkly configuration
- The LaunchDarkly API key must be set in the LD_API_KEY environment variable

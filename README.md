## Text to SQL Tool

An A.I time series analyst to provide insights into price data based off user request.

## Setup
1. The project uses UV as dependency manager. 
2. To activate env: source .venv/bin/activate
3. To add all necessary packages: uv sync

## Running the API:
1. Run the API file: uv run python src/api.py 
2. This creates a local API endpoint.
3. src/test_api.py provides a simple script to try different results: uv run python src/test_api.py

## Git flow

All MRs generally should go to the `development` branch. The strategy is:
- We only have short-lived, small branches ideally.
- Deploy very frequently (all merged MRs are automatically deployed).
- Always keep the special branches in a fully functional state.
- Any critical bugs should be solved or defused, before other things.

## UI:

1. To test the UI, you need 
   - LangGraph studio - this will be setup as a part of env
   - OpenAI API Key
   - LangSmith API key

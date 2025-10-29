"""
Test queries for the time series analyst chatbot
Based on case_data.csv which contains price data for:
- Butter from ZuivelNL (2001-2025)
- Milk from Belgium (1977-2025) 
- Butter from EEX EU (2010-2025)
- SMP from EEX EU (2010-2025)
"""

test_queries = [
    # Basic statistics queries
    "What is the highest price ever recorded for butter from ZuivelNL?",
    
    "What was the lowest milk price from Belgium in the last 5 years?",
    
    "Can you show me the average price of SMP from EEX EU in 2023?",
    
    # Trend and comparison queries
    "How has the price of butter from EEX EU changed over the past 2 years?",
    
    "Which product had the highest price volatility in 2022 - butter from ZuivelNL or SMP from EEX EU?",
    
    # Specific time period queries
    "What was the price range for milk from Belgium during the 2008 financial crisis period?",
    
    "Show me the monthly average prices for butter from ZuivelNL in 2024",
    
    # Market event queries
    "When did butter from EEX EU reach its peak price and what was the value?",
    
    "How did SMP prices from EEX EU perform during the COVID-19 pandemic (2020-2021)?",
    
    # Comparative analysis
    "Compare the price trends of butter from ZuivelNL versus butter from EEX EU since 2010"
]

# Expected data ranges for validation:
expected_ranges = {
    "butter_zuivelnl": {
        "date_range": ("2001-04-23", "2025-10-22"),
        "price_range": (2100, 8100),  # approximate
        "peak_period": "2024-09-18"  # around 8100
    },
    "milk_belgium": {
        "date_range": ("1977-01-01", "2025-09-01"),
        "price_range": (167, 590),  # approximate
        "covid_impact": "2020-04-01"  # significant drop
    },
    "butter_eex_eu": {
        "date_range": ("2010-05-31", "2025-10-22"),
        "price_range": (1600, 8100),  # approximate
        "peak_period": "2024-09-25"  # around 8100
    },
    "smp_eex_eu": {
        "date_range": ("2010-05-31", "2018-11-07"),
        "price_range": (1250, 3300),  # approximate
        "peak_period": "2013-08-31"  # around 3300
    }
}

def run_chatbot_tests(chat_function):
    """
    Run all test queries against the chatbot
    
    Args:
        chat_function: Function that takes a query string and returns a response
    """
    for i, query in enumerate(test_queries, 1):
        print(f"\n🤖 TEST QUERY {i}:")
        print(f"Q: {query}")
        print("-" * 40)
        
        try:
            response = chat_function(query)
            print(f"A: {response}")
        except Exception as e:
            print(f"❌ ERROR: {e}")
        
        print("-" * 40)

# Example usage with your API
def test_with_api():
    """Test using the FastAPI endpoint"""
    import requests
    
    def api_chat(query):
        response = requests.post(
            "http://localhost:8000/chat", 
            json={"message": query}
        )
        if response.status_code == 200:
            return response.json()['response']
        else:
            return f"API Error: {response.status_code}"
    
    run_chatbot_tests(api_chat)

if __name__ == "__main__":
    print("Test queries for time series analyst chatbot:")
    print("\n".join(f"{i}. {q}" for i, q in enumerate(test_queries, 1)))
    
    # Uncomment to run tests
    test_with_api()
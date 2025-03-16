"""
Test file for the Ethical Investment Query System
This script runs example queries against the S&P 500 data file
and returns the top matches for each query, including details
about the query vector and scoring calculation.
"""

from query_system import EthicalInvestmentQuerySystem, load_stock_data
import os
import glob


def print_developer_guide():
    """Print a one-time guide explaining how the query system works"""
    print("\n" + "=" * 80)
    print("DEVELOPER GUIDE: UNDERSTANDING QUERY VECTORS AND SCORING")
    print("=" * 80)
    print(
        """
QUERY VECTOR EXPLANATION:
-------------------------
The query vector represents the user's preferences extracted from natural language:

- Fields like "environmentScore", "socialScore", etc. correspond to stock metrics
- The weight values indicate:
  * Direction: Positive = higher values preferred, Negative = lower values preferred
  * Magnitude: Larger absolute values = more important in the calculation
  * Intensifiers: Words like "very" (1.5x), "extremely" (2.0x) multiply the weights

SCORING ALGORITHM:
-----------------
1. All stock metrics are normalized to 0-1 scale
2. For each stock, the score is calculated as:
   score = sum(weight * normalized_value) / sum(|weight|)

3. Weights work as follows:
   * environmentScore: 1.0 = prefer high environmental scores
   * overallRisk: -1.0 = prefer low risk (negative weight inverts preference)
   * If intensified: "very low risk" = -1.5 (1.5x stronger preference for low risk)

4. Special cases:
   * "specified_sectors": This is a filter, not a weight. Only stocks in these sectors are considered.
   * Missing values default to 0, which may significantly lower scores
   
EXAMPLE INTERPRETATION:
----------------------
Query: "Find stocks with low risk and high environmental scores"
Vector: {"environmentScore": 1.0, "overallRisk": -1.0}

This means:
- Companies with higher environmental scores get boosted
- Companies with higher risk get penalized
- Both factors have equal importance (same absolute weight)

For a stock with normalized environmentScore=0.8 and overallRisk=0.3:
Score = ((1.0 * 0.8) + (-1.0 * 0.3)) / (|1.0| + |-1.0|)
      = (0.8 - 0.3) / 2
      = 0.25

Higher scores indicate better matches to the query criteria.
"""
    )


def format_result(result, index, query_vector):
    """Format a single result with score calculation details"""

    output = [
        f"{index}. {result['symbol']} - {result['name']} (Score: {result['score']:.3f})",
        f"   Sector: {result['sector']}",
        f"   ESG Scores: Environmental={result['environmentScore']:.2f}, "
        f"Social={result['socialScore']:.2f}, Governance={result['governanceScore']:.2f}",
        f"   Total ESG: {result['totalEsg']:.2f}, Risk Level: {result['overallRisk']}",
    ]

    output.append("\n   SCORE CALCULATION:")

    total_weight = sum(
        abs(w) for w, v in query_vector.items() if isinstance(w, (int, float))
    )

    for field, weight in query_vector.items():
        if field == "specified_sectors" or not isinstance(weight, (int, float)):
            continue

        field_value = getattr(result, field, 0)
        if field in result:
            field_value = result[field]
        else:
            field_value = 0

        contribution = (weight * field_value) / total_weight if total_weight > 0 else 0

        direction = "Higher is better" if weight > 0 else "Lower is better"
        output.append(
            f"   - {field}: {field_value:.2f} × weight {weight:.2f} → contribution: {contribution:.3f} ({direction})"
        )

    return "\n".join(output)


def run_query(query_system, stocks_data, query, top_n=10):
    """Run a query and display the top N results with scoring details"""
    print(f"\n{'='*80}")
    print(f'QUERY: "{query}"')
    print(f"{'='*80}")

    query_vector = query_system.parse_query(query)

    print("\nQUERY VECTOR:")
    if not query_vector:
        print("  No specific criteria identified in query")
    else:
        for field, weight in query_vector.items():
            if isinstance(weight, (int, float)):
                print(f"  {field}: {weight:.2f}")
            else:
                print(f"  {field}: {weight}")

    results = query_system.rank_stocks(stocks_data, query)

    if not results:
        print("\nNo matching stocks found for this query.")
        return

    print(f"\nTop {min(top_n, len(results))} matches:")
    for i, result in enumerate(results[:top_n]):
        print(format_result(result, i + 1, query_vector))
        print("-" * 40)


def main():

    print_developer_guide()

    print("\nLoading S&P 500 data...")
    try:

        directory_path = "/Users/wilson/Desktop/CS-4300-Robingood/backend"

        print(f"Looking for data files in: {directory_path}")
        json_files = glob.glob(os.path.join(directory_path, "*.json"))
        txt_files = glob.glob(os.path.join(directory_path, "*.txt"))

        print("Available JSON files:")
        for file in json_files:
            print(f"  - {os.path.basename(file)}")

        print("Available text files:")
        for file in txt_files:
            print(f"  - {os.path.basename(file)}")

        possible_files = json_files + txt_files
        if not possible_files:
            possible_files = [
                os.path.join(directory_path, "sp500.json"),
                os.path.join(directory_path, "paste.txt"),
                os.path.join(directory_path, "S&P500.json"),
                os.path.join(directory_path, "SP500.json"),
            ]

        found_file = False
        for file_path in possible_files:
            if os.path.exists(file_path):
                print(f"Found file at: {file_path}")
                with open(file_path, "r") as file:
                    json_text = file.read()
                stocks_data = load_stock_data(json_text)
                print(f"Successfully loaded data for {len(stocks_data)} stocks.")
                found_file = True
                break

        if not found_file:
            print("Could not find the data file. Please specify the exact path:")
            print("Looked in these locations:")
            for path in possible_files:
                print(f"  - {path}")
            return

    except Exception as e:
        print(f"Error loading stock data: {e}")
        return

    query_system = EthicalInvestmentQuerySystem()

    example_queries = [
        "Find stocks with low risk and high environmental scores",
        "Show me companies with excellent governance and social responsibility",
        "I want to invest in companies that are environmentally friendly with minimal controversy",
        "Which companies have the best overall ESG ratings?",
        "Find technology companies with strong social scores",
        "I need stocks with very low risk that are still good for the environment",
        "Show me health care companies with strong governance",
        "Which companies have the highest environmental scores but also low risk?",
        "Find companies with extremely good social responsibility",
        "I want to invest in utilities with strong environmental practices",
    ]

    for query in example_queries:
        run_query(query_system, stocks_data, query)


if __name__ == "__main__":
    main()

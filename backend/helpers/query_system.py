import json
import re
from collections import defaultdict
import math
import nltk
from nltk.corpus import stopwords
# from nltk.tokenize import word_tokenize
# from nltk.stem import PorterStemmer

class EthicalInvestmentQuerySystem:
    def __init__(self, stocks_data):
        
        # Map possible terms in queries to the corresponding ESG factors
        self.field_mappings = {
            "environmental": ["environmentScore", "environment", "eco", "green", "sustainable", "carbon", "climate"],
            "social": ["socialScore", "society", "community", "people", "ethical", "human rights", "social responsibility"],
            "governance": ["governanceScore", "management", "leadership", "board", "transparency", "corporate governance"],
            "esg": ["totalEsg", "sustainability", "responsible", "ethical investing", "sustainable investing"],
            "risk": ["overallRisk", "risky", "danger", "safe", "safety", "volatility", "stability"],
            "controversy": ["highestControversy", "controversial", "scandal", "dispute", "issue", "problems"],
            "market cap": ["marketCap", "size", "capitalization", "market value", "company size", "large cap", "small cap"],
            "beta": ["beta", "volatility", "stable", "stability", "market risk", "market sensitivity"],
            "percentile": ["percentile", "rank", "standing", "position", "rating", "relative performance"],
            "sector": ["GICS Sector", "industry", "field", "domain", "market segment"],
        }
        self.reverse_mappings = {}
        for key, values in self.field_mappings.items():
            for value in values:
                self.reverse_mappings[value] = key

        # Define modifiers for positive and negative terms
        self.modifiers = {"high": ["high", "good", "strong", "great", "impressive", "positive", "large", "big", "higher", "better"], 
                          "low": ["low", "bad", "weak", "poor", "negative", "minimal", "small", "lower", "worse"]}
        self.reverse_modifiers = {}
        for key, values in self.modifiers.items():
            for value in values:
                self.reverse_modifiers[value] = 1.0 if key == "high" else -1.0

        # Define intensifiers for increasing or decreasing importance
        self.intensifiers = {"very": 1.5, "extremely": 2.0, "highly": 1.7, "incredibly": 1.8, "somewhat": 0.7, "slightly": 0.5, "a bit": 0.6, "a lot": 1.6, "tremendously": 1.9, "exceptionally": 1.8, "moderately": 0.8}

        # Define negations to invert the meaning of terms
        self.negations = ["not", "no", "never", "neither", "nor", "barely", "hardly"]

        self.sectors = [
            "information technology",
            "health care",
            "financials",
            "consumer discretionary",
            "communication services",
            "industrials",
            "consumer staples",
            "energy",
            "utilities",
            "real estate",
            "materials",
        ]

        self.normalized_data = self.normalize_stock_data(stocks_data)

        # Load stopwords for filtering out common words
        try:
            self.stopwords = set(stopwords.words('english'))
        except LookupError:
            nltk.download('stopwords')
            self.stopwords = set(stopwords.words('english'))

        # # Load tokenizer
        # try:
        #     self.tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
        # except LookupError:
        #     nltk.download('punkt_tab')
        #     self.tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')

        # # Load stemmer
        # try:
        #     self.stemmer = PorterStemmer()
        # except LookupError:
        #     nltk.download('punkt_tab')
        #     self.stemmer = PorterStemmer()

    def tokenize(self, text):
        """Simple tokenization by splitting on spaces and removing punctuation"""
        # TODO 1: destroys phrases like carbon-neutral
        # return nltk.word_tokenize(text)
        text = text.lower()
        text = re.sub(r"\s+", " ", text)

        for multi_word in ["a bit", "a lot"]:
            if multi_word in text:
                text = text.replace(multi_word, multi_word.replace(" ", "_"))

        text = re.sub(r"[^\w\s]", "", text)
        tokens = text.split()

        tokens = [t.replace("_", " ") for t in tokens]

        return tokens

    def parse_query(self, query_text):
        """
        Parse a natural language query and convert it to a weighted vector
        representing the importance of different factors
        """
        tokens = self.tokenize(query_text)
        query_vector = defaultdict(float)
        negation_active = False
        window_size = 4
        specified_sectors = []

        # Should do a hard filter
        for token in tokens:
            # TODO 2: Improve synonym mapping + fuzzy matching, misses variants (tech =/= info tech)
            if token in self.sectors:
                specified_sectors.append(token)

        for i in range(len(tokens)):
            if tokens[i] in self.negations:
                negation_active = True
                continue

            if (
                tokens[i] in self.stopwords
                and tokens[i] not in self.intensifiers
                and tokens[i] not in self.negations
            ):
                continue

            # Get the field match in field_mappings
            field_match = None
            for field_key, synonyms in self.field_mappings.items():
                if tokens[i] in synonyms or tokens[i] == field_key:
                    field_match = field_key
                    break

            if field_match:
                # Get the dimension of vector 
                field_value = self.field_mappings[field_match][0]

                modifier_value = 0.0
                intensifier_value = 1.0

                for j in range(max(0, i - window_size), i):
                    # Update intensifier and modifiers values 
                    if tokens[j] in self.intensifiers:
                        intensifier_value *= self.intensifiers[tokens[j]]
                    if tokens[j] in self.reverse_modifiers:
                        modifier_value = self.reverse_modifiers[tokens[j]]

                if modifier_value == 0.0:
                    if field_match in ["environmental", "social", "governance", "esg"]:
                        modifier_value = 1.0
                    elif field_match in ["risk", "controversy", "beta"]:
                        modifier_value = -1.0
                    else:
                        modifier_value = 1.0

                if negation_active:
                    modifier_value *= -1
                    negation_active = False

                query_vector[field_value] = modifier_value * intensifier_value

        if specified_sectors:
            query_vector["specified_sectors"] = specified_sectors

        return dict(query_vector)

    def normalize_stock_data(self, stocks_data):
        """
        Normalize stock data to make features comparable
        """

        features = ["environmentScore", "socialScore", "governanceScore", "totalEsg", 
                    "overallRisk", "highestControversy", "marketCap", "beta", "percentile"]

        feature_arrays = {}
        for feature in features:
            feature_arrays[feature] = [
                float(stock.get(feature, 0)) for stock in stocks_data
            ]

        feature_min_max = {}
        for feature in features:
            values = feature_arrays[feature]
            if values:
                feature_min_max[feature] = (min(values), max(values))
            else:
                feature_min_max[feature] = (0, 1)

        normalized_data = []
        for stock in stocks_data:
            normalized_stock = stock.copy()
            for feature in features:
                if feature in stock:

                    value = float(stock[feature])
                    min_val, max_val = feature_min_max[feature]

                    if max_val > min_val:
                        if feature in ["highestControversy", "overallRisk", "beta"]:

                            normalized_stock[feature] = (max_val - value) / (
                                max_val - min_val
                            )
                        else:
                            normalized_stock[feature] = (value - min_val) / (
                                max_val - min_val
                            )
                    else:
                        normalized_stock[feature] = 0.5

            normalized_data.append(normalized_stock)

        return normalized_data

    def cosine_similarity(self, stock, query_vector):
        query_magnitude = math.sqrt(sum(w**2 for w in query_vector.values()))
        stock_vector = [stock[field] for field in query_vector]
        stock_magnitude = math.sqrt(sum(v**2 for v in stock_vector))
        
        if query_magnitude == 0 or stock_magnitude == 0:
            return 0
            
        dot_product = sum(w * stock[field] for field, w in query_vector.items())
        return dot_product / (query_magnitude * stock_magnitude)

    def calculate_similarity(self, stock, query_vector):
        """
        Calculate the similarity score between a stock and the query vector
        """
        score = 0.0
        total_weight = 0.0

        if "specified_sectors" in query_vector:
            if (
                stock.get("GICS Sector", "").lower()
                not in query_vector["specified_sectors"]
            ):
                return 0.0

        for field, weight in query_vector.items():
            if field != "specified_sectors" and field in stock and weight != 0.0:
                score += weight * float(stock[field])
                total_weight += abs(weight)

        if total_weight > 0:
            score = score / total_weight

        return score

    def rank_stocks(self, stocks_data, query_text):
        """
        Rank stocks based on how well they match the query
        """

        query_vector = self.parse_query(query_text)

        scores = []
        for stock in self.normalized_data:
            score = self.calculate_similarity(stock, query_vector)
            # score = self.cosine_similarity(stock, query_vector)
            if score > 0:
                scores.append(
                    {
                        "symbol": stock["Symbol"],
                        "name": stock["Full Name"],
                        "score": score,
                        "sector": stock.get("GICS Sector", "Unknown"),
                        "environmentScore": float(stock.get("environmentScore", 0)),
                        "socialScore": float(stock.get("socialScore", 0)),
                        "governanceScore": float(stock.get("governanceScore", 0)),
                        "totalEsg": float(stock.get("totalEsg", 0)),
                        "overallRisk": int(float(stock.get("overallRisk", 0))),
                    }
                )

        scores.sort(key=lambda x: x["score"], reverse=True)
        return scores


def parse_json_file(file_path):
    """Parse a JSON file into a list of stock objects"""
    with open(file_path, "r") as file:
        content = file.read()
    return load_stock_data(content)


def load_stock_data(json_text):
    """Parse JSON text into a list of stock objects"""
    cleaned_json = json_text.strip()
    if cleaned_json.startswith("{"):
        cleaned_json = "[" + cleaned_json
    elif not cleaned_json.startswith("["):
        cleaned_json = "[" + cleaned_json
    if not cleaned_json.endswith("]"):
        cleaned_json = cleaned_json + "]"
    cleaned_json = re.sub(r",\s*}", "}", cleaned_json)
    cleaned_json = re.sub(r",\s*]", "]", cleaned_json)
    try:
        return json.loads(cleaned_json)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")

        if "," in cleaned_json:

            last_comma_index = cleaned_json.rindex(",")
            last_bracket_index = cleaned_json.rindex("]")
            if last_comma_index > last_bracket_index:
                cleaned_json = (
                    cleaned_json[:last_comma_index]
                    + cleaned_json[last_comma_index + 1 :]
                )

        try:
            return json.loads(cleaned_json)
        except json.JSONDecodeError as e:
            print(f"Still cannot parse JSON after cleanup: {e}")

            print("Attempting to parse individual objects...")
            try:
                parts = re.split(r"},\s*{", cleaned_json.strip("[]"))
                result = []
                for i, part in enumerate(parts):

                    if not part.startswith("{"):
                        part = "{" + part
                    if not part.endswith("}"):
                        part = part + "}"

                    try:
                        obj = json.loads(part)
                        result.append(obj)
                    except json.JSONDecodeError:
                        print(f"Could not parse object {i+1}")

                if result:
                    print(
                        f"Successfully parsed {len(result)} out of {len(parts)} objects"
                    )
                    return result
                else:
                    print("Could not parse any objects, returning empty list")
                    return []
            except Exception as e:
                print(f"Error during manual parsing: {e}")
                return []

import requests
import json
from .models import CarDealer, DealerReview
from requests.auth import HTTPBasicAuth


# Create a `get_request` to make HTTP GET requests
# e.g., response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
#                                     auth=HTTPBasicAuth('apikey', api_key))
def get_request(url, **kwargs):
    print("GET from {} ".format(url))
    if "api_key" in kwargs:
        api_key = kwargs['api_key']
    else:
        api_key = ''

    try:
        # Call get method of requests library with URL and parameters
        if api_key:
            response = requests.get(url, headers={'Content-Type': 'application/json'},
                                        params=kwargs['params'], auth=HTTPBasicAuth('apikey', api_key))
        else:
            response = requests.get(url, headers={'Content-Type': 'application/json'},
                            params=kwargs)
    except:
        # If any error occurs
        print("Network exception occurred")
    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    return json_data

# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)
def post_request(url, **kwargs):
    print("POST to {} ".format(url))

    try:
        response = requests.post(url, headers={'Content-Type': 'application/json'}, data=kwargs['data'])
    except:
        # If any error occurs
        print("Network exception occurred")

    status_code = response.status_code
    json_data = json.loads(response.text)
    print("With status {} ".format(status_code))
    print(json_data)
    return json_data

# Create a get_dealers_from_cf method to get dealers from a cloud function
# def get_dealers_from_cf(url, **kwargs):
# - Call get_request() with specified arguments
# - Parse JSON results into a CarDealer object list
def get_dealers_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url)
    if json_result:
        # Get the row list in JSON as dealers
        dealers = json_result["dealerships"]
        # For each dealer object
        for dealer in dealers:
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer["address"], city=dealer["city"], full_name=dealer["full_name"],
                                   id=dealer["id"], lat=dealer["lat"], long=dealer["long"],
                                   short_name=dealer["short_name"],
                                   st=dealer["st"], zip=dealer["zip"])
            results.append(dealer_obj)
    return results

# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
# def get_dealer_by_id_from_cf(url, dealerId):
# - Call get_request() with specified arguments
# - Parse JSON results into a DealerView object list
def get_dealer_reviews_from_cf(url, dealership):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url, dealership=dealership)
    print(json_result)
    if json_result:
        # Get the row list in JSON as dealers
        try:
            reviews = json_result["reviews"]
        except:
            return results
        # For each dealer object
        for review in reviews:
            # Get its content in `doc` object
            # Create a CarDealer object with values in `doc` object
            if review['purchase']:
                review_obj = DealerReview(
                    dealership=review['dealership'],
                    name=review['name'],
                    purchase=review['purchase'],
                    purchase_date=review['purchase_date'],
                    review=review['review'],
                    car_make=review['car_make'],
                    car_model=review['car_model'],
                    car_year=review['car_year'],
                    id=["id"])

            else:
                review_obj = DealerReview(
                    dealership=review['dealership'],
                    name=review['name'],
                    purchase=review['purchase'],
                    purchase_date="",
                    review=review['review'],
                    car_make="",
                    car_model="",
                    car_year="",
                    id=["id"])
            
            results.append(review_obj)
    return results

# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
# def analyze_review_sentiments(text):
# - Call get_request() with specified arguments
# - Get the returned sentiment label such as Positive or Negative

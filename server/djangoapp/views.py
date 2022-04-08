from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from .models import CarModel, CarMake, CarDealer
from .restapis import get_dealers_from_cf, get_dealer_reviews_from_cf, post_request
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.


# Create an `about` view to render a static about page
def about(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/about.html', context)

# Create a `contact` view to return a static contact page
def contact(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/contact.html', context)

# Create a `login_request` view to handle sign in request
def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('djangoapp:index')
        else:
            context['message'] = "Invalid username or password."
            return render(request, 'djangoapp/login.html', context)
    else:
        return render(request, 'djangoapp/login.html', context)

# Create a `logout_request` view to handle sign out request
def logout_request(request):
    logout(request)
    return render(request, 'djangoapp/logout.html')

# Create a `registration_request` view to handle sign up request
def registration(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    elif request.method == 'POST':
        # Check if user exists
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.error("New user")
        if not user_exist:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name, password=password)
            login(request, user)
            return redirect("djangoapp:index")
        else:
            context['message'] = "User already exists."
            return render(request, 'djangoapp/registration.html', context)

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    if request.method == "GET":
        context = {}
        url = "https://7d6362dc.us-south.apigw.appdomain.cloud/get-dealership-info/get-dealerships"
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        # Concat all dealer's short name
        context = {
            "dealerships": dealerships
        }
        # Return a list of dealer short name
        return render(request, 'djangoapp/index.html', context)


# Create a `get_dealer_details` view to render the reviews of a dealer
def get_dealer_details(request, **kwargs):
    if request.method == "GET":
        context = {}
        url = url = "https://7d6362dc.us-south.apigw.appdomain.cloud/api/dealership/api/review"
        # Get dealers from the URL
        reviews = get_dealer_reviews_from_cf(url, dealership=kwargs["dealership_id"])
        # Concat all dealer's short name
        context['reviews'] = reviews
        context['dealer'] = kwargs["dealership_id"]
        # Return a list of dealer short name
        return render(request, 'djangoapp/dealer_details.html', context)

# Create a `add_review` view to submit a review
def add_review(request, **kwargs):
    if request.method == "GET":
        context = {}
        cars_at_dealership = CarModel.objects.filter(dealer_id=kwargs['dealership_id'])
        context['cars'] = cars_at_dealership
        context['dealer'] = kwargs['dealership_id']
        return render(request, 'djangoapp/add_review.html', context)
    if request.method == "POST":
        doc = {}
        if request.POST['purchasecheck'] == 'true':
            doc['name'] = request.POST['first_name'] + " " + request.POST['last_name']
            doc['review'] = request.POST['content']
            doc['purchase'] = True
            doc['purchase_date'] = request.POST['purchasedate']
            doc['dealership'] = kwargs['dealership_id']
            car_breakdown = request.POST['car'].split("-")
            doc['car_year'] = car_breakdown[2]
            doc['car_make'] = car_breakdown[1]
            doc['car_model'] = car_breakdown[0]
        else:
            doc['name'] = request.POST['first_name'] + " " + request.POST['last_name']
            doc['review'] = request.POST['content']
            doc['purchase'] = False
            doc['dealership'] = kwargs['dealership_id']

        data = {
            "doc": doc
        }
        url = "https://7d6362dc.us-south.apigw.appdomain.cloud/api/dealership/api/review"
        post_request(url, data=doc)
        post_review(json.dumps(data))
        return redirect("djangoapp:index")

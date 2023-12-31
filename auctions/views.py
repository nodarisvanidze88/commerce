from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Category, Listing


def index(request):
    activeListings = Listing.objects.filter(isActive=True)
    allCategory = Category.objects.all()
    return render(request, "auctions/index.html", {
        "listings":activeListings,
        "categories" : allCategory
        })
def listing(request, id):
    listingData = Listing.objects.get(pk=id)
    isListingInWatchlist = request.user in listingData.watchlist.all()
    print(isListingInWatchlist)
    return render(request, "auctions/listing.html", {
        "listing" : listingData,
        "isListingInWatchlist" : isListingInWatchlist
    })
def removeWatchlist(request, id):
    listingData = Listing.objects.get(pk=id)
    currentUser = request.user
    listingData.watchlist.remove(currentUser)
    return HttpResponse(reverse("listing",args=(id, )) )

def addWatchlist(request, id):
    listingData = Listing.objects.get(pk=id)
    currentUser = request.user
    listingData.watchlist.add(currentUser)
    return HttpResponse(reverse("listing",args=(id, )) )

def displayCategory(request):
    if request.method == "POST":
        categoryFromForm = request.POST["category"]
        category = Category.objects.get(categoryName=categoryFromForm)
        activeListings = Listing.objects.filter(isActive=True, category=category)
        allCategory = Category.objects.all()
        return render(request, "auctions/index.html", {
            "listings":activeListings,
            "categories" : allCategory
            })

def createListing(request):
    if request.method=="GET":
        allCategory = Category.objects.all()
        return render(request, "auctions/create.html", {
            "categories": allCategory
            })
    else:
        request.method=="POST"
        title = request.POST["title"]
        description = request.POST["description"]
        imageUrl = request.POST["imageurl"]
        price = request.POST["price"]
        category = request.POST["category"]
        currentUser = request.user
        categoryData= Category.objects.get(categoryName=category)
        newListing = Listing(
            title = title,
            description = description,
            imageUrl = imageUrl,
            price = float(price),
            category= categoryData,
            owner = currentUser
            )
        newListing.save()
        return HttpResponseRedirect(reverse(index))
def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

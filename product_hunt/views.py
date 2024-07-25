from django.shortcuts import render
from django.http import HttpResponse
from django.utils import timezone
from django.http import HttpResponseRedirect
from django.urls import reverse
from rest_framework import viewsets
from .models import Product, Website
from .serializers import ProductSerializer, WebsiteSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .scrapers import AmazonScraper # EbayScraper, BestBuyScraper  # Add other scrapers here
from textblob import TextBlob

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class WebsiteViewSet(viewsets.ModelViewSet):
    queryset = Website.objects.all()
    serializer_class = WebsiteSerializer


@api_view(['POST'])
def scrape_and_store(request):
    keyword = request.data.get('keyword')
    if not keyword:
        return Response({'error': 'Keyword not provided'}, status=400)

    urls = [
        f'https://www.amazon.com/s?k={keyword}',
        f'https://www.ebay.com/sch/i.html?_nkw={keyword}',
        f'https://www.bestbuy.com/site/searchpage.jsp?st={keyword}'
    ]

    scrapers = [AmazonScraper, EbayScraper, BestBuyScraper]
    
    for url, Scraper in zip(urls, scrapers):
        scraper = Scraper(url)
        product_data = scraper.scrape()
        website, _ = Website.objects.get_or_create(name=scraper.website_name, url=url)
        for product in product_data:
            sentiment_score = analyze_sentiment(product['reviews'])
            Product.objects.create(
                name=product['name'],
                price=product['price'],
                reviews=product['reviews'],
                product_url=product['product_url'],
                image_url=product['image_url'],
                website=website,
                sentiment_score=sentiment_score
            )

    return Response({'message': 'Data scraped successfully'}, status=200)



@api_view(['POST'])
def analyze_sentiment(request):
    product_id = request.data.get('product_id')
    if not product_id:
        return Response({'error': 'Product ID not provided'}, status=400)

    try:
        product = Product.objects.get(id=product_id)
        # Call your sentiment analysis API here
        sentiment_score = get_sentiment_score(product.reviews)
        product.sentiment_score = sentiment_score
        product.save()
        return Response({'sentiment_score': sentiment_score}, status=200)
    except Product.DoesNotExist:
        return Response({'error': 'Product not found'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)
def index(request):
    return HttpResponseRedirect(reverse('product_list'))

def current_time(request):
    now = timezone.now()
    html = f"<html><body>Current time: {now}</body></html>"
    return HttpResponse(html)

def product_list(request):
    products = Product.objects.all()
    if not products:
        message = "No products found."
        return render(request, 'product_hunt/no_products.html', {'message': message})
    return render(request, 'product_hunt/product_list.html', {'products': products})


@api_view(['GET'])
def search_products(request):
    query = request.GET.get('query', '')
    
    if not query:
        return JsonResponse({'error': 'Query parameter is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Perform scraping here and save data
        # For simplicity, we assume data is already in the database
        
        products = Product.objects.filter(name__icontains=query)
        if not products.exists():
            return JsonResponse({'message': 'No products found'}, status=status.HTTP_404_NOT_FOUND)

        product_serializer = ProductSerializer(products, many=True)
        
        # Perform sentiment analysis
        for product in products:
            product.sentiment_score = analyze_sentiment(product.reviews)
            product.save()

        # Find the best product based on price and sentiment score
        best_product = find_best_product(products)  # Implement this function to return the best product

        return JsonResponse({
            'products': product_serializer.data,
            'best_product': ProductSerializer(best_product).data if best_product else None
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def find_best_product(products):
    """
    Finds the best product based on price and sentiment score.
    """
    best_product = None
    highest_score = float('-inf')
    
    for product in products:
        score = product.sentiment_score - product.price  # Example scoring formula
        if score > highest_score:
            highest_score = score
            best_product = product
    
    return best_product
    

def analyze_sentiment(review):
    analysis = TextBlob(review)
    return analysis.sentiment.polarity
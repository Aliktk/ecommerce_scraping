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
        scraper.scrape()

    return Response({'message': 'Data scraped successfully'}, status=200)

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
        if not products:
            return JsonResponse({'message': 'No products found'}, status=status.HTTP_404_NOT_FOUND)

        product_serializer = ProductSerializer(products, many=True)
        
        # Perform sentiment analysis
        # Assuming sentiment analysis is performed and added to the data
        best_product = find_best_product(products)  # Implement this function to return the best product

        return JsonResponse({
            'products': product_serializer.data,
            'best_product': best_product
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def find_best_product(products):
    # Dummy implementation; replace with your logic
    try:
        best_product = max(products, key=lambda p: (p.price, p.sentiment_score))
        return ProductSerializer(best_product).data
    except Exception as e:
        return {'error': f'Error finding best product: {str(e)}'}
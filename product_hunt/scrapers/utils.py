from product_hunt.models import Website, Product
def save_to_database(product_data):
    website, created = Website.objects.get_or_create(name='Amazon', url=self.base_url)
    for product in product_data:
        Product.objects.create(
            name=product['name'],
            price=product['price'],
            reviews=product['reviews'],
            url=product['product_url'],
            image_url=product['image_url'],
            website=website
        )
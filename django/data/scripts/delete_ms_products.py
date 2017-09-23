if __name__ == "__main__":

    from pathlib import Path
    import sys

    project_dir = str(Path().resolve().parents[1])
    sys.path.append('%s/' % project_dir)

    import django
    from redington import settings

    DJANGO_SETTINGS_MODULE = settings
    django.setup()

    from products.models import Products
    from orders.models import Orders

    order_placed_prod_ids = Orders.objects.filter(vendor__vendor_name='Microsoft').values_list('items__product__pk', flat=True)

    order_placed_prod_ids = list(set(order_placed_prod_ids))

    products_to_be_deleted = Products.objects.filter(vendor_details__vendor_name='Microsoft', product_featured=False).exclude(pk__in=order_placed_prod_ids)

    print(products_to_be_deleted.delete())

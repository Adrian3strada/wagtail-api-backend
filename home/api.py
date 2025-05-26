from wagtail.api.v2.views import PagesAPIViewSet
from wagtail.models import Site
from wagtail.api.v2.router import WagtailAPIRouter
from rest_framework.response import Response

class CustomPagesAPIViewSet(PagesAPIViewSet):

    def listing_view(self, request, *args, **kwargs):
        # Llama la vista original
        response = super().listing_view(request, *args, **kwargs)

        # Encuentra el sitio actual y la página raíz
        site = Site.find_for_request(request)
        root_page = site.root_page if site else None

        menu_items = []

        if root_page:
            for page in root_page.get_children().live().in_menu():
                item = {
                    'title': page.title,
                    'url': page.url,
                    'children': []
                }

                # Añade submenú si tiene hijos en menú
                for child in page.get_children().live().in_menu():
                    item['children'].append({
                        'title': child.title,
                        'url': child.url
                    })

                menu_items.append(item)

        # Añade el menú a la respuesta JSON
        response.data['navbar'] = menu_items
        return response

from wagtail.api.v2.views import PagesAPIViewSet
from wagtail.models import Site
from wagtail.api.v2.router import WagtailAPIRouter
from rest_framework.response import Response
from wagtail.api.v2.views import BaseAPIViewSet
from home.models import FooterLink
from .models import CustomPage

class CustomPagesAPIViewSet(PagesAPIViewSet):

    def listing_view(self, request, *args, **kwargs):
        response = super().listing_view(request, *args, **kwargs)

        site = Site.find_for_request(request)
        root_page = site.root_page if site else None

        menu_items = []

        if root_page:
            menu_items.append({
                'title': root_page.title,
                'url': root_page.url,
                'children': []
            })

            for page in root_page.get_children().live().in_menu():
                item = {
                    'title': page.title,
                    'url': page.url,
                    'children': []
                }
                for child in page.get_children().live().in_menu():
                    item['children'].append({
                        'title': child.title,
                        'url': child.url
                    })

                menu_items.append(item)

        response.data['navbar'] = menu_items
        return response


class FooterAPIViewSet(BaseAPIViewSet):
    model = FooterLink
    meta_fields = ['id']
    listing_default_fields = ['titulo', 'url']
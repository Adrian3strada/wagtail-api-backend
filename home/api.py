from wagtail.api.v2.views import PagesAPIViewSet, BaseAPIViewSet
from wagtail.models import Site
from rest_framework.response import Response
from home.models import FooterLink, SiteBranding  # Importa SiteBranding correctamente
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

        # Obtener branding del sitio
        branding = SiteBranding.for_request(request)
        logo_url = branding.logo.file.url if branding.logo else None
        favicon_url = branding.favicon.file.url if branding.favicon else None

        # Añadir navbar, logo y favicon a la respuesta
        response.data['navbar'] = menu_items
        response.data['logo'] = logo_url
        response.data['favicon'] = favicon_url

        return response


class FooterAPIViewSet(BaseAPIViewSet):
    model = FooterLink
    meta_fields = ['id']
    listing_default_fields = ['titulo', 'url']

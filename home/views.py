# home/api/views.py

from wagtail.models import Page
from rest_framework.views import APIView
from rest_framework.response import Response
from home.models import SiteBranding  # importa tu modelo de branding

def build_menu_tree(page):
    children = page.get_children().live().in_menu().order_by('path')
    return {
        "title": page.title,
        "url": page.url,
        "children": [build_menu_tree(child) for child in children]
    }

class NavbarAPIView(APIView):
    def get(self, request):
        root_page = Page.get_first_root_node()
        first_level_pages = root_page.get_children().live().in_menu().order_by('path')
        menu = [build_menu_tree(page) for page in first_level_pages]

        # Obtén logo y favicon
        branding = SiteBranding.for_request(request)
        logo_url = branding.logo.file.url if branding.logo else None
        favicon_url = branding.favicon.file.url if branding.favicon else None

        return Response({
            "navbar": menu,
            "logo": logo_url,
            "favicon": favicon_url
        })

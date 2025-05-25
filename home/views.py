from rest_framework.views import APIView
from rest_framework.response import Response
from wagtail.models import Page

class NavbarMenuAPI(APIView):
    def get(self, request):
        site_root = Page.get_first_root_node()
        menu_pages = site_root.get_children().live().in_menu()

        data = [
            {
                'title': page.title,
                'url': page.url,
                'slug': page.slug
            }
            for page in menu_pages
        ]
        return Response(data)

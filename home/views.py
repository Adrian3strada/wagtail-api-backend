from wagtail.models import Site
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import NavItem
from .serializers import NavItemSerializer


def menu_api(request):
    site = Site.find_for_request(request)
    root_page = site.root_page

    menu_items = []

    for page in root_page.get_children().live().in_menu():
        item = {
            'title': page.title,
            'url': page.url,
            'children': [
                {
                    'title': child.title,
                    'url': child.url
                } for child in page.get_children().live().in_menu()
            ]
        }
        menu_items.append(item)

    return JsonResponse(menu_items, safe=False)




class NavbarAPIView(APIView):
    def get(self, request):
        items = NavItem.objects.all().order_by('order')
        serializer = NavItemSerializer(items, many=True)
        return Response(serializer.data)
from wagtail.models import Page
from rest_framework.views import APIView
from rest_framework.response import Response

class NavbarAPIView(APIView):
    def get(self, request):
        menu_items = Page.objects.filter(live=True, show_in_menus=True)

        data = []
        for item in menu_items:
            children = item.get_children().live().in_menu()
            data.append({
                "title": item.title,
                "url": item.url,
                "children": [
                    {
                        "title": child.title,
                        "url": child.url
                    }
                    for child in children
                ]
            })

        return Response(data)

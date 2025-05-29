from wagtail.models import Page, Site
from rest_framework.views import APIView
from rest_framework.response import Response

class NavbarAPIView(APIView):
    def get(self, request):
        site = Site.objects.get(is_default_site=True)
        root = site.root_page

        data = []


        if root.live:
            data.append({
                "title": "Inicio",
                "url": root.url,
                "children": []
            })

        menu_items = Page.objects.filter(live=True, show_in_menus=True).exclude(id=root.id)

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

        return Response({"navbar": data})

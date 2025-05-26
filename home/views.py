from wagtail.models import Site
from django.http import JsonResponse

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

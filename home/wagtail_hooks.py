from wagtail import hooks
from wagtail.admin.menu import MenuItem
from django.templatetags.static import static
from django.utils.html import format_html

@hooks.register('construct_page_subpage_menu')
def limit_subpage_types(menu_items, request, parent_page):
    from .models import HomePage, StandardPage  
    if isinstance(parent_page.specific, HomePage):
        allowed = ['StandardPage']
        menu_items[:] = [item for item in menu_items if item.name in allowed]

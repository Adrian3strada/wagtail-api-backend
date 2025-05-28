from rest_framework import serializers
from .models import NavItem

class NavItemSerializer(serializers.ModelSerializer):
    page_url = serializers.SerializerMethodField()
    children = serializers.SerializerMethodField()

    class Meta:
        model = NavItem
        fields = ['title', 'page_url', 'children']

    def get_page_url(self, obj):
        return obj.page.url

    def get_children(self, obj):
        children = obj.page.get_children().live().in_menu()
        return [
            {
                "title": child.title,
                "url": child.url
            }
            for child in children
        ]
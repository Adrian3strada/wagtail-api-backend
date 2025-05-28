from rest_framework import serializers
from .models import NavItem

class NavItemSerializer(serializers.ModelSerializer):
    page_url = serializers.SerializerMethodField()
    children = serializers.SerializerMethodField()

    class Meta:
        model = NavItem
        fields = ['title', 'page_url', 'children']

    def get_page_url(self, obj):
        return obj.page.url if obj.page else None

    def get_children(self, obj):
        children = obj.children.all().order_by('order')
        return NavItemSerializer(children, many=True).data

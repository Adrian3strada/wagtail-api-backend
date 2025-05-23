from django.db import models
from wagtail.models import Page
from wagtail.fields import StreamField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.api import APIField
from wagtail.images.blocks import ImageChooserBlock
from wagtail import blocks
from wagtail.fields import RichTextField



QUASAR_COLOR_CHOICES = [
    ('primary', 'Primary'),
    ('secondary', 'Secondary'),
    ('accent', 'Accent'),
    ('dark', 'Dark'),
    ('positive', 'Positive'),
    ('negative', 'Negative'),
    ('info', 'Info'),
    ('warning', 'Warning'),
]

class TestimonioBlock(blocks.StructBlock):
    nombre = blocks.CharBlock(label="Nombre")
    comentario = blocks.TextBlock(label="Comentario")
    imagen = ImageChooserBlock(required=False, label="Imagen (opcional)")

    class Meta:
        icon = "user"
        label = "Testimonio"


class TestimoniosBlock(blocks.StructBlock):
    testimonios = blocks.ListBlock(TestimonioBlock(), label="Lista de testimonios")

    class Meta:
        template = "blocks/testimonios_block.html"
        icon = "group"
        label = "Testimonios"

class CarouselImageBlock(blocks.StructBlock):
    image = ImageChooserBlock(required=True, label="Imagen")
    caption = blocks.CharBlock(required=False, label="Texto opcional", max_length=250)

    class Meta:
        icon = "image"
        label = "Imagen del Carrusel"

class HoverImageBlock(blocks.StructBlock):
    image = ImageChooserBlock(required=True, label="Imagen")
    texto_overlay = blocks.CharBlock(required=False, label="Texto sobre la imagen")
    color_overlay = blocks.ChoiceBlock(
        choices=QUASAR_COLOR_CHOICES,
        label="Color del overlay (Quasar)",
        required=False,
        help_text="Color que se verá al pasar el mouse"
    )

    class Meta:
        template = "blocks/hover_image_block.html"
        icon = "image"
        label = "Imagen con Hover"

class CarouselBlock(blocks.StructBlock):
    images = blocks.ListBlock(CarouselImageBlock(), label="Imágenes")

    class Meta:
        icon = "image"
        label = "Carrusel de imágenes"
        template = "blocks/carrusel_block.html"

class ButtonBlock(blocks.StructBlock):
    text = blocks.CharBlock(required=True, help_text="Texto del botón")
    url = blocks.URLBlock(required=True, help_text="Enlace del botón")
    style = blocks.ChoiceBlock(
        choices=[
            ('primary', 'Primary'),
            ('secondary', 'Secondary'),
            ('success', 'Success'),
            ('danger', 'Danger'),
            ('warning', 'Warning'),
        ],
        default='primary',
        required=False,
        help_text="Estilo del bot"
    )

    class Meta:
        template = 'blocks/button_block.html'
        icon = 'placeholder'
        label = 'Botón'

class VideoBlock(blocks.StructBlock):
    video_url = blocks.URLBlock(label="URL del video (YouTube o Vimeo)")

    class Meta:
        icon = "media"
        label = "Video embebido"
        template = "blocks/video_block.html"


class GalleryImageBlock(blocks.StructBlock):
    image = ImageChooserBlock(required=True, label="Imagen")
    caption = blocks.CharBlock(required=False, label="Texto opcional", max_length=250)

    class Meta:
        icon = "image"
        label = "Imagen de galería"


class GalleryBlock(blocks.StructBlock):
    images = blocks.ListBlock(GalleryImageBlock(), label="Imágenes")

    class Meta:
        icon = "image"
        label = "Galería de imágenes"
        template = "blocks/gallery_block.html"

class IframeBlock(blocks.StructBlock):
    iframe_url = blocks.URLBlock(label="URL del contenido embebido")
    height = blocks.IntegerBlock(default=400, label="Altura (px)")

    class Meta:
        icon = "code"
        label = "Contenido embebido (iframe)"
        template = "blocks/iframe_block.html"


common_streamfield = [
    ('heading', blocks.CharBlock(classname="full title", label="Encabezado")),
    ('paragraph', blocks.RichTextBlock(label="Párrafo enriquecido")),
    ('plain_text', blocks.TextBlock(label="Texto simple")),
    ('image', ImageChooserBlock(label="Imagen")),
    ('gallery', GalleryBlock()),
    ('carousel', CarouselBlock()),
    ('button', ButtonBlock()),
    ('video', VideoBlock()),
    ('iframe', IframeBlock()),
    ('hover_image', HoverImageBlock()),
    ('testimonios', TestimoniosBlock()),
]

class BaseContentPage(Page):
    body = StreamField(common_streamfield, use_json_field=True, blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("body"),
    ]

    api_fields = [
        APIField("body"),
    ]

    class Meta:
        abstract = True

class HomePage(BaseContentPage):
    subpage_types = [
        'home.NoticiasIndexPage',
        'home.EventosIndexPage',
        'home.ContactoPage',
        'home.PaginaInformativaPage',
    ]
    class Meta:
        verbose_name = "Inicio"


class NoticiasIndexPage(BaseContentPage):
    subpage_types = ['home.NoticiaPage']
    parent_page_types = ['home.HomePage']

class NoticiaPage(BaseContentPage):
    fecha = models.DateField("Fecha de Publicación", auto_now_add=True, editable=False)

    content_panels = BaseContentPage.content_panels + [
        
    ]

    api_fields = BaseContentPage.api_fields + [
        APIField("fecha"),
    ]

    subpage_types = []
    parent_page_types = ['home.NoticiasIndexPage']

class EventosIndexPage(BaseContentPage):
    subpage_types = ['home.EventoPage']
    parent_page_types = ['home.HomePage']

class EventoPage(BaseContentPage):
    fecha = models.DateTimeField("Fecha del Evento")
    ubicacion = models.CharField("Ubicación", max_length=255)

    content_panels = BaseContentPage.content_panels + [
        FieldPanel("fecha"),
        FieldPanel("ubicacion"),
    ]

    api_fields = BaseContentPage.api_fields + [
        APIField("fecha"),
        APIField("ubicacion"),
    ]

    subpage_types = []
    parent_page_types = ['home.EventosIndexPage']


class PaginaInformativaPage(BaseContentPage):  
    parent_page_types = ['home.HomePage']
    subpage_types = []




class ContactoPage(BaseContentPage):
    telefono = models.CharField("Teléfono", max_length=20, blank=True)
    email = models.EmailField("Correo Electrónico", blank=True)
    direccion = models.TextField("Dirección", blank=True)
    horario = models.TextField("Horario", blank=True)


    content_panels = BaseContentPage.content_panels + [
        FieldPanel("telefono"),
        FieldPanel("email"),
        FieldPanel("direccion"),
        FieldPanel("horario"),
    ]

    api_fields = BaseContentPage.api_fields + [
        APIField("telefono"),
        APIField("email"),
        APIField("direccion"),
        APIField("horario"),
    ]

    parent_page_types = ['home.HomePage']
    subpage_types = []
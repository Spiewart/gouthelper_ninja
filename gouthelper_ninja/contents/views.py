from django.views.generic import TemplateView


class Home(TemplateView):
    template_name = "contents/home.html"

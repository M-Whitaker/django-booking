from django.views.generic import TemplateView
from .tasks import show_hello_world
from .models import DemoModel
import django

# Create your views here.


class ShowHelloWorld(TemplateView):
    template_name = "home.html"

    def get(self, *args, **kwargs):
        show_hello_world.apply()
        return super().get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["demo_content"] = DemoModel.objects.all()
        context["version"] = django.get_version()
        return context

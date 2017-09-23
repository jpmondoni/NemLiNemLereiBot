import re
from jinja2 import Environment, FileSystemLoader


def render_template(template_name, **kwargs):
    environment = Environment(loader=FileSystemLoader('templates'))
    template = environment.get_template(template_name)
    return template.render(kwargs)

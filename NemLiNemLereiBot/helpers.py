import re
from jinja2 import Environment, FileSystemLoader


def render_template(template_name, **kwargs):
    environment = Environment(loader=FileSystemLoader('templates'))
    template = environment.get_template(template_name)
    return template.render(kwargs)


def percentage_decrease(content, summary):
    content_length = len(content)
    summary_length = len(summary)

    decrease = (((content_length - summary_length) / content_length) * 100)

    return decrease

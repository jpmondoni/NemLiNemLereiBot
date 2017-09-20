import re
import archiveis
from jinja2 import Environment, FileSystemLoader


def url_matches_plugin(PluginManager, url):
    loaded_plugins = PluginManager.loaded_plugins
    for plugin, pattern in loaded_plugins.items():
        if re.match(pattern, url):
            return plugin


def get_archiveis_url(url):
    archive_url = archiveis.capture(url)
    return archive_url


def render_template(template_name, **kwargs):
    environment = Environment(loader=FileSystemLoader('templates'))
    template = environment.get_template(template_name)
    return template.render(kwargs)

from pluginbase import PluginBase


class PluginManager():
    def __init__(self):
        self.plugin_source = PluginBase(
            package='plugins').make_plugin_source(searchpath=['plugins'])
        self.loaded_plugins = {}
        self.load_plugins()

    def register_plugin(self, plugin, url_pattern):
        self.loaded_plugins[plugin] = url_pattern

    def load_plugins(self):
        for plugin_name in self.plugin_source.list_plugins():
            plugin = self.get_plugin(plugin_name)
            plugin.register_plugin(self)

    def get_plugin(self, plugin_name):
        plugin = self.plugin_source.load_plugin(plugin_name).Plugin()
        return plugin

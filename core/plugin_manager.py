import os
import sys
import importlib
import logging


logger = logging.getLogger('plugman')

class PluginManager:
    def __init__(self, plugins_location: str, bot_instance):
        logger.info('Initializing plugin manager')
        self.bot = bot_instance

        self._plugins = []  # Plugin modules
        self.plugins = []  # Instantiated plugins
        self.events = {}  # Dictionary of events to list of plugins that have implemented that event

        # Walk down the plugins folder and load them
        for root, folders, files in os.walk(plugins_location):
            for file in files:
                filename, ext = os.path.splitext(file)
                if ext == '.py' and not filename.startswith('__'):
                    try:
                        plugin = importlib.import_module('.'.join((root.replace('/', '.'), filename)))
                        # Skip disabled plugins
                        if plugin.Plugin.disabled:
                            continue
                        instantiated_plugin = plugin.Plugin(self.bot)
                        # Iterate over implemented events
                        for event_name in [key
                                           for key in plugin.Plugin.__dict__
                                           if key.startswith('on_')]:
                            if event_name not in self.events.keys():
                                self.events[event_name] = []
                            self.events[event_name].append(instantiated_plugin)
                        self._plugins.append(plugin)
                        self.plugins.append(instantiated_plugin)
                        logger.info(f'{os.path.join(root, file)} loaded')
                    except AttributeError:
                        logging.error(f'! Failed to load {os.path.join(root, file)}')

        self._sort_on_message()
        logger.info('Initialized')

    def _sort_on_message(self):
        """Sort `on_message` events into {trigger: [plugins]} dictionary"""
        if 'on_message' in self.events.keys():
            trigger_to_plugin = {}
            for plugin in self.events['on_message']:
                for trigger in getattr(plugin, 'triggers', ()):
                    if trigger not in trigger_to_plugin.keys():
                        trigger_to_plugin[trigger] = []
                    trigger_to_plugin[trigger].append(plugin)
            self.events['on_message'].clear()
            self.events['on_message'] = trigger_to_plugin

    def reload(self):
        logger.info('Reloading plugins')
        # Invalidate instantiated plugins
        self.plugins.clear()
        self.events.clear()
        for plugin in self._plugins:
            logger.info(f'Reloading {plugin.Plugin.name}')
            importlib.reload(plugin)  # Reload module
            instantiated_plugin = plugin.Plugin(self.bot)  # Reinstantiate
            # Iterate over implemented events
            for event_name in [key
                               for key in plugin.Plugin.__dict__
                               if key.startswith('on_')]:
                if event_name not in self.events.keys():
                    self.events[event_name] = []
                self.events[event_name].append(instantiated_plugin)
            self.plugins.append(instantiated_plugin)
        self._sort_on_message()
        logger.info('Reloaded')

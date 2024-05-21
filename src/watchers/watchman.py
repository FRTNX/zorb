import time
import threading

from logging import Logger
from .watcher_utils import online

from .libera_chat_watcher import LiberaChatWatcher
from .ycombinator_watcher import YCombinatorWatcher
from .techcrunch_watcher import TechCrunchWatcher

from event_stream import EventStream

ACTIVE_WATCHERS = [LiberaChatWatcher, YCombinatorWatcher, TechCrunchWatcher]

class WatchMan:
    """Manages all watchers."""
    WATCHERS = []

    def __init__(self, event_stream: EventStream, config: dict, logging: Logger):
        self._event_stream = event_stream
        self._logging = logging
        self._config = config
        self._online = online()
        self._watchers_active = False

        for Watcher in ACTIVE_WATCHERS:                   # instantiate active watchers
            self.WATCHERS.append(Watcher(event_stream=event_stream,
                                         config=config[Watcher.NAME], logging=logging))

    def deploy(self):
        """Deploy all watchers in watchers list."""
        for watcher in self.WATCHERS:
            watcher.start()
            self._logging.info(watcher.NAME + ' watcher deployed.')
        self._watchers_active = True
        connection_thread = threading.Thread(target=self._monitor_connection)
        connection_thread.start()

    def terminate(self):
        """Terminate all currently deployed watchers."""
        for watcher in self.WATCHERS:
            watcher.stop()
            self._logging.info(watcher.NAME + ' terminated.')
        self._watchers_active = False

    def _monitor_connection(self):
        """Stops watchers if offline."""
        while True:
            zorb_online = online()
            self._logging.info(f'Is online: {zorb_online}')  # remove after resolving double subs on redeploys 

            if zorb_online and not self._watchers_active:
                self._logging.info('Connection established. Deploying watchers...')
                self.deploy()                                # redeploy watchers once online again

            if not zorb_online and self._watchers_active:
                self._logging.info('Connection lost. Stopping watchers...')
                self.terminate()
            time.sleep(self._config['connection_test_interval'])


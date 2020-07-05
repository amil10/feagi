"""
Source: https://camcairns.github.io/python/2017/09/06/python_watchdog_jobs_queue.html

This class inherits from the Watchdog PatternMatchingEventHandler class. In this code our watchdog will only be
triggered if a file is moved to have a .trigger extension. Once triggered the watchdog places the event object on the
queue, ready to be picked up by the worker thread
"""

from watchdog.events import PatternMatchingEventHandler


class FileLoaderWatchdog(PatternMatchingEventHandler):
    ''' Watches a nominated directory and when a trigger file is
        moved to take the ".trigger" extension it proceeds to execute
        the commands within that trigger file.

        Notes
        ============
        Intended to be run in the background
        and pickup trigger files generated by other ETL process
    '''

    def __init__(self, queue, patterns):
        PatternMatchingEventHandler.__init__(self, patterns=patterns)
        self.queue = queue

    def process(self, event):
        '''
        event.event_type
            'modified' | 'created' | 'moved' | 'deleted'
        event.is_directory
            True | False
        event.src_path
            path/to/observed/file
        '''
        self.queue.put(event)

    def on_moved(self, event):
        self.process(event)


def process_image(q):
    event = q.get()
    print('\n\n\n\n\n\n\nImage is being processed!!!!\n\n\n\n\n\n', event)

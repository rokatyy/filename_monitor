#!/usr/bin/python3
import pandas as pd
import os, sys
import time
import re
import json
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# variables
template_file_path = '/home/rokatyy/labs/lab1/template.tbl'
controlled_path = '/home/rokatyy/labs/lab1/'


class Controller:
    def __init__(self):
        self.TEMPLATE_FILE = template_file_path
        data = self._read_template_file()
        self.forbidden_names = data["names"]
        self.forbidden_extensions = tuple(
            ['.{}'.format(extension) for extension in data["extensions"]])
        self.forbidden_regex = data["regex"]

    def _read_template_file(self):
        """G
        Reads template file
        if not exists, returns exception
        """
        try:
            return json.loads(open(self.TEMPLATE_FILE,'r').read())
        except FileNotFoundError:
            sys.stdout.write("Template-file does not exist.\n")
        except OSError as e:
            sys.stdout.write(
                "Error: \'{}\' occured while reading the template file. It could be possibly insufficient access.\n".
                format(e))

    @staticmethod
    def __parse_full_path(path):
        """
        Parses file path and returns dir and file separately 
        Args:
            path (str) - full file path
        Return:
            dir (str) - file directory
            name (str) - file name
        """
        dir = path[:path.rfind('/') + 1]
        name = path[path.rfind('/') + 1:]
        return dir, name

    def check_is_event_valid(self, event):
        """
        Checks filename which active in event. In case of any forbitten option file will be deleted.
        Args: 
            event (FileSystemEventHandler object) - current system event

        """
        if event.src_path == template_file_path:
            self.__init__()
        if not hasattr(event, 'dest_path'):
            event.dest_path = None
        for path in [event.src_path, event.dest_path]:
            if path is not None:
                dir, name = self.__parse_full_path(path)
                if dir.find(controlled_path
                            ) >= 0 and not self._check_is_name_valid(name):
                    if path == event.dest_path:
                        os.system('cp {dest} {src}'.format(
                            dest=event.dest_path, src=event.src_path))
                    os.system('rm -rf {dir}{name}'.format(dir=dir, name=name))

    def __check_is_match_regex(self, name):
        for regex in self.forbidden_regex:
            if re.match(regex, name):
                return True
        return False

    def _check_is_name_valid(self, name):
        """
        Checks if name allowed
        Args: 
            name (str) - just filename. Be aware that there are shouln't be directory path inside.
        """
        if name in self.forbidden_names or name.endswith(
                self.forbidden_extensions) or self.__check_is_match_regex(name):
            return False
        return True


class Watcher:
    WATCH_DIR = controlled_path

    def __init__(self):
        self.observer = Observer()
        self.event_handler = EventHandler()

    def run(self):
        self.observer.schedule(
            self.event_handler, self.WATCH_DIR, recursive=True)
        self.observer.start()
        try:
            while True:
                time.sleep(1)
        except:
            self.observer.stop()
            print("Error")

        self.observer.join()


class EventHandler(FileSystemEventHandler):
    def __init__(self):
        self.controller = Controller()

    def on_any_event(self, event):
        self.controller.check_is_event_valid(event)


def main():
    w = Watcher()
    w.run()


if __name__ == '__main__':
    main()

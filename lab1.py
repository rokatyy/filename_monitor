#!/usr/bin/python3
import pandas as pd
import os,sys
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# variables
template_file_path = '/home/rokatyy/labs/lab1/template.tbl'
controlled_path = '/home/rokatyy/labs/lab1/'

class Controller:
    
    def __init__(self):

        self.TEMPLATE_FILE = template_file_path
        data = self.read_template_file()
        self.forbitten_names = list(data.names)

    def read_template_file(self):
    	"""
    	Reads template file
    	if not exists, returns exception
    	"""
    	try:
    		return pd.read_csv(self.TEMPLATE_FILE)
    	except FileNotFoundError:
    		sys.stdout.write("Template-file does not exist.\n")
    	except OSError as e:
    		sys.stdout.write("Error: \'{}\' occured while reading the template file. It could be possibly insufficient access.\n".format(e))

    @staticmethod
    def __parse_full_path(path):
        return path[:path.rfind('/')+1],path[path.rfind('/')+1:]
 
    def check_is_event_valid(self, event):
        """"""
        path, name = self.__parse_full_path(event.src_path)
        if path.find(controlled_path) >= 0 :
            self.check_is_name_valid(name)

    def check_is_name_valid(self, name):
        if name in self.forbitten_names:
            os.system('rm -rf {file}'.format(file = name))


class Watcher:
    WATCH_DIR = controlled_path

    def __init__(self):
        self.observer = Observer()

    def run(self):
        event_handler = EventHandler()
        self.observer.schedule(event_handler, self.WATCH_DIR, recursive=True)
        self.observer.start()
        try:
            while True:
                time.sleep(1)
        except:
            self.observer.stop()
            print("Error")

        self.observer.join()


class EventHandler(FileSystemEventHandler):
    controller = Controller()

    def on_any_event(self,event):
        self.controller.check_is_event_valid(event)

if __name__ == '__main__':
    w = Watcher()
    w.run()
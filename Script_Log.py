# module for generating logs
import os
from datetime import datetime

class Script_Log:

    def __init__(self, name, path):
        self.fileObj = open(os.path.join(path, name+'.txt'),'w')
        print('Starting the log')

    def record_event(self, msg):
        self.fileObj.write(str(datetime.now())+': ' + msg + '\n')

    def end_log(self):
        self.fileObj.close()
        print('Log finished')
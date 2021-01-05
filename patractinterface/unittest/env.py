import json
import time
import logging
import threading
from subprocess import *
from executor import execute_prepared, ExternalCommand

class SubstrateTestEnv:
    def __init__(self, type_def, port, logLv = logging.DEBUG):
        self.type_def = type_def
        self.port = port
        self.logLv = logLv
        self.thread = None

        self.name = f'test_{self.type_def}_{self.port}'
        args = " --name {} --tmp -lruntime=debug --ws-port {}".format(self.name, self.port)
        if type_def != 'europa':
            args += ' --dev'
        self.cmd = self.type_def + args
        self.ec = ExternalCommand(self.cmd)

    @classmethod
    def create_canvas(cls, port=9944):
        return cls(type_def='canvas', port=port)

    @classmethod
    def create_europa(cls, port=9944):
        return cls(type_def='europa', port=port)

    def start_node(self):
        logging.info("run cmd {}".format(self.cmd))

        def loggerThread():
            self.ec.start()
            self.pid = self.ec.pid
            self.ec.wait()

        self.thread = threading.Thread(target=loggerThread, name=self.name)
        self.thread.start()

        time.sleep(3) # for startup

        logging.info("start_node {}".format(self.name))
        return

    def stop_node(self):
        self.ec.kill()
        return

    def url(self) -> str:
        return f'ws://127.0.0.1:{self.port}'

    def typ(self) -> str:
        if self.type_def == 'canvas':
            return 'canvas'

        if self.type_def == 'europa':
            return 'default'

    def types(self) -> dict:
        if self.type_def == 'canvas':
            return {'types': {"Address": "AccountId", "LookupSource": "AccountId"}}
        if self.type_def == 'europa':
            return {'types': {'LookupSource': 'MultiAddress'}}
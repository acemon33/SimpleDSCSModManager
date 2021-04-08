import os

from PyQt5 import QtCore

    
class ScriptWorker:
    def __init__(self, origin, destination, script_func, threadpool, func_message, func_message_past,
                  lockGuiFunc, releaseGuiFunc, messageLogFunc, updateMessageLogFunc,
                  remove_input=False):
        self.origin = origin
        self.destination = destination
        self.script_func = script_func
        self.ncomplete = 0
        self.njobs = 0
        self.threadpool = threadpool
        self.func_message = func_message
        self.func_message_past = func_message_past
        self.remove_input = remove_input
        
        self.lockGuiFunc = lockGuiFunc
        self.releaseGuiFunc = releaseGuiFunc
        self.messageLogFunc = messageLogFunc
        self.updateMessageLogFunc = updateMessageLogFunc

        
    def run(self):
        self.ncomplete = 0
        try:
            self.lockGuiFunc()
            scripts = os.listdir(self.origin)
            self.njobs = len(scripts)
            if len(scripts):
                self.messageLogFunc("")
            else:
                self.messageLogFunc(f"Zero scripts at {self.origin} to decompile.")
                self.releaseGuiFunc()
                return
            for script in scripts:
                job = ScriptRunnable(self.script_func,
                                     script, self.origin, self.destination,
                                     self.update_messagelog,
                                     self.update_finished,
                                     self.raise_exception,
                                     self.remove_input)
                job.signals.exception.connect(self.raise_exception)
                job.signals.update_messagelog.connect(self.update_messagelog)
                job.signals.update_finished.connect(self.update_finished)
                self.threadpool.start(job)
        except Exception as e:
            self.raise_exception(e)
            
    def update_finished(self):
        if self.ncomplete == self.njobs:
            self.releaseGuiFunc()
                
    def update_messagelog(self, message):
        self.ncomplete += 1
        self.updateMessageLogFunc(f"{self.func_message_past} script {self.ncomplete}/{self.njobs} [{message}]")
        
    def raise_exception(self, exception):
        try:
            raise exception
        except ScriptHandlerError as e:
            self.threadpool.clear()
            self.threadpool.waitForDone()
            self.messageLogFunc(f"The following exception occured when {self.func_message} script {e.args[1]}: {e.args[0]}")
            raise e.args[0]
        except Exception as e:
            self.threadpool.clear()
            self.threadpool.waitForDone()
            self.messageLogFunc(f"The following exception occured when {self.func_message} scripts: {e}")
            raise e
        finally:
            self.releaseGuiFunc()


class ScriptRunnable(QtCore.QRunnable):
    def __init__(self, decompile_script, script, origin, destination, update_messagelog, update_finished, raise_exception,
                 remove_input=False):
        super().__init__()
        self.decompile_script = decompile_script
        self.script = script
        self.origin = origin
        self.destination = destination
        self.remove_input = remove_input
        # Signals won't work for some reason unless there's a reference to the
        # functions that the signals are connected to in the runnable
        self.update_messagelog = update_messagelog
        self.update_finished = update_finished
        self.raise_exception = raise_exception
        self.signals = Signals()
        
    @QtCore.pyqtSlot()
    def run(self):
        try:
            self.decompile_script(self.script, self.origin, self.destination, self.remove_input)
            # This should be a signal, but first you'll need to implement a
            # thread-safe messaging queue to prevent this overwriting the
            # error messages from the exception
            self.update_messagelog(self.script)
            self.update_finished()
        except Exception as e:
            self.signals.exception.emit(ScriptHandlerError(e, self.script))


class Signals(QtCore.QObject):
    exception = QtCore.pyqtSignal(Exception)
    update_messagelog = QtCore.pyqtSignal(str)
    update_finished = QtCore.pyqtSignal()


class ScriptHandlerError(Exception):
    pass


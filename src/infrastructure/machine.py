import datetime
import threading

class MachineState(object):
    def __init__(self,xyz = [0.0,0.0,0.0], speed = 1.0):
        self.x, self.y, self.z = xyz
        self.speed = speed

    @property
    def xy(self):
        return [self.x,self.y]

    @property
    def xyz(self):
        return [self.x,self.y, self.z]

    def set_state(self, cordanates, speed):
        self.x, self.y, self.z = cordanates
        self.speed = speed

class MachineError(object):
    def __init__(self,message, layer = None):
        self.timestamp = datetime.datetime.now()
        self.message = message
        self.layer = layer

class MachineStatus(object):
    def __init__(self, status_call_back = None):
        self._status_call_back = status_call_back
        self._current_layer = 0
        self._laser_state = False
        self._waiting_for_drips = True
        self._height = 0.0
        self._model_height = 0.0
        self._errors = []
        self._start_time = datetime.datetime.now()
        self._stop_time = None
        self._complete = False
        self._drips = 0
        self._drips_per_second = 0
        self._drip_history = []
        self._skipped_layers = 0
        self._lock = threading.Lock()

    def _update(self):
        if not self._lock.locked():
            if self._status_call_back:
                self._lock.acquire()
                try:
                    self._status_call_back(self.status())
                finally:
                    self._lock.release()

    def drip_call_back(self, drips, height,drips_per_second,drip_history = []):
        self._height = height
        self._drips = drips
        self._drips_per_second = drips_per_second
        self._drip_history = drip_history
        self._update()

    def add_layer(self):
        self._current_layer += 1
        self._update()

    def skipped_layer(self):
        self._skipped_layers += 1

    def add_error(self, error):
        self._errors.append(error)
        self._update()

    def set_waiting_for_drips(self):
        self._waiting_for_drips = True
        self._update()

    def set_not_waiting_for_drips(self):
        self._waiting_for_drips = False
        self._update()

    def set_model_height(self, model_height):
        self._model_height = model_height
        self._update()

    def set_complete(self):
        self._complete = True
        self._update()

    def _elapsed_time(self):
        return datetime.datetime.now() - self._start_time

    def _status(self):
        if self._complete:
            return 'Complete'
        if (self._drips == 0 and self._current_layer == 0):
            return 'Starting'
        else:
            return 'Running'
    
    def _formatted_errors(self):
        return [ {'time': error.timestamp, 'message' : error.message, 'layer' : error.layer} for error in self._errors ]

    def status(self): 
        return { 
            'start_time' : self._start_time,
            'elapsed_time' : self._elapsed_time(),
            'current_layer' : self._current_layer,
            'status': self._status(),
            'errors' : self._formatted_errors(),
            'waiting_for_drips' : self._waiting_for_drips,
            'height' : self._height,
            'drips' : self._drips,
            'drips_per_second' : self._drips_per_second,
            'model_height' : self._model_height,
            'skipped_layers' : self._skipped_layers,
            'drip_history' : self._drip_history
        }
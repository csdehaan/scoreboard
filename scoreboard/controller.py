
from bluezero import adapter
from bluezero import peripheral
from bluezero import constants
import json

SB_SERVICE_UUID   = 'ff950000-09cc-4150-bf5b-fcc751d720ad'
T1_NAME_UUID      = 'ff950001-09cc-4150-bf5b-fcc751d720ad'
T2_NAME_UUID      = 'ff950002-09cc-4150-bf5b-fcc751d720ad'
SCORE_UUID        = 'ff950003-09cc-4150-bf5b-fcc751d720ad'
STATUS_UUID       = 'ff950004-09cc-4150-bf5b-fcc751d720ad'
ONLINE_UUID       = 'ff950005-09cc-4150-bf5b-fcc751d720ad'
BUTTON_PRESS_UUID = 'ff950010-09cc-4150-bf5b-fcc751d720ad'



class Controller(peripheral.Peripheral):

    def __init__(self, name, button_cb):
        super().__init__(list(adapter.Adapter.available())[0].address, local_name=name)
        self.add_service(srv_id=1, uuid=SB_SERVICE_UUID, primary=True)
        self.add_characteristic(srv_id=1, chr_id=1, uuid=T1_NAME_UUID, value='Team 1'.encode(), notifying=False, flags=['notify','read'], notify_callback=self.notify_cb, read_callback=self.read_t1_name)
        self.add_characteristic(srv_id=1, chr_id=2, uuid=T2_NAME_UUID, value='Team 2'.encode(), notifying=False, flags=['notify','read'], notify_callback=self.notify_cb, read_callback=self.read_t2_name)
        self.add_characteristic(srv_id=1, chr_id=3, uuid=SCORE_UUID, value=[0,0,0], notifying=False, flags=['notify','read'], notify_callback=self.notify_cb, read_callback=self.read_score)
        self.add_characteristic(srv_id=1, chr_id=4, uuid=STATUS_UUID, value=[0], notifying=False, flags=['notify','read'], notify_callback=self.notify_cb, read_callback=self.read_status)
        self.add_characteristic(srv_id=1, chr_id=5, uuid=ONLINE_UUID, value=[1], notifying=False, flags=['read'])
        self.add_characteristic(srv_id=1, chr_id=10, uuid=BUTTON_PRESS_UUID, value=[], notifying=False, flags=['write','write-without-response'], write_callback=button_cb)
        self.chars = {
            T1_NAME_UUID: {'char': None, 'val': 'Team 1'.encode()},
            T2_NAME_UUID: {'char': None, 'val': 'Team 2'.encode()},
            SCORE_UUID: {'char': None, 'val': [0,0,0]},
            STATUS_UUID: {'char': None, 'val': [0]}
        }


    def status(self):
        stat = self.read_status()[0]
        if stat == 1: return 'scoring'
        if stat == 2: return 'waiting'
        if stat == 3: return 'selecting'
        if stat == 4: return 'next_game'
        if stat == 6: return 'no_matches'
        if stat == 11: return 'scoring'
        if stat == 12: return 'waiting'
        return 'undefined'


    def notify_cb(self, notifying, characteristic):
        try:
            if notifying:
                self.chars[characteristic.Get(constants.GATT_CHRC_IFACE, 'UUID')]['char'] = characteristic
            else:
                self.chars[characteristic.Get(constants.GATT_CHRC_IFACE, 'UUID')]['char'] = None
        except KeyError:
            pass


    def read_t1_name(self):
        return self.chars[T1_NAME_UUID]['val']



    def read_t2_name(self):
        return self.chars[T2_NAME_UUID]['val']


    def read_score(self):
        return self.chars[SCORE_UUID]['val']


    def read_status(self):
        return self.chars[STATUS_UUID]['val']


    def set_t1_name(self, name):
        val = name.encode()
        if self.chars[T1_NAME_UUID]['val'] != val:
            self.chars[T1_NAME_UUID]['val'] = val
            if self.chars[T1_NAME_UUID]['char']: self.chars[T1_NAME_UUID]['char'].set_value(val)


    def set_t2_name(self, name):
        val = name.encode()
        if self.chars[T2_NAME_UUID]['val'] != val:
            self.chars[T2_NAME_UUID]['val'] = val
            if self.chars[T2_NAME_UUID]['char']: self.chars[T2_NAME_UUID]['char'].set_value(val)


    def set_score(self, t1_score, t2_score, server):
        val = [t1_score, t2_score, server]
        if self.chars[SCORE_UUID]['val'] != val:
            self.chars[SCORE_UUID]['val'] = val
            if self.chars[SCORE_UUID]['char']: self.chars[SCORE_UUID]['char'].set_value(val)


    def set_status(self, status, selections=[]):
        val = list(selections)
        val.insert(0, status)
        if self.chars[STATUS_UUID]['val'] != val or status == 3:
            self.chars[STATUS_UUID]['val'] = val
            if self.chars[STATUS_UUID]['char']: self.chars[STATUS_UUID]['char'].set_value(val)


    def set_status_scoring(self, online=True):
        if online: self.set_status(1)
        else: self.set_status(11)


    def set_status_waiting(self, online=True):
        if online: self.set_status(2)
        else: self.set_status(12)


    def set_status_selecting(self, matches={'names': ['No Matches Scheduled\t'], 'ids': [0]}):
        self.set_status(3, json.dumps(matches).encode())


    def set_status_next_game(self):
        self.set_status(4)


    def set_status_serve_order(self, serve_order):
        self.set_status(5, json.dumps({'players': serve_order}).encode())


    def set_status_no_matches(self):
        self.set_status(6)


    def send_config(self, config_json):
        self.set_status(20, config_json.encode())

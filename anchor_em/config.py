import os

from db import objects as db_objects, DefaultConfigModel
from decawave import AnchorConfigurationFrame, CPPRXFrame, CPPTXFrame, BlinkFrame

ANCHOR_SOURCE_FILE_PATH = os.environ.get('ANCHOR_SOURCE_FILE_PATH', "source.log")
ANCHOR_STATE_IDLE = 0
ANCHOR_STATE_CONFIGURED = 1
ANCHOR_STATE_WORKING = 2
ANCHOR_STATE = (
    (ANCHOR_STATE_IDLE, "idle"),
    (ANCHOR_STATE_CONFIGURED, "configured"),
    (ANCHOR_STATE_WORKING, "working"),
)

# get anchor default config from database
with db_objects.allow_sync():
    default_db_config = DefaultConfigModel.select()[DefaultConfigModel.select().count() - 1]

anchor_config = AnchorConfigurationFrame()
anchor_config.chan = default_db_config.chan or 0
anchor_config.prf = default_db_config.prf or 1
anchor_config.txPreambLength = default_db_config.txPreambLength or 24
anchor_config.rxPAC = default_db_config.rxPAC or 3
anchor_config.txCode = default_db_config.txCode or 8
anchor_config.rxCode = default_db_config.rxCode or 8
anchor_config.nsSFD = default_db_config.nsSFD or 0
anchor_config.dataRate = default_db_config.dataRate or 2
anchor_config.phrMode = default_db_config.phrMode or 3
anchor_config.sfdTO = default_db_config.sfdTO or 1058
anchor_config.my_master_ID = default_db_config.my_master_ID or 66666655198446766421
anchor_config.role = default_db_config.role or 1
anchor_config.master_period = default_db_config.master_period or 7777
anchor_config.submaster_delay = default_db_config.submaster_delay or 253


class AnchorConfig:
    def __init__(self, default_config):
        self.ID = os.environ.get('ANCHOR_ID', None)
        if not self.ID:
            raise SystemExit("Configure ANCHOR_ID!!!")
        self.state = ANCHOR_STATE_IDLE
        self.anchor_config = default_config
        self.frame_queue = []
        self.load_data_from_file()

    def load_data_from_file(self):
        f = open(ANCHOR_SOURCE_FILE_PATH, "r")
        for line in f.readlines():
            # print(line)
            if "CS_TX" in line:
                if "M %s" % self.ID in line:
                    frame = CPPTXFrame()
                    values = line.split()
                    frame.seq_n = int(values[4])
                    frame.clock_sync_tx_time = bytes(str(float(values[6])), "utf-8")
                    self.frame_queue.append(frame)
            if "CS_RX" in line:
                if "A %s" % self.ID in line:
                    frame = CPPRXFrame()
                    values = line.split()
                    frame.seq_n = int(values[4])
                    frame.master_anchor_addr = self.anchor_config.my_master_ID
                    frame.clock_sync_rx_time = bytes(str(float(values[6])), "utf-8")
                    frame.fp = int(values[7].replace("FP:", ""))
                    self.frame_queue.append(frame)
            if "BLINK" in line:
                if "A %s" % self.ID in line:
                    frame = BlinkFrame()
                    values = line.split()
                    frame.tag_address = bytes(values[2], "utf-8")
                    frame.seq_n = int(values[3])
                    frame.blink_rx_time = bytes(str(float(values[8])), "utf-8")
                    frame.fp = int(values[10])
                    self.frame_queue.append(frame)

    def set_state(self, state):
        self.state = state

    def set_anchor_config(self, config_frame):
        self.anchor_config = config_frame

    def get_anchor_config(self):
        return self.anchor_config

    def get_data(self):
        for frame in self.frame_queue:
            yield frame


config = AnchorConfig(anchor_config)

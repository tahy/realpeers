import os

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


default_anchor_configuration = AnchorConfigurationFrame()
default_anchor_configuration.chan = 0
default_anchor_configuration.prf = 1
default_anchor_configuration.txPreambLength = 24
default_anchor_configuration.rxPAC = 3
default_anchor_configuration.txCode = 8
default_anchor_configuration.rxCode = 8
default_anchor_configuration.nsSFD = 0
default_anchor_configuration.dataRate = 2
default_anchor_configuration.phrMode = 3
default_anchor_configuration.sfdTO = 1058
default_anchor_configuration.my_master_ID = 66666655198446766421
default_anchor_configuration.role = 1
default_anchor_configuration.master_period = 7777
default_anchor_configuration.submaster_delay = 253


class AnchorConfig:
    def __init__(self):
        self.ID = os.environ.get('ANCHOR_ID', None)
        if not self.ID:
            raise SystemExit("Configure ANCHOR_ID!!!")
        self.state = ANCHOR_STATE_IDLE
        self.anchor_config = default_anchor_configuration
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

        # print(len(self.message_queue))

    def set_state(self, state):
        self.state = state

    def set_anchor_config(self, config_frame):
        self.anchor_config = config_frame

    def get_anchor_config(self):
        return self.anchor_config

    def get_data(self):
        for frame in self.frame_queue:
            yield frame


config = AnchorConfig()

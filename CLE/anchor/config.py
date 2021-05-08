import os

from CLE.config import ANCHOR_STATE_IDLE
from CLE.ds.decawave import AnchorConfigurationFrame, CPPRXFrame, CPPTXFrame, BlinkFrame

ANCHOR_SOURCE_FILE_PATH = os.environ.get('CLE_ANCHOR_SOURCE_FILE', "source.log")


anchor_config = AnchorConfigurationFrame()
anchor_config.chan = 0
anchor_config.prf = 1
anchor_config.txPreambLength = 24
anchor_config.rxPAC = 3
anchor_config.txCode = 8
anchor_config.rxCode = 8
anchor_config.nsSFD = 0
anchor_config.dataRate = 2
anchor_config.phrMode = 3
anchor_config.sfdTO = 1058
anchor_config.my_master_ID = 6666665519844
anchor_config.role = 1
anchor_config.master_period = 7777
anchor_config.submaster_delay = 253


class AnchorConfig:
    def __init__(self, default_config):
        self.ID = os.environ.get('CLE_ANCHOR_ID', None)
        self.state = ANCHOR_STATE_IDLE
        self.source_file = ANCHOR_SOURCE_FILE_PATH
        self.anchor_config = default_config
        self.frame_queue = []
        if self.ID:
            self.load_data_from_file()

    def load_data_from_file(self):
        """
        Загрузка данных из файла логов в очередь сообщений
        """
        f = open(self.source_file, "r")
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

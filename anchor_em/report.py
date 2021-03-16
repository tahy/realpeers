from config import config
from decawave import Frame, AnchorConfigurationFrame, OkFrame, AnchorStateFrame, normalise_value


class Report:
    frame_class = None
    frame_data = None
    frame = None

    def __init__(self, payload=None):
        self.payload = payload

    def render_frame(self):
        self.frame = self.frame_class(self.get_frame_data())
        self.process()
        return self.frame.to_binary()

    def process(self):
        pass

    def get_frame_data(self):
        return self.frame_data


class ConfigGetReport(Report):
    frame_class = AnchorConfigurationFrame

    def get_frame_data(self):
        return config.get_anchor_config().to_binary()


class ConfigPutReport(Report):
    frame_class = OkFrame
    frame_data = bytes([1])

    def process(self):
        config_frame = AnchorConfigurationFrame(self.payload)
        config.set_anchor_config(config_frame)


class StateGetReport(Report):
    frame_class = AnchorStateFrame

    def get_frame_data(self):
        return normalise_value(config.state, 1)


class StatePutReport(Report):
    frame_class = OkFrame

    def process(self):
        state_frame = AnchorStateFrame(self.payload)
        config.set_state(state_frame.state_dec)


class PopQueueGetReport(Report):
    def render_frame(self):
        return next(config.get_data()).to_binary()

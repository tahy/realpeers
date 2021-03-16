from decawave import AnchorConfigurationFrame


class Report:
    frame_class = None

    def __init__(self):
        self.frame = self.frame_class()
        # find report in logs

    def render_frame(self):
        return self.frame.to_binary()


class ConfigGetReport(Report):
    frame_class = AnchorConfigurationFrame


class ConfigPutReport(Report):
    frame_class = AnchorConfigurationFrame


class StateGetReport(Report):
    frame_class = AnchorConfigurationFrame


class StatePutReport(Report):
    frame_class = AnchorConfigurationFrame


class PopQueueGetReport(Report):
    frame_class = AnchorConfigurationFrame

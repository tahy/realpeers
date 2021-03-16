from collections import OrderedDict
from copy import deepcopy


class Frame(type):
    """Метакласс для фреймов инициализирует список полей и
    преобразования из, в байты
    Использование:

    Описание фрейма
    FrameName(metaclass=Frame):
        field_name = <default value>, <length bytes>

    если длина = 0, то берется длина по факту,
    допустимо только для последнего поля во фрейме

    Можно инициализировать по строке байтов
    frame = FrameName(b"binary_frame")

    Обращение к полям:
    frame.fn_ce - значение в виде строки байтов
    frame.fn_ce_hex - значение в виде хекса
    frame.fn_ce_dec - в виде инта
    frame.fn_ce_raw - кортеж (значение, длина в байтах)

    Запись в поле:
    frame.fn_ce = value value должно иметь тип int или bytes (b"")
    внутреннее представление всегда bytes, поэтому int будет к нему преобразован

    методы:
    to_binary() - значение фрейма в байтах
    from_binary(bin_frame) - переписать значения полей из строки байтов

    попытка записать отсутствующее в декларации класса поле рейзит AttributeError
    """

    def init(self, bin_frame=None):
        self.__dict__["fields"] = deepcopy(self.fields)
        if bin_frame:
            self.from_binary(bin_frame)

    def getattr(self, name):
        try:
            if name[-4:] == "_hex":
                return self.fields[name[:-4]][0].hex()

            if name[-4:] == "_dec":
                return int("0x" + str(self.fields[name[:-4]][0].hex()), 0)

            if name[-4:] == "_raw":
                return self.fields[name[:-4]]

            return self.fields[name][0]
        except KeyError:
            raise AttributeError("Unknown attribute \"%s\" " % name)

    def setattr(self, key, value):
        if key not in self.fields.keys():
            raise AttributeError("Unknown attribute \"%s\" " % key)
        if isinstance(value, tuple):
            self.fields[key] = value
        else:
            value = Frame.normalise_value(value, self.fields[key][1])
            self.fields[key] = value, self.fields[key][1]

    @staticmethod
    def normalise_value(value, length):
        if isinstance(value, int):
            value = value.to_bytes(length, byteorder='little', signed=False)

        if length == 0:
            return value

        if len(value) > length:
            return value[:length]

        while len(value) < length:
            value = b"\x00" + value

        return value

    def from_binary(self, bin_frame):
        for key, value in self.fields.items():
            if value[1] == 0:
                part = bin_frame
            else:
                part = bin_frame[:value[1]]
                bin_frame = bin_frame[value[1]:]

            setattr(self, key, (part, value[1]))

    def to_binary(self):
        result = b""
        for val in self.fields.values():
            result += Frame.normalise_value(val[0], val[1])
        return result

    def __new__(mcs, classname, bases, attrs):
        fields = OrderedDict()
        for name, val in attrs.items():
            if not name.startswith('__'):
                fields[name] = Frame.normalise_value(val[0], val[1]), val[1]

        for name in fields.keys():
            attrs.pop(name)

        attrs["fields"] = fields
        attrs["__init__"] = mcs.init
        attrs["__getattr__"] = mcs.getattr
        attrs["__setattr__"] = mcs.setattr
        attrs["to_binary"] = mcs.to_binary
        attrs["from_binary"] = mcs.from_binary
        return super(Frame, mcs).__new__(mcs, classname, bases, attrs)


class CPPUWBFrame(metaclass=Frame):
    frame_ctrl = 0x41c8, 2           # FrameCtrl
    seq_n = b"\x00", 1               # Seq#
    pan_id = 0xDECA, 2               # PANID
    dest_addr = 0xFFFF, 2            # Dest Addr
    src_addr = b"4", 8               # Src Addr
    fn_cd = 0x2C, 1                  # FnCd
    crc = b"6", 2                    # CRC


class CPPRXReportFrame(metaclass=Frame):
    fn_ce = 0x31, 1                      # Function code
    master_anchor_addr = b"", 8          # Master Anchor Address
    seq_n = b"", 1                       # Seq#
    clock_sync_rx_time = b"", 5          # Clock Sync Rx Time
    fp = b"", 2                          # FP First Path raw index of the received CCP frame.
    el = b"", 1                          # EL Length of variable payload field
    payload = b"", 0                     # Payload


class CPPTXReportFrame(metaclass=Frame):
    fn_ce = 0x30, 1                       # Function code
    seq_n = b"", 1                        # Seq#
    clock_sync_tx_time = b"", 5           # Clock Sync Rx Time
    el = b"", 1                           # EL Length of variable payload field
    payload = b"", 0                      # Payload


class BlinkFrame(metaclass=Frame):
    fc = 0xC5, 1                # FC 1 byte frame control
    seq_n = b"", 1              # Seq#
    tag_address = b"", 8        # Tag Address
    crc = b"", 2                # CRC


class BlinkReportFrame(metaclass=Frame):
    fn_ce = 0x32, 1                  # Function code
    tag_address = b"", 8             # Tag Address
    seq_n = b"", 1                   # Seq#
    blink_rx_time = b"", 5           # 40-bit Blink frame received timestamp.
    fp = b"", 2                      # FP First Path raw index of the received CCP frame.
    el = b"", 1                      # EL Length of variable payload field
    payload = b"", 0                 # Payload


class DiagnosticPartFrame(metaclass=Frame):
    log_number = b"\00", 4      # 4 byte log number. It increments for each report sent.
    diagnostics = b"", 0        # Diagnostic data


class RequestConfFrame(metaclass=Frame):
    fn_ce = 0x42, 1             # Function code
    anchor_address = b"", 8     # 64-bit unique Anchor Identifier
    version = b"", 1            # version


class CommunicationTestStartRequestFrame(metaclass=Frame):
    fn_ce = 0x32, 1                # Function code
    tax_rx = 0, 1                  # 1 – Transmitter, 0 – Receiver
    tx_frames = b"", 2             # Number of Frames to Transmitted, 1 to 65535


class CommunicationTestDoneIndicationFrame(metaclass=Frame):
    done = 0x81, 1                 # RTLS_COMM_TEST_DONE_IND


class CommunicationTestResultRequestFrame(metaclass=Frame):
    result = 0x54, 1              # RTLS_COMM_TEST_RESULT_REQ


class CommunicationTestResultFrame(metaclass=Frame):
    fn_ce = 0x82, 1               # Function code
    rx_data = b"", 2              # 2 bytes - Number of Data Frames Received.
    rx_others = b"", 2            # 2 bytes - Number of Other Frames Received.


# class AnchorConfigurationFrame(metaclass=Frame):
#     fn_ce = 0x44, 1          # Function code
#     a_n = b"", 1             # Not used (obsolete).
#     m = b"", 1               # RTLS Role
#     cp = b"", 1              # UWB Channel Number (Lower Nibble)
#     dr = b"", 1              # Data Rate
#     pc = b"", 1              # Preamble Code: 1-15
#     pl = b"", 1              # Preamble Len
#     psn = b"", 1             # PAC Size (Preamble Acquisition Chunk)
#     adrx = b"", 2            # 16 bit anchor’s RX antenna delay
#     adtx = b"", 2            # 16 bit anchor’s TX antenna delay
#     reserved = 0, 1          # 0 (must be set to 0)
#     ld = 0, 1                # 0, 1 - disable, enable sending of diagnostic information
#     primary_master = b"", 8  #
#     lag = b"", 4             # Secondary Master’s CCP frame Tx delay


class AnchorConfigurationFrame(metaclass=Frame):
    chan = 3, 1
    prf = 1, 1
    txPreambLength = 24, 1
    rxPAC = 3, 1
    txCode = 8, 1
    rxCode = 8, 1
    nsSFD = 0, 1
    dataRate = 2, 1
    phrMode = 3, 1
    sfdTO = 1058, 2
    my_master_ID = 13758255198446766421, 16
    role = 1, 1
    master_period = 7777, 2
    submaster_delay = 253, 1

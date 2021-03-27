import json

from collections import OrderedDict
from copy import deepcopy


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


class FrameMeta(type):
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

    def __new__(mcs, classname, bases, attrs):
        fields = OrderedDict()
        for name, value in attrs.items():
            if not name.startswith('__') and name not in ("from_binary", "to_binary", "to_json"):
                fields[name] = normalise_value(value[0], value[1]), value[1]

        for name in fields.keys():
            attrs.pop(name)

        attrs["fields"] = fields
        return super().__new__(mcs, classname, bases, attrs)


class Frame(metaclass=FrameMeta):

    def __init__(self, bin_frame=None):
        self.__dict__["fields"] = deepcopy(self.fields)
        if bin_frame:
            self.from_binary(bin_frame)

    def __str__(self):
        result = "%s object \n" % self.__class__.__name__
        result += "====================================================\n"
        for name in self.fields.keys():
            result += "%s: %s\n" % (name, getattr(self, name))
        return result

    def __getattr__(self, name):
        try:
            if name[-4:] == "_hex":
                return self.fields[name[:-4]][0].hex()

            if name[-4:] == "_dec":
                return int.from_bytes(self.fields[name[:-4]][0],
                                      byteorder='little', signed=False)

            if name[-4:] == "_raw":
                return self.fields[name[:-4]]

            return self.fields[name][0]
        except KeyError:
            raise AttributeError("Unknown attribute \"%s\" " % name)

    def __setattr__(self, key, value):
        if key not in self.fields.keys():
            raise AttributeError("Unknown attribute \"%s\" " % key)
        if isinstance(value, tuple):
            self.fields[key] = value
        else:
            value = normalise_value(value, self.fields[key][1])
            self.fields[key] = value, self.fields[key][1]

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
            result += normalise_value(val[0], val[1])
        return result

    def to_json(self):
        result = {"frame_type": self.__class__.__name__}
        for name in self.fields.keys():
            result[name] = getattr(self, name + "_hex")
        return json.dumps(result)


class CPPRXFrame(Frame):
    fn_ce = 0x31, 1                      # Function code
    master_anchor_addr = b"", 8          # Master Anchor Address
    seq_n = b"", 1                       # Seq#
    clock_sync_rx_time = b"", 5          # Clock Sync Rx Time
    fp = b"", 2                          # FP First Path raw index of the received CCP frame.
    el = b"", 1                          # EL Length of variable payload field
    payload = b"", 0                     # Payload


class CPPTXFrame(Frame):
    fn_ce = 0x30, 1                       # Function code
    seq_n = b"", 1                        # Seq#
    clock_sync_tx_time = b"", 5           # Clock Sync Rx Time
    el = b"", 1                           # EL Length of variable payload field
    payload = b"", 0                      # Payload


class BlinkFrame(Frame):
    fn_ce = 0x32, 1                  # Function code
    tag_address = b"", 8             # Tag Address
    seq_n = b"", 1                   # Seq#
    blink_rx_time = b"", 5           # 40-bit Blink frame received timestamp.
    fp = b"", 2                      # FP First Path raw index of the received CCP frame.
    el = b"", 1                      # EL Length of variable payload field
    payload = b"", 0                 # Payload


class AnchorConfigurationFrame(Frame):
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


class OkFrame(Frame):
    ok = 1, 1


class AnchorStateFrame(Frame):
    state = 0, 1          # состояние якоря

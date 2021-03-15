BYTE_ORDER_DEF = 'little'

RTLS_INIT_REQ_LEN_VALUE = 1
RTLS_CMD_SET_CFG_CCP_LEN_VALUE = 26
RTLS_POWER_TEST_START_LEN_VALUE = 4
RTLS_COMM_TEST_START_LEN_VALUE = 4
RTLS_COMM_TEST_RESULT_REQ_LEN_VALUE = 1
RTLS_RANGE_MEAS_REQ_LEN_VALUE = 21
RTLS_ASYMM_TWR_MODE_REQ_LEN_VALUE = 27
RTLS_SINGLE_TWR_MODE_REQ_LEN_VALUE = 17
RTLS_START_REQ_LEN_VALUE = 2
RTLS_LOG_ACC_REQ_LEN_VALUE = 4
RTLS_RESET_REQ_LEN_VALUE = 18

cle_message_len_dict = {
    'RTLS_INIT_REQ_LEN': RTLS_INIT_REQ_LEN_VALUE.to_bytes(1, byteorder=BYTE_ORDER_DEF, signed=False).hex(),
    'RTLS_CMD_SET_CFG_CCP_LEN': RTLS_CMD_SET_CFG_CCP_LEN_VALUE.to_bytes(1, byteorder=BYTE_ORDER_DEF,
                                                                        signed=False).hex(),
    'RTLS_POWER_TEST_START_LEN': RTLS_POWER_TEST_START_LEN_VALUE.to_bytes(1, byteorder=BYTE_ORDER_DEF,
                                                                          signed=False).hex(),
    'RTLS_COMM_TEST_START_LEN': RTLS_COMM_TEST_START_LEN_VALUE.to_bytes(1, byteorder=BYTE_ORDER_DEF,
                                                                        signed=False).hex(),
    'RTLS_COMM_TEST_RESULT_REQ_LEN': RTLS_COMM_TEST_RESULT_REQ_LEN_VALUE.to_bytes(1, byteorder=BYTE_ORDER_DEF,
                                                                                  signed=False),
    'RTLS_RANGE_MEAS_REQ_LEN': RTLS_RANGE_MEAS_REQ_LEN_VALUE.to_bytes(1, byteorder=BYTE_ORDER_DEF, signed=False).hex(),
    'RTLS_ASYMM_TWR_MODE_REQ_LEN': RTLS_ASYMM_TWR_MODE_REQ_LEN_VALUE.to_bytes(1, byteorder=BYTE_ORDER_DEF,
                                                                              signed=False).hex(),
    'RTLS_SINGLE_TWR_MODE_REQ_LEN': RTLS_SINGLE_TWR_MODE_REQ_LEN_VALUE.to_bytes(1, byteorder=BYTE_ORDER_DEF,
                                                                                signed=False).hex(),
    'RTLS_START_REQ_LEN': RTLS_START_REQ_LEN_VALUE.to_bytes(1, byteorder=BYTE_ORDER_DEF, signed=False).hex(),
    'RTLS_LOG_ACC_REQ_LEN': RTLS_LOG_ACC_REQ_LEN_VALUE.to_bytes(1, byteorder=BYTE_ORDER_DEF, signed=False).hex(),
    'RTLS_RESET_REQ_LEN': RTLS_RESET_REQ_LEN_VALUE.to_bytes(1, byteorder=BYTE_ORDER_DEF, signed=False).hex()}

RTLS_INIT_REQ_VALUE = 0x56
RTLS_CMD_SET_CFG_CCP_VALUE = 0x44
RTLS_POWER_TEST_START_REQ_VALUE = 0x58
RTLS_COMM_TEST_START_REQ_VALUE = 0x53
RTLS_COMM_TEST_RESULT_REQ_VALUE = 0x54
RTLS_RANGE_MEAS_REQ_VALUE = 0x55
RTLS_ASYMM_TWR_MODE_REQ_VALUE = 0x58
RTLS_SINGLE_TWR_MODE_REQ_VALUE = 0x5A
RTLS_START_REQ_VALUE = 0x57
RTLS_LOG_ACCUMULATOR_REQ_VALUE = 0x88
RTLS_RESET_REQ_VALUE = 0x59


class Message:
    def __init__(self, data):
        function_code = (data[0])
        if function_code == 49:  # 0x31
            self.type = "CS_RX"
            self.state = 1
            data1 = data[2:10]
            ID = ""
            for i in reversed(data1):
                a = str(hex(i))
                ID += a[2:]
            if len(ID) < 15:
                ID += '0'
            self.tx_ID = ID
            self.rx_ID = ""
            self.seq = data[1]
            self.TimeStamp = int.from_bytes(data[10:15],
                                            byteorder=BYTE_ORDER_DEF, signed=False) * (1.0 / 499.2e6 / 128.0)
            self.FP = int.from_bytes(data[15:17], byteorder=BYTE_ORDER_DEF, signed=False)
        elif function_code == 50:  # 0x32
            self.type = "BLINK"
            self.state = 1
            data1 = data[2:10]
            ID = ""
            for i in reversed(data1):
                a = str(hex(i))
                ID += a[2:]
            if len(ID) < 14:
                ID += '0'
            self.tx_ID = ID
            self.rx_ID = ""
            self.SN = data[1]
            self.TimeStamp = int.from_bytes(data[10:15],
                                            byteorder=BYTE_ORDER_DEF, signed=False) * (1.0 / 499.2e6 / 128.0)
            self.FP = int.from_bytes(data[15:17], byteorder=BYTE_ORDER_DEF, signed=False)
            self.number = 0
        elif function_code == 48:  # 0x30
            self.type = "CS_TX"
            self.state = 1
            self.tx_ID = ""
            self.rx_ID = ""
            self.seq = data[1]
            self.TimeStamp = int.from_bytes(data[2:7],
                                            byteorder=BYTE_ORDER_DEF, signed=False) * (1.0 / 499.2e6 / 128.0)
            self.FP = data[7]
        elif function_code == 66:  # 0x42
            self.type = "Config request"
            self.state = 1
            data = data[1:9]
            ID = ""
            for i in reversed(data):
                a = str(hex(i))
                ID += a[2:]
            if len(ID) < 15:
                ID += '0'
            self.tx_ID = ID
            self.rx_ID = ID
            self.seq = 0
            self.TimeStamp = 0
            self.FP = 0
            self.i = 0
        elif function_code == 130:  # 0x82
            self.type = "COMM_TEST_RESULT_IND"
            self.state = 0
            self.tx_ID = "0"
            self.rx_ID = "0"
            self.seq = 0
            self.Rx = 0
            self.FP = int.from_bytes(data[4:6], byteorder=BYTE_ORDER_DEF, signed=False)
        else:
            self.type = "Unknown"
            self.state = 0
            self.tx_ID = "0"
            self.rx_ID = "0"
            self.seq = 0
            self.Rx = 0
            self.FP = 0

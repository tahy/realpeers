from datetime import datetime

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

# You can generate a Token from the "Tokens Tab" in the UI
token = "9Frq6PFFW7BkE4y_ndYes7_9wh1-YZnBIDVuPF6gAX2wdltXqPfWYWTJMYTlS84g5TJ-DAr1hZOS6RPG0AfmIQ=="
org = "realpeers"
bucket = "cle"

client = InfluxDBClient(url="http://influxdb:8086", token=token)
write_api = client.write_api(write_options=SYNCHRONOUS)

# data = "mem,host=host2 used_percent=23.43234543"
# write_api.write(bucket, org, data)
#
# point = Point("mem") \
#   .tag("host", "host1") \
#   .field("used_percent", 123123.54) \
#   .time(datetime.utcnow(), WritePrecision.NS)
#
#
# write_api.write(bucket, org, point)


def publish(parameters):
    data = "anchors,anchor_id=%s," % parameters["anchor_id"]   #used_percent=23.43234543"
    for k, v in parameters.items():
        if k not in ("anchor_id", "solver"):
            data += k + "=" + (v or "0") + ","
    data = data[:-1] + " " + "solver_x=%d," % parameters["solver"][0] \
                           + "solver_y=%d," % parameters["solver"][1] \
                           + "solver_z=%d" % parameters["solver"][2]
    write_api.write(bucket, org, data)
    print("Published to influxdb")
    print(data)

# query = f'from(bucket: "{bucket}") |> range(start: -1m)'
# tables = client.query_api().query(query, org=org)
# print(tables)

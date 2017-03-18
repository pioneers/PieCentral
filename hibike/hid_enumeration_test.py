import threading
import hibike_message as hm
from hid import HIDWrapper as hid

# get all available hid devices
devices = hid.open_all()

def print_uid(i, device):
    for packet in hm.hid_blocking_read_generator(device):
        if packet.getmessageID() == hm.messageTypes["SubscriptionResponse"]:
            params, delay, uid = hm.parse_subscription_response(packet)
            print("thread %d enumerated %s with uid %d" % (i, hm.uid_to_device_name(uid), uid))
            return

# start up a read thread for each device
read_threads = [threading.Thread(target=print_uid, args=(i, device)) for (i, device) in enumerate(devices)]

for read_thread in read_threads:
    read_thread.start()

# ping each device
for device in devices:
    hm.hid_send(device, hm.make_ping())

# wait until each thread enumerates its device and exits
for read_thread in read_threads:
    read_thread.join()

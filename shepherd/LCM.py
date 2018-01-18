import threading
import lcm

def lcm_start_read(receive_channel, queue):
    '''
    Takes in receiving channel name (string), queue (Python queue object).
    Creates thread that receives any message to receiving channel and adds
    it to queue as tuple (header, [*args]).
    header: string
    [*args]: variable length containing ints/strings. If no args, empty list.
    '''
    comm = lcm.LCM()

    def string_to_int(string):
        try:
            return int(string)
        except ValueError:
            return string

    def handler(_, item):
        msg = item.decode()
        msg_list = msg.split('|||')
        queue.put((msg_list[0], [string_to_int(x) for x in msg_list[1:]]))

    comm.subscribe(receive_channel, handler)

    def run():
        while True:
            comm.handle()

    rec_thread = threading.Thread()
    rec_thread.run = run
    rec_thread.start()

def lcm_send(target_channel, header, *args):
    '''
    Send header (string) and variable number of arguments (string or int) to target channel (string)
    '''
    msg = '|||'.join(str(a) for a in args)
    if msg:
        msg = '|||'.join([header, msg])
    else:
        msg = header
    lcm.LCM().publish(target_channel, msg.encode())

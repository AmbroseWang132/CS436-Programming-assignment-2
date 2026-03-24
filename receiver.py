#!/usr/bin/env python3
import sys
import socket
from packet import Packet


def write_log_line(fp, value: int):
    fp.write(f"{value}\n")
    fp.flush()


def main():
    if len(sys.argv) != 5:
        print(
            "Usage: receiver <emulator_host> <emu_port> <receiver_port> <output_file>",
            file=sys.stderr,
        )
        sys.exit(1)

    emulator_host = sys.argv[1]
    emu_port = int(sys.argv[2])
    receiver_port = int(sys.argv[3])
    output_file = sys.argv[4]

    received_data = {}
    seen_seqnums = set()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("", receiver_port))

    with open("arrival.log", "w", encoding="ascii") as arrival_log:
        while True:
            raw_data, _ = sock.recvfrom(1024)
            pkt = Packet(raw_data)
            typ, seqnum, length, data = pkt.decode()

            if typ == 1:
                write_log_line(arrival_log, seqnum)

                # ACK every received data packet, including duplicates
                ack_pkt = Packet(0, seqnum, 0, "")
                sock.sendto(ack_pkt.encode(), (emulator_host, emu_port))

                # Discard duplicate, otherwise buffer it
                if seqnum not in seen_seqnums:
                    seen_seqnums.add(seqnum)
                    received_data[seqnum] = data

            elif typ == 2:
                # Sender EOT received:
                # send EOT back, write buffered data in order, then exit
                eot_pkt = Packet(2, seqnum, 0, "")
                sock.sendto(eot_pkt.encode(), (emulator_host, emu_port))

                ordered_seqnums = sorted(received_data.keys())
                with open(output_file, "w", encoding="ascii") as f:
                    for s in ordered_seqnums:
                        f.write(received_data[s])

                break

    sock.close()


if __name__ == "__main__":
    main()
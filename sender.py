#!/usr/bin/env python3
import sys
import socket
from packet import Packet


MAX_DATA_LEN = 500


def chunk_file(filename: str):
    with open(filename, "r", encoding="ascii") as f:
        content = f.read()

    chunks = []
    for i in range(0, len(content), MAX_DATA_LEN):
        chunks.append(content[i:i + MAX_DATA_LEN])
    return chunks


def write_log_line(fp, value: int):
    fp.write(f"{value}\n")
    fp.flush()


def main():
    if len(sys.argv) != 6:
        print(
            "Usage: sender <emulator_host> <emu_port> <sender_port> <timeout_ms> <input_file>",
            file=sys.stderr,
        )
        sys.exit(1)

    emulator_host = sys.argv[1]
    emu_port = int(sys.argv[2])
    sender_port = int(sys.argv[3])
    timeout_ms = int(sys.argv[4])
    input_file = sys.argv[5]

    timeout_sec = timeout_ms / 1000.0

    chunks = chunk_file(input_file)

    packets = {}
    acked = set()

    for seqnum, data in enumerate(chunks):
        packets[seqnum] = Packet(1, seqnum, len(data), data)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("", sender_port))
    sock.settimeout(timeout_sec)

    with open("seqnum.log", "w", encoding="ascii") as seq_log, \
         open("ack.log", "w", encoding="ascii") as ack_log:

        # Send all data packets once initially
        for seqnum in sorted(packets.keys()):
            sock.sendto(packets[seqnum].encode(), (emulator_host, emu_port))
            write_log_line(seq_log, seqnum)

        # Keep receiving ACKs; on timeout resend all unACKed packets
        while len(acked) < len(packets):
            try:
                raw_data, _ = sock.recvfrom(1024)
                pkt = Packet(raw_data)
                typ, seqnum, _, _ = pkt.decode()

                if typ == 0:
                    write_log_line(ack_log, seqnum)
                    acked.add(seqnum)
                elif typ == 2:
                    # Should not happen before all data are ACKed, but ignore safely
                    pass

            except socket.timeout:
                for seqnum in sorted(packets.keys()):
                    if seqnum not in acked:
                        sock.sendto(packets[seqnum].encode(), (emulator_host, emu_port))
                        write_log_line(seq_log, seqnum)

        # Send EOT after all data packets are ACKed
        eot_pkt = Packet(2, 0, 0, "")
        sock.sendto(eot_pkt.encode(), (emulator_host, emu_port))

        # Wait for receiver EOT
        while True:
            raw_data, _ = sock.recvfrom(1024)
            pkt = Packet(raw_data)
            typ, _, _, _ = pkt.decode()
            if typ == 2:
                break

    sock.close()


if __name__ == "__main__":
    main()
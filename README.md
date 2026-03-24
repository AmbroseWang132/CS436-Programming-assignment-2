# CS 436 – Assignment 2

Reliable Data Transfer Protocol
Author: Ambrose Wang
Quest ID: 20894753

---

## 1. Environment

This program was developed and tested on the University of Waterloo CS undergrad environment using:

* ubuntu2404-002 (Sender)
* ubuntu2404-004 (Network Emulator)
* ubuntu2404-006 (Receiver)

Corresponding IP addresses:

* Sender (Host1): 129.97.167.158
* Emulator (Host2): 129.97.167.171
* Receiver (Host3): 129.97.167.172


---

## 2. Files Included

* sender.py
* receiver.py
* packet.py
* network_emulator.py
* README.md

**input.txt is required** for the sender program and must be present on the sender machine.

---

## 3. How to Run

Programs must be started in the correct order on three different machines.

---

### Step 1: Start Network Emulator (Host2 – ubuntu2404-004)

```bash
python3 network_emulator.py \
9991 \
129.97.167.172 \   # Receiver (Host3)
9994 \
9993 \
129.97.167.158 \   # Sender (Host1)
9992 \
100 \
0.2 \
1
```

---


### Step 2: Start Receiver (Host3 – ubuntu2404-006)

```bash
python3 receiver.py \
129.97.167.171 \   # Emulator (Host2)
9993 \              # emulator backward port (receives ACKs from receiver)
9994 \              # receiver listening port
output.txt          # output file
```

---

### Step 3: Start Sender (Host1 – ubuntu2404-002)

```bash
python3 sender.py \
129.97.167.171 \   # Emulator (Host2)
9991 \              # emulator forward port (receives data from sender)
9992 \              # sender listening port (for ACKs)
50 \                # timeout in milliseconds
input.txt           # input file (must exist on sender)
```

---

## 4. Output Files

### Sender (Host1)

* seqnum.log → sequence numbers of sent packets
* ack.log → ACKs received

### Receiver (Host3)

* arrival.log → received packet sequence numbers
* output.txt → reconstructed file

---

## 5. Notes

* The protocol implements reliable data transfer over an unreliable network emulator.
* Packet loss, delay, and duplication are handled using retransmission and acknowledgements.
* All packets are at most 500 bytes as required.
* The sender retransmits all unacknowledged packets upon timeout.
* The receiver buffers out-of-order packets and discards duplicates.
* End-of-transmission (EOT) packets are used to terminate communication.

---

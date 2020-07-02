# Name:    Cris Shumack
# Project: Reliable Data Transfer


from unreliable import *

class RDTLayer(object):
    # The length of the string data that will be sent per packet...
    DATA_LENGTH = 4 # characters
    # Receive window size for flow-control
    FLOW_CONTROL_WIN_SIZE = 15 # characters

    # Add class members as needed...
    def __init__(self):
        self.sendChannel = None
        self.receiveChannel = None
        self.dataToSend = ''
        self.currentIteration = 0 # <--- Use this for segment 'timeouts'
        # String that contains the current data received
        self.dataReceived = ''
        # Used to keep track of the first char in the current data segment to be sent.
        self.fromIndex = 0
        # Used to keep track of the last char in the current data segment to be sent.
        self.toIndex = 4
        # Used to assign sequence numbers to segments. Increments by RDTLayer.DATA_LENGTH.
        self.seqnum = 0
        # Keeps track of all ack numbers received
        self.acksReceived = list()
        # Holds the number of the expected next segment's seqnum (used for fixing out of order packets)
        self.nextPacketExpected = 0
        # Holds packets that have been sent. If they are correctly received, they are removed. Otherwise, resent later.
        self.sentPackets = list()
        #
        self.packetsWaiting = list()
        # If start iteration is 2 or more behind current iteration, send packet again
        self.timeout = 2

    # Called by main to set the unreliable sending lower-layer channel
    def setSendChannel(self, channel):
        self.sendChannel = channel

    # Called by main to set the unreliable receiving lower-layer channel
    def setReceiveChannel(self, channel):
        self.receiveChannel = channel

    # Called by main to set the string data to send
    def setDataToSend(self,data):
        self.dataToSend = data

    # Called by main to get the currently received and buffered string data, in order
    def getDataReceived(self):
        return self.dataReceived

    # "timeslice". Called by main once per iteration
    def manage(self):
        self.currentIteration += 1
        self.manageSend()
        self.manageReceive()

    # Manage Segment sending  tasks...
    def manageSend(self):

        # You should pipeline segments to fit the flow-control window
        # The flow-control window is the constant RDTLayer.FLOW_CONTROL_WIN_SIZE
        # The maximum data that you can send in a segment is RDTLayer.DATA_LENGTH
        # These constants are given in # characters

        # Variable to keep up with how many packets have been sent in a given call to manageSend()
        # to ensure more packets are not sent than what is allowed.
        packetsThisLoop = 0

        # Loop through the list of packets sent but not acknowledged and try to resend.
        for seg in self.sentPackets:
            # If the packet has a checksum error, reset the payload then resend and reset startIteration.
            if not seg.checkChecksum() and packetsThisLoop < \
                    int(RDTLayer.FLOW_CONTROL_WIN_SIZE / RDTLayer.DATA_LENGTH):
                seg.setData(seg.seqnum, self.dataToSend[seg.seqnum:seg.seqnum + 4])
                self.sendChannel.send(seg)
                seg.setStartIteration(self.currentIteration)
                packetsThisLoop += 1
            # If packet was lost or delayed, resend and reset the startIteration.
            elif seg.startIteration + self.timeout < self.currentIteration and packetsThisLoop < \
                    int(RDTLayer.FLOW_CONTROL_WIN_SIZE / RDTLayer.DATA_LENGTH):
                self.sendChannel.send(seg)
                seg.setStartIteration(self.currentIteration)
                packetsThisLoop += 1

        # NOTE: I TRIED TO IMPLEMENT THE SLIDING WINDOW HERE WITH THE COMMENTED OUT IF STATEMENT,
        # BUT IT CAUSED THE PROGRAM TO INFINITELY LOOP EVERY FEW RUNS. THEREFORE, SLIDING WINDOW
        # DOES NOT WORK AND HAS NOT BEEN IMPLEMENTED.
        # if len(sentPackets) < int(RDTLayer.FLOW_CONTROL_WIN_SIZE / RDTLayer.DATA_LENGTH):
        while packetsThisLoop < int(RDTLayer.FLOW_CONTROL_WIN_SIZE / RDTLayer.DATA_LENGTH):
            if self.fromIndex >= len(self.dataToSend):
                break

            seg = Segment()
            seg.setStartIteration(self.currentIteration)
            seg.setData(self.seqnum, self.dataToSend[self.fromIndex:self.toIndex])

            # Use the unreliable sendChannel to send the segment
            self.sendChannel.send(seg)
            self.sentPackets.append(seg)
            packetsThisLoop += 1
            self.fromIndex += 4
            self.toIndex += 4
            self.seqnum += 4

    # Manage Segment receive tasks...
    def manageReceive(self):
        # This call returns a list of incoming segments (see Segment class)...
        listIncoming = self.receiveChannel.receive()

        # Append everything in the listIncoming list to member list packetsWaiting.
        # I used this new list to fix the outOfOrder flag. Packets stay in this list
        # until they are sent in the correct order.
        for seg in listIncoming:
            self.packetsWaiting.append(seg)

        # Loops through all segments in member list packetsWaiting.
        for seg in self.packetsWaiting:
            # If the current segment is a data packet and is the next segment expected (by seqnum),
            # add it to the end of the data received string and send an ack to the sender. Packet
            # is also removed from packetsWaiting. An ack will only be sent for packets that are
            # the both the next expected in the sequence, and free of checksum errors. Otherwise,
            # they will be left in the packetWaiting list and either resent (if there is an error)
            # or checked for correct sequence next time manageReceive is called.
            if seg.seqnum >= 0:
                if seg.seqnum == self.nextPacketExpected and seg.checkChecksum():
                    self.dataReceived += seg.payload
                    ack = Segment()
                    acknum = seg.seqnum + RDTLayer.DATA_LENGTH
                    ack.setAck(acknum)
                    self.sendChannel.send(ack)
                    # Set the number of the next expected packet.
                    self.nextPacketExpected = acknum
                    # Since the packet was the next expected, it was clearly sent in order
                    # and can be removed from the packets waiting list.
                    self.packetsWaiting.remove(seg)

            # If the current segment is an ack packet, add it to the member list acksReceived. Also,
            # update the member list sentPackets to include only those packets who were sent, but
            # never received.
            if seg.acknum >= 0:
                self.acksReceived.append(seg)
                self.sentPackets = [x for x in self.sentPackets if (x.seqnum + RDTLayer.DATA_LENGTH) > seg.acknum]

# SOURCES CITED:
# Kurose & Ross, Computer Networking: A Top-Down Approach (7th Edition), Chapter 3.4

import smbus
import time

# RPI version 1, must use "bus = smbus.SMBus(0)"
bus = smbus.SMBus(0)

# This is the address we setup in the Arduino Program
address = 0x04


def writeNumber(value):
    bus.write_byte(address, value)
    # bus.write_byte_data(address, 0, value)
    return -1


def read_team_and_player():
    try:
        data = bus.read_i2c_block_data(address, 0, 2)
        print len(data), "/", data
        team = data[0];
        player = data[1];
        return (team, player)
    except IOError:
        return (-1, -1)


while True:
    time.sleep(1)
    team, player = read_team_and_player()
    if team == -1:
        continue
    print "Winner: %d, Player: %d" % (team, player)
    print

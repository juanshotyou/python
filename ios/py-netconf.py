#!usr/bin/env python3

from ncclient import manager

IOSXE_HOST = "192.168.0.210"
NETCONF_PORT = "830"
USERNAME = "netconf"
PASSWORD = "n3tc0nfp4ss"
LOOPBACK_ID = "99"
LOOPBACK_IP = "99.99.99.99"

""" Get device capabilities """

def getCapabilities():

    with manager.connect(host=IOSXE_HOST,port=NETCONF_PORT,username=USERNAME,password=PASSWORD,hostkey_verify=False) as device:
        print("\n***NETCONF capabilities for device {}***\n".format(IOSXE_HOST))
        for capability in device.server_capabilities:
            print(capability)

""" Create a loopback interface and assign an IP address for it """

def addLoopback():

    add_loop_interface = """<config>
              <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
                <interface>
                  <name>{id}</name>
                  <description>Interface created with NETCONF</description>
                  <type xmlns:ianaift="urn:ietf:params:xml:ns:yang:iana-if-type">
                    ianaift:softwareLoopback
                  </type>
                  <enabled>true</enabled>
                  <ipv4 xmlns="urn:ietf:params:xml:ns:yang:ietf-ip">
                    <address>
                      <ip>{ip}</ip>
                      <netmask>255.255.255.255</netmask>
                    </address>
                  </ipv4>
                </interface>
              </interfaces>
            </config>""".format(id=LOOPBACK_ID, ip=LOOPBACK_IP)

    with manager.connect(host=IOSXE_HOST,port=NETCONF_PORT,username=USERNAME,password=PASSWORD,hostkey_verify=False) as device:
        print("\n Adding Loopback {} with IP address {} to device {}...\n".format(LOOPBACK_ID, LOOPBACK_IP, IOSXE_HOST))
        netconf_response = device.edit_config(target='running',config=add_loop_interface)
        print(netconf_response)

if __name__ == "__main__":
    getCapabilities()
    addLoopback()

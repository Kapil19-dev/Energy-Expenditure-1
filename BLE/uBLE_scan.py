#!/usr/bin/env python3
import gatt

manager = gatt.DeviceManager(adapter_name='hci0')

class AnyDevice(gatt.Device):
    def connect_succeeded(self):
        super().connect_succeeded()
        print("[%s] Connected" % (self.mac_address))

    def connect_failed(self, error):
        super().connect_failed(error)
        print("[%s] Connection failed: %s" % (self.mac_address, str(error)))

    def disconnect_succeeded(self):
        super().disconnect_succeeded()
        print("[%s] Disconnected" % (self.mac_address))

    def services_resolved(self):
        super().services_resolved()

        print("[%s] Resolved services" % (self.mac_address))
        for service in self.services:
            print("[%s]  Service [%s]" % (self.mac_address, service.uuid))
            for characteristic in service.characteristics:
                print("[%s]    Characteristic [%s]" % (self.mac_address, characteristic.uuid))

#30:AE:A4:CC:26:12 - esp32
#D0:41:AF:74:f6:F1 - geonaute
#F0:57:3B:FB:D6:C2 - band
#F1:1B:B0:E1:6F:C1 - poço
device = AnyDevice(mac_address='D0:41:AF:74:f6:F1', manager=manager)
device.connect()

manager.run()
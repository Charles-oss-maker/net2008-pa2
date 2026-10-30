# Name: Charles Nwabuisi
# Student ID: 101382788 
import sys
import xml.etree.ElementTree as ET

class Device:
    """One network device from the inventory."""

    def __init__(self, el):
        """Read the fields and count interfaces by status."""
        self.id = el.get("id")
        self.role = el.get("role")
        self.os = el.get("os")
        self.owner = (el.findtext("owner") or "").strip()
        self.up = 0
        self.down = 0
        self.other = 0
        for iface in el.findall("interface"):
            status = iface.get("status")
            # TODO: if status is "up", add 1 to self.up
            # TODO: elif status is "down", add 1 to self.down
            # TODO: else add 1 to self.other

    def has_owner(self):
        """Return True if the device has a non-empty owner."""
        # TODO: return True when self.owner is not an empty string

def main():
    """Entry point: print the id of every device in the inventory."""
    root = ET.parse(sys.argv[1]).getroot()
    for el in root.findall("device"):
        print(el.get("id"))


if __name__ == "__main__":
    main()
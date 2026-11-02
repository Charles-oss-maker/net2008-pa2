# Name: Charles Nwabuisi
# Student ID: 101382788 
from email import policy
import sys 
import yaml



import xml.etree.ElementTree as ET

class AuditError(Exception):
    """An error in the audit process."""
    pass

def load_policy(filename):
    """Load the policy from a YAML file."""
    try:
        with open(filename) as f:
            policy = yaml.safe_load(f)
    except FileNotFoundError:
        raise AuditError(f"Policy file {filename} not found")
    except yaml.YAMLError as e:
        raise AuditError(f"Error parsing policy file {filename}: {e}")
    if policy is None:
        raise AuditError(f"Policy file {filename} is empty")
    if not isinstance(policy, dict):
        raise AuditError(f"Policy file {filename} does not contain a dictionary")
    print(policy)
    return policy


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
            if status:
                self.up += 1
            elif not status:
                self.down += 1
            
            # TODO: else add 1 to self.other
            else:
                self.other += 1

    def has_owner(self):    
        """Return True if the device has a non-empty owner."""  
        # TODO: return True when self.owner is not an empty string
        if self.owner != " ":
            return True


def main():
    """Entry point: print the id of every device in the inventory."""
    yaml_policy = sys.argv[2]
    load_policy(yaml_policy)


    root = ET.parse(sys.argv[1]).getroot()
    kept = []
    skipped = 0
    for ele in root.findall("device"):
        if ele.get("id") is None:
            skipped += 1
            continue
        continue
    kept.append(Device(ele))
    

    for el in root.findall("device"):
        print(el.get("id"))

    print(f"Skipped {skipped} devices with no id")
    for device in kept:
        print(f"{device.id}: {device.up} up, {device.down} down, {device.other} other")

        print(f"Policy: {yaml_policy}")



if __name__ == "__main__":
    main()
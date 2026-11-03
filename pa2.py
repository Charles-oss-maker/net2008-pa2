
# Name: Charles Nwabuisi
# Student ID: 101382788

import sys
import json
import yaml
import xml.etree.ElementTree as ET
from collections import Counter


class AuditError(Exception):
    """Custom exception for audit errors."""
    pass


class Device:
    """Represent a network device and its interfaces."""

    def __init__(self, element):
        """Extract device information from an XML element."""
        self.id = element.get("id")
        self.role = element.get("role")
        self.os = element.get("os")
        self.owner = (element.findtext("owner") or "").strip()

        self.up = 0
        self.down = 0
        self.other = 0

        for interface in element.findall("interface"):
            status = interface.get("status")

            if status == "up":
                self.up += 1
            elif status == "down":
                self.down += 1
            else:
                self.other += 1

    def has_owner(self):
        """Check whether the device has a non-empty owner."""
        return bool(self.owner)


def load_policy(filename):
    """Load and validate the YAML policy file."""
    try:
        with open(filename, encoding="utf-8") as file:
            policy = yaml.safe_load(file)

    except FileNotFoundError:
        raise AuditError(f"Policy file {filename} not found")
    except yaml.YAMLError as error:
        raise AuditError(f"Invalid YAML file {filename}: {error}")
    except OSError as error:
        raise AuditError(f"Cannot read {filename}: {error}")

    if policy is None:
        raise AuditError(f"Policy file {filename} is empty")

    if not isinstance(policy, dict):
        raise AuditError(f"Policy file {filename} must contain a mapping")

    return policy


def load_inventory(filename):
    """Load and validate the XML inventory."""
    try:
        return ET.parse(filename).getroot()

    except FileNotFoundError:
        raise AuditError(f"Inventory file {filename} not found")
    except ET.ParseError as error:
        raise AuditError(f"Invalid XML file {filename}: {error}")
    except OSError as error:
        raise AuditError(f"Cannot read {filename}: {error}")


def version_tuple(version):
    """Convert a dotted version into comparable integer parts."""
    return tuple(int(part) for part in version.split("."))


def audit_device(device, policy):
    """Check a device against the compliance policy."""
    violations = []

    min_os = policy.get("min_os", {})

    if "min_os" in policy:
        if device.role not in min_os:
            violations.append({
                "device": device.id,
                "type": "unknown_role",
                "role": device.role
            })

        else:
            required = min_os[device.role]

            if device.os is not None:
                if version_tuple(device.os) < version_tuple(required):
                    violations.append({
                        "device": device.id,
                        "type": "os_outdated",
                        "found": device.os,
                        "required": required
                    })

    if policy.get("require_owner") is True:
        if not device.has_owner():
            violations.append({
                "device": device.id,
                "type": "missing_owner"
            })

    if "max_down_interfaces" in policy:
        if device.down > policy["max_down_interfaces"]:
            violations.append({
                "device": device.id,
                "type": "too_many_down",
                "down": device.down
            })

    return violations


def main():
    """Run the fleet compliance audit."""
    if len(sys.argv) != 3:
        print("usage: python pa2.py DEVICES.xml POLICY.yaml")
        return 2

    xml_filename = sys.argv[1]
    yaml_filename = sys.argv[2]

    try:
        policy = load_policy(yaml_filename)
        root = load_inventory(xml_filename)

        devices = []
        skipped = 0

        for element in root.findall("device"):
            if element.get("id") is None:
                skipped += 1
                continue

            devices.append(Device(element))

        roles = Counter()
        interfaces = Counter()
        violations = []
        compliant = []

        for device in devices:
            roles[device.role] += 1

            interfaces["up"] += device.up
            interfaces["down"] += device.down
            interfaces["other"] += device.other

            device_violations = audit_device(device, policy)

            violations.extend(device_violations)

            if not device_violations:
                compliant.append(device.id)

        report = {
            "site": root.get("site"),
            "total_devices": len(devices),
            "skipped_devices": skipped,
            "roles": dict(roles),
            "interfaces": {
                "up": interfaces["up"],
                "down": interfaces["down"],
                "other": interfaces["other"]
            },
            "violations": violations,
            "compliant": sorted(compliant)
        }

        with open("audit.json", "w", encoding="utf-8") as file:
            json.dump(report, file, indent=4)

        print(f"Audit complete: {len(devices)} devices")
        print(f"Skipped: {skipped}")
        print(f"Violations: {len(violations)}")
        print(f"Compliant: {len(compliant)}")
        print("Report saved to audit.json")

        return 0

    except AuditError as error:
        print(error, file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

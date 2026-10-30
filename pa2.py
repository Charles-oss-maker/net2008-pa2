# Name: Charles Nwabuisi
# Student ID: 101382788 
import sys
import xml.etree.ElementTree as ET


def main():
    """Entry point: print the id of every device in the inventory."""
    root = ET.parse(sys.argv[1]).getroot()
    for el in root.findall("device"):
        print(el.get("id"))


if __name__ == "__main__":
    main()
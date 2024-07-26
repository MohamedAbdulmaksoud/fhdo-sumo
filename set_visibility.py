# sets the visibility attribute for the <parkingAreaReroute> elements as described. The script takes a file as a
# required parameter and has an optional --all-false flag to set all visibility to false.
# python3 ../../set_visibility.py parking.rerouter.add.xml

import xml.etree.ElementTree as ET
import argparse


def set_visibility(file, all_false=False, all_true=False):
    """
    Sets the visibility attribute for parkingAreaReroute elements in an XML file.

    Parameters:
    file (str): The path to the XML file to modify.
    all_false (bool): If True, sets all visibility attributes to 'false'.
    all_true (bool): If True, sets all visibility attributes to 'true'.
    """
    # Parse the XML file
    tree = ET.parse(file)
    root = tree.getroot()

    # Define the namespaces
    namespaces = {
        'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
    }

    # Iterate over all rerouter elements
    for rerouter in root.findall('rerouter'):
        if all_true:
            # Set all parkingAreaReroute elements to true
            for parkingAreaReroute in rerouter.findall('interval/parkingAreaReroute'):
                parkingAreaReroute.set('visible', 'true')
        elif all_false:
            # Set all parkingAreaReroute elements to false
            for parkingAreaReroute in rerouter.findall('interval/parkingAreaReroute'):
                parkingAreaReroute.set('visible', 'false')
        else:
            # Default behavior: Set the first parkingAreaReroute visible to true and others to false
            first_parking_set = False
            for parkingAreaReroute in rerouter.findall('interval/parkingAreaReroute'):
                if not first_parking_set:
                    parkingAreaReroute.set('visible', 'true')
                    first_parking_set = True
                else:
                    parkingAreaReroute.set('visible', 'false')

    # Add namespaces to the root element
    ET.register_namespace('xsi', namespaces['xsi'])
    root.set('xmlns:xsi', namespaces['xsi'])
    root.set('xsi:noNamespaceSchemaLocation', 'http://sumo.dlr.de/xsd/additional_file.xsd')

    # Write the modified XML back to the file
    tree.write(file, encoding='utf-8', xml_declaration=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Set visibility of parkingAreaReroute elements in XML file.")
    parser.add_argument("file", help="The XML file to modify.")
    parser.add_argument("--all-false", action="store_true", help="Set all visibility attributes to false.")
    parser.add_argument("--all-true", action="store_true", help="Set all visibility attributes to true.")

    args = parser.parse_args()

    # Ensure only one visibility flag is used at a time
    if args.all_false and args.all_true:
        print("Error: --all-false and --all-true cannot be used together.")
        sys.exit(1)

    if args.all_false or args.all_true:
        set_visibility(args.file, all_false=args.all_false, all_true=args.all_true)
    else:
        set_visibility(args.file)

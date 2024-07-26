# sets the visibility attribute for the <parkingAreaReroute> elements as described. The script takes a file as a
# required parameter and has an optional --all-false flag to set all visibility to false.
# python3 ../../set_visibility.py parking.rerouter.add.xml

import xml.etree.ElementTree as ET
import argparse


def set_visibility(file, all_false=False):
    """
    Sets the visibility attribute for parkingAreaReroute elements in an XML file.

    Parameters:
    file (str): The path to the XML file to modify.
    all_false (bool): If True, sets all visibility attributes to 'false'. If False, sets only the first visibility to 'true' and the rest to 'false' for each rerouter.
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
        first_parking_set = False
        # Iterate over all parkingAreaReroute elements within the rerouter
        for parkingAreaReroute in rerouter.findall('interval/parkingAreaReroute'):
            if all_false:
                # Set all visibility attributes to false
                parkingAreaReroute.set('visible', 'false')
            else:
                if not first_parking_set:
                    # Set the first parkingAreaReroute visible to true
                    parkingAreaReroute.set('visible', 'true')
                    first_parking_set = True
                else:
                    # Set all subsequent visibility attributes to false
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

    args = parser.parse_args()
    set_visibility(args.file, args.all_false)

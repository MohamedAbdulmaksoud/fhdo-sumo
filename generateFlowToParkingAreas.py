import xml.etree.ElementTree as ET
import argparse
import random


# Function to parse ParkingAreas XML and extract parking area data
def parse_parking_areas(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    parking_areas = []
    for parking_area in root.findall('parkingArea'):
        id = parking_area.get('id')
        capacity = int(parking_area.get('roadsideCapacity'))
        parking_areas.append((id, capacity))
    return parking_areas


# Function to read edges from a file
def read_edges(file_path):
    with open(file_path, 'r') as file:
        edges_line = file.readline().strip()
    edge_list = edges_line.split(',')
    return edge_list


# Function to create a new Routes XML with flows based on parking areas and edge IDs
def create_routes_xml(parking_areas, edge_list, flow_factor, output_file):
    routes = ET.Element('routes', {
        'xmlns:xsi': "http://www.w3.org/2001/XMLSchema-instance",
        'xsi:noNamespaceSchemaLocation': "http://sumo.dlr.de/xsd/routes_file.xsd"
    })

    for id, capacity in parking_areas:
        from_edge = random.choice(edge_list)
        flow = ET.SubElement(routes, 'flow', {
            'id': f'flow_{id}',
            'type': 'car',
            'begin': '2',
            'period': '2',
            'number': str(flow_factor * capacity),
            'from': from_edge
        })
        stop = ET.SubElement(flow, 'stop', {
            'parkingArea': id,
            'duration': '3600'
        })

    tree = ET.ElementTree(routes)
    tree.write(output_file, encoding='UTF-8', xml_declaration=True)


def main():
    parser = argparse.ArgumentParser(description='Generate Routes XML from ParkingAreas XML')
    parser.add_argument('-pa', '--parkingAreas', type=str, required=True, help='Path to the ParkingAreas XML file')
    parser.add_argument('-o', '--output', type=str, required=True, help='Path to the output Routes XML file')
    parser.add_argument('-fe', '--flowEdges', type=str, required=True,
                        help='Path to the file containing comma-separated edge IDs')
    parser.add_argument('-ff', '--flow-factor', type=int, default=2,
                        help='Factor to multiply with capacity for flow number')

    args = parser.parse_args()

    # Parse parking areas and edge list
    parking_areas = parse_parking_areas(args.parkingAreas)
    edge_list = read_edges(args.flowEdges)

    # Generate routes XML
    create_routes_xml(parking_areas, edge_list, args.flow_factor, args.output)


if __name__ == '__main__':
    main()

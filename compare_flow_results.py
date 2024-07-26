# This tool reads vehroute-output with exit-times and generates statistics for the time and the distance vehicles
# spent on searching parking locations as well as the length of the walking way back. It evaluates the time and
# distance between the first reroute and the arrival at the final stop.
# @file    parkingSearchTraffic.py
# @author  Michael Behrisch - Mohamed Abdulmaksoud
# @date    2024-07-26

import os
import argparse
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt

"""
    Recursively searches for all 'flow_results.xml' files within the specified main directory.

    Parameters:
    main_directory (str): The main directory to start searching from.

    Returns:
    list: A list of file paths to 'flow_results.xml' files found within the directory structure.
"""


def find_flow_result_files(main_directory):
    flow_result_files = []
    for root, _, files in os.walk(main_directory):
        for file in files:
            if file == "flow_results.xml":
                flow_result_files.append(os.path.join(root, file))
    return flow_result_files


"""
    Extracts summary data from a 'flow_results.xml' file.

    Parameters:
    file_path (str): The path to the 'flow_results.xml' file.

    Returns:
    tuple: A tuple containing:
        - parent_directory (str): The name of the parent directory containing the XML file.
        - data (dict): A dictionary with summary statistics:
            - 'total_vehicles' (int): Total number of vehicles.
            - 'total_distance' (float): Total distance traveled by all vehicles.
            - 'total_time' (float): Total travel time of all vehicles.
            - 'total_walking_distance' (float): Total walking distance.
            - 'not_arrived' (int): Total number of vehicles that did not arrive.
    """


def extract_summary_data(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()

    summary = root.find('Summary')
    data = {
        'total_vehicles': int(summary.find('TotalVehicles').text),
        'total_distance': float(summary.find('TotalDistance').text),
        'total_time': float(summary.find('TotalTime').text),
        'total_walking_distance': float(summary.find('TotalWalkingDistance').text),
        'not_arrived': int(summary.find('NotArrived').text)
    }

    parent_directory = os.path.basename(os.path.dirname(os.path.dirname(file_path)))
    return parent_directory, data


"""
    Extracts data for a specific flow from a 'flow_results.xml' file.

    Parameters:
    file_path (str): The path to the 'flow_results.xml' file.
    flow_name (str): The ID of the flow to extract data for.

    Returns:
    tuple: A tuple containing:
        - parent_directory (str): The name of the parent directory containing the XML file.
        - data (dict): A dictionary with flow-specific statistics:
            - 'total_vehicles' (int): Total number of vehicles in the flow.
            - 'total_distance' (float): Total distance traveled by vehicles in the flow.
            - 'total_time' (float): Total travel time of vehicles in the flow.
            - 'total_walking_distance' (float): Total walking distance in the flow.
            - 'not_arrived' (int): Total number of vehicles in the flow that did not arrive.
    """


def extract_flow_data(file_path, flow_name):
    tree = ET.parse(file_path)
    root = tree.getroot()

    for flow in root.findall('Flow'):
        if flow.get('id') == flow_name:
            data = {
                'total_vehicles': int(flow.find('TotalVehicles').text),
                'total_distance': float(flow.find('TotalDistance').text),
                'total_time': float(flow.find('TotalTime').text),
                'total_walking_distance': float(flow.find('TotalWalkingDistance').text),
                'not_arrived': int(flow.find('NotArrived').text)
            }
            parent_directory = os.path.basename(os.path.dirname(os.path.dirname(file_path)))
            return parent_directory, data
    return None, None


"""
    Generates a bar plot comparing specified metrics across different simulations and saves the plot.

    Parameters:
    data (dict): A dictionary where keys are simulation labels and values are the metric values.
    title (str): The title of the plot.
    y_label (str): The label for the y-axis.
    output_path (str): The path to save the generated plot.
    is_flow (bool): Indicates whether the plot is for a specific flow. Default is False.
    """


def plot_comparison(data, title, y_label, output_path, is_flow=False):
    plt.figure(figsize=(10, 6))
    for label, values in data.items():
        plt.bar(label, values)

    plt.xlabel('Simulation Run')
    plt.ylabel(y_label)
    plt.title(title)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    if is_flow:
        output_file = os.path.join(output_path, f"{title.replace(' ', '_')}_comparison_flow.png")
    else:
        output_file = os.path.join(output_path, f"{title.replace(' ', '_')}_comparison_summary.png")

    plt.savefig(output_file)
    plt.close()


def main(main_directory, flow_name=None):
    flow_result_files = find_flow_result_files(main_directory)

    summary_data = {}
    flow_data = {}

    for file in flow_result_files:
        if flow_name:
            label, data = extract_flow_data(file, flow_name)
            if data:
                flow_data[label] = data
        else:
            label, data = extract_summary_data(file)
            summary_data[label] = data

    output_path = os.path.join(main_directory, "..")

    if flow_name:
        plot_comparison({k: v['total_vehicles'] for k, v in flow_data.items()}, f"Total Vehicles for Flow {flow_name}",
                        "Total Vehicles", output_path, is_flow=True)
        plot_comparison({k: v['total_distance'] for k, v in flow_data.items()}, f"Total Distance for Flow {flow_name}",
                        "Total Distance (m)", output_path, is_flow=True)
        plot_comparison({k: v['total_time'] for k, v in flow_data.items()}, f"Total Time for Flow {flow_name}",
                        "Total Time (s)", output_path, is_flow=True)
        plot_comparison({k: v['total_walking_distance'] for k, v in flow_data.items()},
                        f"Total Walking Distance for Flow {flow_name}", "Total Walking Distance (m)", output_path,
                        is_flow=True)
        plot_comparison({k: v['not_arrived'] for k, v in flow_data.items()},
                        f"Vehicles Not Arrived for Flow {flow_name}", "Not Arrived", output_path, is_flow=True)
    else:
        plot_comparison({k: v['total_vehicles'] for k, v in summary_data.items()}, "Total Vehicles Summary",
                        "Total Vehicles", output_path)
        plot_comparison({k: v['total_distance'] for k, v in summary_data.items()}, "Total Distance Summary",
                        "Total Distance (m)", output_path)
        plot_comparison({k: v['total_time'] for k, v in summary_data.items()}, "Total Time Summary", "Total Time (s)",
                        output_path)
        plot_comparison({k: v['total_walking_distance'] for k, v in summary_data.items()},
                        "Total Walking Distance Summary", "Total Walking Distance (m)", output_path)
        plot_comparison({k: v['not_arrived'] for k, v in summary_data.items()}, "Vehicles Not Arrived Summary",
                        "Not Arrived", output_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compare flow results from multiple simulations.")
    parser.add_argument("main_directory", help="Main directory containing the simulation results.")
    parser.add_argument("--flow_name", help="Specific flow name to compare", required=False)
    args = parser.parse_args()

    main(args.main_directory, args.flow_name)

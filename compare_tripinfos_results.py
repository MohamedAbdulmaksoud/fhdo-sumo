import os
import argparse
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import numpy as np


def parse_tripinfo(file):
    """Parse the tripinfo XML file and return total CO2_abs, fuel_abs, and timeLoss."""
    tree = ET.parse(file)
    root = tree.getroot()

    total_CO2_abs = 0
    total_fuel_abs = 0
    total_timeLoss = 0

    for tripinfo in root.findall('tripinfo'):
        emissions = tripinfo.find('emissions')
        total_CO2_abs += float(emissions.get('CO2_abs'))
        total_fuel_abs += float(emissions.get('fuel_abs'))
        total_timeLoss += float(tripinfo.get('timeLoss'))

    # Convert units
    total_CO2_abs /= 1000  # grams to kilograms
    total_fuel_abs /= 1000  # grams to kilograms
    total_timeLoss /= 3600  # seconds to hours

    return total_CO2_abs, total_fuel_abs, total_timeLoss


def plot_comparison(data, labels, output_file_prefix):
    """Plot a comparison of total CO2_abs, fuel_abs, and timeLoss for different simulations."""
    num_simulations = len(data)

    CO2_abs = [d[0] for d in data]
    fuel_abs = [d[1] for d in data]
    timeLoss = [d[2] for d in data]

    x = np.arange(num_simulations)  # label locations
    width = 0.5  # bar width

    # Define colors for each label
    colors = {
        'parkAnywhere_1_visible': 'blue',
        'no_memory': 'orange',
        'frustration_100': 'green',
        'knowledge_1': 'red',
        'parkAnywhere': 'purple',
        'active_memory': 'brown',
        'all_visible': 'pink'
    }
    bar_colors = [colors[label] for label in labels]

    fig, ax = plt.subplots()
    bars = ax.bar(x, CO2_abs, width, color=bar_colors)

    ax.set_xlabel('Simulations')
    ax.set_ylabel('CO2 Emissions (kg)')
    ax.set_title('Comparison of CO2 Emissions across Simulations')
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45, fontsize='small')
    ax.legend()

    ax.bar_label(bars, padding=3)

    fig.tight_layout()
    plt.savefig(f'{output_file_prefix}_CO2_abs.png')
    plt.show()

    fig, ax = plt.subplots()
    bars = ax.bar(x, fuel_abs, width, color=bar_colors)

    ax.set_xlabel('Simulations')
    ax.set_ylabel('Fuel Consumption (kg)')
    ax.set_title('Comparison of Fuel Consumption across Simulations')
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45, fontsize='small')
    ax.legend()

    ax.bar_label(bars, padding=3)

    fig.tight_layout()
    plt.savefig(f'{output_file_prefix}_fuel_abs.png')
    plt.show()

    fig, ax = plt.subplots()
    bars = ax.bar(x, timeLoss, width, color=bar_colors)

    ax.set_xlabel('Simulations')
    ax.set_ylabel('Time Loss (hours)')
    ax.set_title('Comparison of Time Loss across Simulations')
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45, fontsize='small')
    ax.legend()

    ax.bar_label(bars, padding=3)

    fig.tight_layout()
    plt.savefig(f'{output_file_prefix}_timeLoss.png')
    plt.show()


def main(input_files, labels, output_file_prefix):
    data = []
    for file in input_files:
        total_CO2_abs, total_fuel_abs, total_timeLoss = parse_tripinfo(file)
        data.append((total_CO2_abs, total_fuel_abs, total_timeLoss))

    plot_comparison(data, labels, output_file_prefix)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Compare and visualize total CO2_abs, fuel_abs, and timeLoss from multiple tripinfos.xml files.")
    parser.add_argument('-i', '--input', required=True, nargs='+', help="List of tripinfos.xml files to compare.")
    parser.add_argument('-l', '--labels', required=True, nargs='+',
                        help="Labels for the corresponding tripinfos.xml files.")
    parser.add_argument('-o', '--output', required=True, help="Output file prefix for the comparison plots.")

    args = parser.parse_args()

    if len(args.input) != len(args.labels):
        print("Error: The number of input files must match the number of labels.")
        sys.exit(1)

    main(args.input, args.labels, args.output)

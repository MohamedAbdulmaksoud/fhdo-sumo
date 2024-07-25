#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Eclipse SUMO, Simulation of Urban MObility; see https://eclipse.dev/sumo
# Copyright (C) 2008-2023 German Aerospace Center (DLR) and others.
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License 2.0 which is available at
# https://www.eclipse.org/legal/epl-2.0/
# This Source Code may also be made available under the following Secondary
# Licenses when the conditions for such availability set forth in the Eclipse
# Public License 2.0 are satisfied: GNU General Public License, version 2
# or later which is available at
# https://www.gnu.org/licenses/old-licenses/gpl-2.0-standalone.html
# SPDX-License-Identifier: EPL-2.0 OR GPL-2.0-or-later

# @file    parkingSearchTraffic.py
# @author  Michael Behrisch - Mohamed Abdulmaksoud
# @date    2024-07-26

from __future__ import absolute_import
from __future__ import print_function
import os
import sys
import xml.etree.ElementTree as ET

sys.path.append(os.path.join(os.environ["SUMO_HOME"], 'tools'))
import sumolib  # noqa
from sumolib.options import ArgumentParser  # noqa


def parse_args():
    optParser = ArgumentParser()
    optParser.add_argument("net", help="net file")
    optParser.add_argument("routes", help="route file")
    return optParser.parse_args()


def write_results_to_xml(flow_results, total_summary, output_file):
    root = ET.Element("Results")

    # Create a summary element for all vehicles
    summary = ET.SubElement(root, "Summary")
    ET.SubElement(summary, "TotalVehicles").text = str(total_summary["total_vehicles"])
    ET.SubElement(summary, "TotalDistance").text = str(total_summary["total_distance"])
    ET.SubElement(summary, "TotalTime").text = str(total_summary["total_time"])
    ET.SubElement(summary, "TotalWalkingDistance").text = str(total_summary["total_walking_distance"])
    ET.SubElement(summary, "NotArrived").text = str(total_summary["not_arrived"])

    for flow_id, data in flow_results.items():
        flow_element = ET.SubElement(root, "Flow", id=flow_id)
        ET.SubElement(flow_element, "TotalVehicles").text = str(data["total_vehicles"])
        ET.SubElement(flow_element, "TotalDistance").text = str(data["total_distance"])
        ET.SubElement(flow_element, "TotalTime").text = str(data["total_time"])
        ET.SubElement(flow_element, "TotalWalkingDistance").text = str(data["total_walking_distance"])
        ET.SubElement(flow_element, "NotArrived").text = str(data["not_arrived"])

    tree = ET.ElementTree(root)
    tree.write(output_file)


def main(net, routes):
    net = sumolib.net.readNet(net)
    dist = sumolib.miscutils.Statistics("Distance")
    time = sumolib.miscutils.Statistics("Time")
    walk_dist = sumolib.miscutils.Statistics("Walking Distance")

    flow_results = {}
    total_summary = {
        "total_vehicles": 0,
        "total_distance": 0,
        "total_time": 0,
        "total_walking_distance": 0,
        "not_arrived": 0
    }

    for vehicle in sumolib.xml.parse(routes, 'vehicle'):
        flow_id = vehicle.id.split('.')[0]  # Identify flow by ID before "."

        if flow_id not in flow_results:
            flow_results[flow_id] = {
                "total_vehicles": 0,
                "total_distance": 0,
                "total_time": 0,
                "total_walking_distance": 0,
                "not_arrived": 0
            }

        flow_results[flow_id]["total_vehicles"] += 1
        total_summary["total_vehicles"] += 1

        if not vehicle.stop:
            print("Warning! Vehicle '%s' did not arrive." % vehicle.id)
            flow_results[flow_id]["not_arrived"] += 1
            total_summary["not_arrived"] += 1
            continue

        if vehicle.routeDistribution and vehicle.stop:
            replace_index = None
            for r in vehicle.routeDistribution[0].route:
                if replace_index is None and r.replacedOnEdge:
                    replace_index = len(r.edges.split())
                    replace_time = r.replacedAtTime
            extra_route = r.edges.split()[replace_index:]
            length = sum([net.getEdge(e).getLength() for e in extra_route])
            dist.add(length, vehicle.id)
            flow_results[flow_id]["total_distance"] += length
            total_summary["total_distance"] += length

            start_time = vehicle.stop[0].started
            if start_time is not None:
                elapsed_time = sumolib.miscutils.parseTime(start_time) - sumolib.miscutils.parseTime(replace_time)
                time.add(elapsed_time, vehicle.id)
                flow_results[flow_id]["total_time"] += elapsed_time
                total_summary["total_time"] += elapsed_time

            if extra_route:
                walk, _ = net.getShortestPath(net.getEdge(extra_route[-1]), net.getEdge(extra_route[0]),
                                              ignoreDirection=True)
                walk_length = sum([e.getLength() for e in walk])
            else:
                walk_length = 0

            walk_dist.add(walk_length, vehicle.id)
            flow_results[flow_id]["total_walking_distance"] += walk_length
            total_summary["total_walking_distance"] += walk_length
        else:
            dist.add(0, vehicle.id)
            time.add(0, vehicle.id)
            walk_dist.add(0, vehicle.id)
            flow_results[flow_id]["total_distance"] += 0
            flow_results[flow_id]["total_time"] += 0
            flow_results[flow_id]["total_walking_distance"] += 0

    print(dist)
    print(time)
    print(walk_dist)

    # Export results to XML
    output_file = "/output/flow_results.xml"
    write_results_to_xml(flow_results, total_summary, output_file)
    print(f"Results exported to {output_file}")


if __name__ == "__main__":
    options = parse_args()
    main(options.net, options.routes)

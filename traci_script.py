import sumolib
import traci
import locale
locale.setlocale(locale.LC_ALL, 'C')

def start_simulation(config_file):
    # Start the SUMO simulation with the provided config file
    traci.start(['sumo-gui', '-c', config_file])


def highlight_vehicle(vehicle_id):
    # Highlight a specific vehicle in the SUMO GUI
    traci.gui.trackVehicle(traci.gui.getIDList()[0], vehicle_id)
    traci.gui.setZoom(traci.gui.getIDList()[0], 2000)


def find_nearest_parking_area(vehicle_pos):
    # Function to find the nearest parking area to a given position
    min_distance = float('inf')
    nearest_parking = None

    try:
        parking_area_ids = traci.parkingarea.getIDList()
    except traci.exceptions.TraCIException as e:
        print(f"Error getting parking area list: {e}")
        return None

    for parking_area_id in parking_area_ids:
        try:
            lane_id = traci.parkingarea.getLaneID(parking_area_id)
        except traci.exceptions.TraCIException as e:
            print(f"Error getting lane ID for parking area {parking_area_id}: {e}")
            continue

        try:
            edge_id = traci.lane.getEdgeID(lane_id)
        except traci.exceptions.TraCIException as e:
            print(f"Error getting edge ID for lane {lane_id}: {e}")
            continue

        try:
            edge_pos = traci.simulation.convert2D(edge_id, pos=0)[0:2]
        except traci.exceptions.TraCIException as e:
            print(f"Error converting edge ID {edge_id} to 2D position: {e}")
            continue
        except sumolib.geomhelper.SumoException as e:
            print(f"Error converting edge ID {edge_id} to 2D position: {e}")
            continue

        try:
            distance = sumolib.geomhelper.distance(vehicle_pos, edge_pos)
        except Exception as e:  # sumolib might throw non-TraCI exceptions
            print(f"Error calculating distance for parking area {parking_area_id}: {e}")
            continue

        if distance < min_distance:
            min_distance = distance
            nearest_parking = parking_area_id

    return nearest_parking

def park_vehicle(vehicle_id):
    try:
        vehicle_pos = traci.vehicle.getPosition(vehicle_id)
        print(f"Vehicle {vehicle_id} position: {vehicle_pos}")
    except traci.exceptions.TraCIException as e:
        print(f"Error getting position for vehicle {vehicle_id}: {e}")
        return False

    try:
        nearest_parking = find_nearest_parking_area(vehicle_pos)
    except traci.exceptions.TraCIException as e:
        print(f"Error finding nearest parking area for vehicle {vehicle_id}: {e}")
        return False

    if nearest_parking:
        try:
            lane_id = traci.parkingarea.getLaneID(nearest_parking)
            edge_id = traci.lane.getEdgeID(lane_id)
            traci.vehicle.changeTarget(vehicle_id, edge_id)
        except traci.exceptions.TraCIException as e:
            print(f"Error changing target for vehicle {vehicle_id} to parking area {nearest_parking}: {e}")
            return False

        try:
            while True:
                traci.simulationStep()
                current_lane_id = traci.vehicle.getLaneID(vehicle_id)
                if current_lane_id == lane_id:
                    vehicle_count = traci.parkingarea.getVehicleCount(nearest_parking)
                    capacity = traci.parkingarea.getCapacity(nearest_parking)
                    if vehicle_count < capacity:
                        try:
                            traci.vehicle.setParkingAreaStop(vehicle_id, nearest_parking, duration=60)
                        except traci.exceptions.TraCIException as e:
                            print(f"Error setting parking area stop for vehicle {vehicle_id} at parking area {nearest_parking}: {e}")
                            return False
                        return True
                    else:
                        try:
                            nearest_parking = find_nearest_parking_area(traci.vehicle.getPosition(vehicle_id))
                        except traci.exceptions.TraCIException as e:
                            print(f"Error finding next nearest parking area for vehicle {vehicle_id}: {e}")
                            return False

                        if nearest_parking:
                            try:
                                lane_id = traci.parkingarea.getLaneID(nearest_parking)
                                edge_id = traci.lane.getEdgeID(lane_id)
                                traci.vehicle.changeTarget(vehicle_id, edge_id)
                            except traci.exceptions.TraCIException as e:
                                print(f"Error changing target for vehicle {vehicle_id} to next nearest parking area {nearest_parking}: {e}")
                                return False
                        else:
                            return False
        except traci.exceptions.TraCIException as e:
            print(f"Error during simulation step for vehicle {vehicle_id}: {e}")
            return False

    return False


def main():
    config_file = 'osm.sumocfg'
    start_simulation(config_file)

    tracked_vehicle = 'veh0'  # Change this to your target vehicle ID
    highlight_vehicle(tracked_vehicle)

    vehicle_data = {}

    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()

        vehicle_ids = traci.vehicle.getIDList()
        for vehicle_id in vehicle_ids:
            if vehicle_id not in vehicle_data:
                vehicle_data[vehicle_id] = {
                    'start_time': traci.simulation.getTime(),
                    'co2': 0,
                    'distance': 0
                }

            if park_vehicle(vehicle_id):
                end_time = traci.simulation.getTime()
                trip_time = end_time - vehicle_data[vehicle_id]['start_time']
                average_speed = traci.vehicle.getDistance(
                    vehicle_id) / trip_time
                co2_consumption = vehicle_data[vehicle_id]['co2']

                print(f"Vehicle {vehicle_id} parked")
                print(f"Trip time: {trip_time} seconds")
                print(f"Average speed: {average_speed} m/s")
                print(f"CO2 consumption: {co2_consumption} mg")

                del vehicle_data[vehicle_id]
            else:
                vehicle_data[vehicle_id]['co2'] += traci.vehicle.getCO2Emission(
                    vehicle_id)
                vehicle_data[vehicle_id]['distance'] += traci.vehicle.getDistance(
                    vehicle_id)

    traci.close()


if __name__ == '__main__':
    main()

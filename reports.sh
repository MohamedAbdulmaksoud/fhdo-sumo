#!/bin/zsh

#Run script from root folder for a specific configuration

sumo -c osm.sumocfg --vehroutes output/vehroutes.xml --emission-output output/emissions.xml --tripinfo-output output/tripinfos.xml --statistic-output output/statistics.xml --stop-output output/stopinfo.xml --summary-output output/summary.xml

python3 "$SUMO_HOME"/tools/visualization/plotXMLAttributes.py -x depart -y duration -i id ./output/tripinfos.xml -o ./output/report/trip_duration.png &&
python3 "$SUMO_HOME"/tools/visualization/plotXMLAttributes.py ./output/summary.xml -x time -y meanTravelTime -o ./output/report/mean_travel_time.png &&
python3 "$SUMO_HOME"/tools/visualization/plotXMLAttributes.py ./output/summary.xml -x time -y meanSpeed -o ./output/report/mean_speed.png &&
python3 "$SUMO_HOME"/tools/visualization/plotXMLAttributes.py ./output/summary.xml -x time -y arrived -o ./output/report/arrived.png &&
python3 ../../parkingSearchTraffic.py ../osm.net.xml ./output/vehroutes.xml

python3 compare_flow_results.py .

python3 "$SUMO_HOME"/tools/visualization/plot_summary.py \
    -i ./active_memory/output/summary.xml,./all_visible/output/summary.xml,./frustration_100/output/summary.xml,./knowledge_1/output/summary.xml,./all_visible_knowledge_1/output/summary.xml,./parkAnywhere_1_visible/output/summary.xml \
    -l active_memory,all_visible,frustration_100,knowledge_1,all_visible_knowledge_1,parkAnywhere_1_visible \
    --xlim 0,40000 \
    --ylim 0,2000 \
    -m "arrived" \
    -o reports/arrived.png \
    --yticks 0,2000,200,11 \
    --xticks 0,40000,2500,5 \
    --xtime1 \
    --ygrid \
    --ylabel "arrived vehicles [#]" \
    --xlabel "time" \
    --title "arrived vehicles over time" \
    --adjust .14,.1

python3 compare_tripinfos.py -i ./active_memory/output/tripinfos.xml ./all_visible/output/tripinfos.xml ./frustration_100/output/tripinfos.xml ./knowledge_1/output/tripinfos.xml ./all_visible_knowledge_1/output/tripinfos.xml ./parkAnywhere_1_visible/output/tripinfos.xml -l active_memory all_visible frustration_100 knowledge_1 all_visible_knowledge_1 parkAnywhere_1_visible -o reports/co2_fuel_timeLoss_comparison.png

#!/bin/sh
set -eu

while read line
do
    index=$(echo ${line} | cut -d , -f 1)
    region=$(echo ${line} | cut -d , -f 4)
    if [ $index = $BATCH_TASK_INDEX ]; then
        break
    fi
done < ${MOUNT_PATH}/index.csv

case "$region" in
    "岩見沢" ) region_no=2 ;;
    "岡山"   ) region_no=6 ;;
    "那覇"   ) region_no=8 ;;
esac

# コントロール群
python3 heat_load_calc/heat_load_calc/heat_load_calc.py ${MOUNT_PATH}/house_data_${BATCH_TASK_INDEX}.json \
-o out \
--region $region_no \
--log INFO \
2> ${MOUNT_PATH}/stderr_${BATCH_TASK_INDEX}.log
python3 aggregator.py out/result_detail_a.csv ${MOUNT_PATH}/result_summary_${BATCH_TASK_INDEX}.json

# 対照群(簡易な入力方法R5)
python3 heat_load_calc/heat_load_calc/heat_load_calc.py ${MOUNT_PATH}/new_house_data_${BATCH_TASK_INDEX}.json \
-o out \
--region $region_no \
--log INFO \
2> ${MOUNT_PATH}/new_stderr_${BATCH_TASK_INDEX}.log
python3 aggregator.py out/result_detail_a.csv ${MOUNT_PATH}/new_result_summary_${BATCH_TASK_INDEX}.json

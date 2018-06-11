#! /bin/bash
pidof robot.py # 检测程序是否运行
while [ $? -ne 0 ]    # 判断程序上次运行是否正常结束
do
    echo "Process exits with errors! Restarting!"
    python robot.py    #重启程序
done

echo "process ends!"

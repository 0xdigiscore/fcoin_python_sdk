#! /bin/bash
pidof app.py 
while [ $? -ne 0 ]   
do
    echo "Process exits with errors! Restarting!"
    python app.py   
done

echo "process ends!"

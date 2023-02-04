#!/bin/bash
pid=`ps -ef | grep -i 'nq-agent' | grep -v grep| awk '{print $2}'`
if [ "$pid" ]; then
 kill -9 $pid
fi
rm -Rf /etc/nodequery
echo -e "Uninstall completed."
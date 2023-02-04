#!/bin/bash

PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

# Prepare output
echo -e "|\n|   NodeQuery Installer\n|   ===================\n|"

# Root required
if [ $(id -u) != "0" ];
then
	echo -e "|   Error: You need to be root to install the NodeQuery agent\n|"
	echo -e "|          The agent itself will NOT be running as root but instead under its own non-privileged user\n|"
	exit 1
fi


# Attempt to delete previous agent
if [ -f /etc/nodequery/nq-agent.sh ]
then
  pid=`ps -ef | grep -i 'nq-agent' | grep -v grep| awk '{print $2}'`
  if [ "$pid" ]; then
    kill -9 $pid
  fi
  rm -Rf /etc/nodequery
fi

# Create agent dir
mkdir -p /etc/nodequery

# Download agent
echo -e "|   Downloading nq-agent.sh to /etc/nodequery\n|\n|   + $(wget -nv -o /dev/stdout -O /etc/nodequery/nq-agent.sh --no-check-certificate %agent_url%)"

if [ -f /etc/nodequery/nq-agent.sh ]
then

	chmod +x /etc/nodequery/nq-agent.sh
	nohup /etc/nq-agent.sh >/dev/null 2>&1 &

	# Show success
	echo -e "|\n|   Success: The NodeQuery agent has been installed\n|"
else
	# Show error
	echo -e "|\n|   Error: The NodeQuery agent could not be installed\n|"
fi
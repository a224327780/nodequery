#!/bin/bash

PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

# Prepare output
echo -e "|\n|   NodeQuery Installer\n|   ===================\n|"

# Root required
if [ $(id -u) != "0" ]; then
  echo -e "|   Error: You need to be root to install the NodeQuery agent\n|"
  echo -e "|          The agent itself will NOT be running as root but instead under its own non-privileged user\n|"
  exit 1
fi

apt update
if ! command -v python3 >/dev/null 2>&1; then
  apt install python3 python3-distutils -y
fi

if ! command -v pip3 >/dev/null 2>&1; then
  curl -o get-pip.py https://bootstrap.pypa.io/get-pip.py
  python3 get-pip.py && rm -f get-pip.py
fi

pip3 install websockets

# Attempt to delete previous agent
if [ -f /etc/nodequery/nq-agent.sh ]; then
  pid=$(ps -ef | grep -i 'nq-agent' | grep -v grep | awk '{print $2}')
  if [ "$pid" ]; then
    kill -9 $pid
  fi
  rm -Rf /etc/nodequery
fi

# Create agent dir
mkdir -p /etc/nodequery

# Download agent
echo -e "|   Downloading nq-agent.py to /etc/nodequery\n|\n|   + $(wget -nv -o /dev/stdout -O /etc/nodequery/nq-agent.py --no-check-certificate %agent_py_url%)"

echo -e "|   Downloading nq-agent.sh to /etc/nodequery\n|\n|   + $(wget -nv -o /dev/stdout -O /etc/nodequery/nq-agent.sh --no-check-certificate %agent_sh_url%)"

if [ -f /etc/nodequery/nq-agent.sh ]; then

  chmod +x /etc/nodequery/nq-agent.sh
  chmod +x /etc/nodequery/nq-agent.py
  nohup /etc/nodequery/nq-agent.py >/dev/null 2>&1 &

  # Show success
  echo -e "|\n|   Success: The NodeQuery agent has been installed\n|"
else
  # Show error
  echo -e "|\n|   Error: The NodeQuery agent could not be installed\n|"
fi

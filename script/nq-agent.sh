#!/bin/bash

# Set environment
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

# Prepare values
function prep() {
  echo "$1" | sed -e 's/^ *//g' -e 's/ *$//g' | sed -n '1 p'
}

# Integer values
function int() {
  echo ${1/\.*/}
}

# Filter numeric
function num() {
  case $1 in
  '' | *[!0-9\.]*) echo 0 ;;
  *) echo $1 ;;
  esac
}

while true ; do
  # System uptime
  uptime=$(prep $(int "$(uptime | awk '{print $3}')"))

  # Login session count
  sessions=$(prep "$(who | wc -l)")

  # OS details
  os_kernel=$(prep "$(uname -r)")

  if ls /etc/*release >/dev/null 2>&1; then
    os_name=$(prep "$(cat /etc/*release | grep '^PRETTY_NAME=\|^NAME=\|^DISTRIB_ID=' | awk -F\= '{ print $2 }' | tr -d '"' | tac)")
  fi

  if [ -z "$os_name" ]; then
    if [ -e /etc/redhat-release ]; then
      os_name=$(prep "$(cat /etc/redhat-release)")
    elif [ -e /etc/debian_version ]; then
      os_name=$(prep "Debian $(cat /etc/debian_version)")
    fi

    if [ -z "$os_name" ]; then
      os_name=$(prep "$(uname -s)")
    fi
  fi

  os_arch=$(prep "$(uname -m)")

  # CPU details
  cpu_cores=$(lscpu | awk '/^CPU\(s\)/{print $2}')
  cpu_name=$(prep "$(lscpu | grep 'Model name' | awk -F ': ' '{print $2}')")
  cpu_usage=$(top -bn1 | awk '/Cpu/{print $2 + $4}')

  cpu_freq=$(prep "$(cat /proc/cpuinfo | grep 'cpu MHz' | awk -F\: '{ print $2 }')")

  if [ -z "$cpu_freq" ]; then
    cpu_freq=$(prep $(num "$(lscpu | grep 'CPU MHz' | awk -F\: '{ print $2 }' | sed -e 's/^ *//g' -e 's/ *$//g')"))
  fi

  # RAM usage
  ram_total=$(prep $(num "$(cat /proc/meminfo | grep ^MemTotal: | awk '{ print $2 }')"))
  ram_free=$(prep $(num "$(cat /proc/meminfo | grep ^MemFree: | awk '{ print $2 }')"))
  ram_cached=$(prep $(num "$(cat /proc/meminfo | grep ^Cached: | awk '{ print $2 }')"))
  ram_buffers=$(prep $(num "$(cat /proc/meminfo | grep ^Buffers: | awk '{ print $2 }')"))
  ram_usage=$((($ram_total - ($ram_free + $ram_cached + $ram_buffers)) * 1024))
  ram_total=$(($ram_total * 1024))

  # Swap usage
  swap_total=$(prep $(num "$(cat /proc/meminfo | grep ^SwapTotal: | awk '{ print $2 }')"))
  swap_free=$(prep $(num "$(cat /proc/meminfo | grep ^SwapFree: | awk '{ print $2 }')"))
  swap_usage=$((($swap_total - $swap_free) * 1024))
  swap_total=$(($swap_total * 1024))

  # Disk usage
  disk_total=$(prep $(num "$(($(df -P -B 1 | grep '^/' | awk '{ print $2 }' | sed -e :a -e '$!N;s/\n/+/;ta')))"))
  disk_usage=$(prep $(num "$(($(df -P -B 1 | grep '^/' | awk '{ print $3 }' | sed -e :a -e '$!N;s/\n/+/;ta')))"))

  # 获取进程列表
  process_list=$(ps aux --sort=-%cpu | head -n 11 | awk '{print $2,$3,$4,$11}' | sed '1d')

  # Network interface
  nic=$(prep "$(ip route get 1.1.1.1 | grep dev | awk -F'dev' '{ print $2 }' | awk '{ print $1 }')")

  if [ -z $nic ]; then
    nic=$(prep "$(ip link show | grep 'eth[0-9]' | awk '{ print $2 }' | tr -d ':')")
  fi

  # IP addresses and network usage
  #ipv4=$(prep "$(ip addr show $nic | grep 'inet ' | awk '{ print $2 }' | awk -F\/ '{ print $1 }' | grep -v '^127' | awk '{ print $0 } END { if (!NR) print "N/A" }')")
  # dhclient -6 $nic
  ipv6=$(prep "$(ip addr show $nic | grep 'inet6 ' | awk '{ print $2 }' | awk -F\/ '{ print $1 }' | grep -v '^::' | grep -v '^0000:' | grep -v '^fe80:' | awk '{ print $0 } END { if (!NR) print "N/A" }')")

  if [ -d /sys/class/net/$nic/statistics ]; then
    rx=$(prep $(num "$(cat /sys/class/net/$nic/statistics/rx_bytes)"))
    tx=$(prep $(num "$(cat /sys/class/net/$nic/statistics/tx_bytes)"))
  else
    rx=$(prep $(num "$(ip -s link show $nic | grep '[0-9]*' | grep -v '[A-Za-z]' | awk '{ print $1 }' | sed -n '1 p')"))
    tx=$(prep $(num "$(ip -s link show $nic | grep '[0-9]*' | grep -v '[A-Za-z]' | awk '{ print $1 }' | sed -n '2 p')"))
  fi

  # Detailed system load calculation
  if [ -e /etc/nodequery/nq-data.log ]; then
    data=($(cat /etc/nodequery/nq-data.log))
    ipv4=${data[2]}

    if [[ $rx -gt ${data[0]} ]]; then
      rx_gap=$(($rx - ${data[0]}))
    fi

    if [[ $tx -gt ${data[1]} ]]; then
      tx_gap=$(($tx - ${data[1]}))
    fi
  else
    ipv4=$(curl -s https://ipv4.icanhazip.com/)
  fi

  # System load cache
  echo "$rx $tx $ipv4" >/etc/nodequery/nq-data.log

  # Prepare load variables
  rx_gap=$(prep $(num "$rx_gap"))
  tx_gap=$(prep $(num "$tx_gap"))

  # Build data for post
  data_post="token=%TOKEN%&uptime=$uptime&sessions=$sessions&os_kernel=$os_kernel&os_name=$os_name&os_arch=$os_arch&cpu_name=$cpu_name&cpu_cores=$cpu_cores&cpu_freq=$cpu_freq&ram_total=$ram_total&ram_usage=$ram_usage&swap_total=$swap_total&swap_usage=$swap_usage&disk_total=$disk_total&disk_usage=$disk_usage&nic=$nic&ipv4=$ipv4&ipv6=$ipv6&rx=$rx&tx=$tx&rx_gap=$rx_gap&tx_gap=$tx_gap&cpu_usage=$cpu_usage&process_list=$process_list"

  curl -s -d "$data_post" "%AGENT_API%"
  sleep 5
done
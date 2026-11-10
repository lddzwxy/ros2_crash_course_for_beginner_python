#!/usr/bin/env bash
# 环境检查脚本：确认 Ubuntu / ROS2 Jazzy / Python / Gazebo 就绪
# 用法：bash check_env.sh

set -e
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

pass=0
fail=0

check() {
  local desc="$1"
  local cmd="$2"
  local expect="$3"
  echo -n "检查 ${desc} ... "
  if out=$(eval "$cmd" 2>/dev/null); then
    if [[ -z "$expect" ]] || echo "$out" | grep -qi "$expect"; then
      echo -e "${GREEN}通过${NC}  (${out})"
      pass=$((pass+1))
    else
      echo -e "${YELLOW}警告${NC}  期望含 '${expect}'，实际: ${out}"
      fail=$((fail+1))
    fi
  else
    echo -e "${RED}失败${NC}  命令: ${cmd}"
    fail=$((fail+1))
  fi
}

echo "========== ROS2 Jazzy 环境检查 =========="
check "Ubuntu 版本"          "lsb_release -ds"                "24.04"
check "Python 版本"          "python3 --version"              "3.12"
check "ROS 发行版"           "printenv ROS_DISTRO"            "jazzy"
check "ros2 命令"            "ros2 --help >/dev/null && echo ros2-ok"  "ros2-ok"
check "colcon"               "colcon --help >/dev/null && echo colcon-ok" "colcon-ok"
check "rosdep"               "rosdep --help >/dev/null && echo rosdep-ok" "rosdep-ok"
echo "----- 可选：仿真工具 -----"
check "Gazebo Harmonic(gz)"  "gz sim --version"               ""
check "ros_gz"               "ros2 pkg prefix ros_gz_sim"     ""
echo "----------------------------------------"
echo "通过 ${pass} 项，失败/警告 ${fail} 项"
if [[ $fail -eq 0 ]]; then
  echo -e "${GREEN}环境就绪，可以开始课程！${NC}"
else
  echo -e "${YELLOW}请根据上方提示修复后再继续。${NC}"
fi

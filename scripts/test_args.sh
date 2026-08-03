#！/bin/bash


read -p "输入颜色:" COLOR  # 需要用户在终端输入，读取输入内容后执行下方 case 语句
case "${COLOR}" in
  red) echo "输入颜色为红色";;
  blue) echo "输入颜色为蓝色";;
  *) echo "输入未知颜色";;
esac
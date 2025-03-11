#!/bin/bash

GID="$1";
FileNum="$2";
File="$3";
MinSize="1"  #限制最低上传大小，默认1k
MaxSize="8388608"  #限制最高文件大小(单位k)，默认8G
#RemoteDIR="/RATS/";  #rclone挂载的本地文件夹，最后面保留/
LocalDIR="/opt/test/app/assets/";  #Aria2下载目录，最后面保留/

if [[ -z $(echo "$FileNum" |grep -o '[0-9]*' |head -n1) ]]; then FileNum='0'; fi
if [[ "$FileNum" -le '0' ]]; then exit 0; fi
if [[ "$#" != '3' ]]; then exit 0; fi

function LoadFile(){
  IFS_BAK=$IFS
  IFS=$'\n'
  echo "$LocalDIR" "$GID" "$FileNum" "$File"
  if [[ ! -d "$LocalDIR" ]]; then return; fi
  if [[ -e "$File" ]]; then
    FileLoad="${File/#$LocalDIR}"
    while true
      do
        if [[ "$FileLoad" == '/' ]]; then return; fi
        echo "$FileLoad" |grep -q '/';
        if [[ "$?" == "0" ]]; then
          FileLoad=$(dirname "$FileLoad");
        else
          break;
        fi;
      done;
    if [[ "$FileLoad" == "$LocalDIR" ]]; then return; fi
    EXEC="$(command -v python3)"
    if [[ -z "$EXEC" ]]; then return; fi
    Option=" /opt/test/app/upload.py upload";
    cd "$LocalDIR";
    if [[ -e "$FileLoad" ]]; then
      ItemSize=$(du -s "$FileLoad" |cut -f1 |grep -o '[0-9]*' |head -n1)
      if [[ -z "$ItemSize" ]]; then return; fi
      if [[ "$ItemSize" -le "$MinSize" ]]; then
        echo -ne "\033[33m$FileLoad \033[0mtoo small to spik.\n";
        return;
      fi
      if [[ "$ItemSize" -ge "$MaxSize" ]]; then
        echo -ne "\033[33m$FileLoad \033[0mtoo large to spik.\n";
        return;
      fi
      #eval "${EXEC}${Option}" \'"${FileLoad}"\' "${RemoteDIR}";
      eval "${EXEC}${Option}" \'"${FileLoad}"\';
      rm -rf "${FileLoad}"
    fi
  fi
  IFS=$IFS_BAK
}
LoadFile;
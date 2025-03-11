#!/bin/python
# coding: utf-8
import platform

plat = platform.system().lower()
if plat == 'windows':
    from .server import windows as myos
else:
    from .server import linux as myos


class system:
    def __init__(self):
        self.isWindows = self._isWindows()

    def _isWindows(self):
        plat = platform.system().lower()
        if plat == 'windows':
            return True
        return False

    def GetSystemAllInfo(self, isCache=False):
        """
        获取系统所有信息
        """
        data = {}
        data['mem'] = self.GetMemInfo()
        # data['load_average'] = self.GetLoadAverage()
        data['network'] = self.GetNetWork()
        data['infocpu'] = self.GetCpuInfo(1)
        data['usedcpu'] = self.GetCpuUse(1)
        data['disk'] = self.GetDiskInfo()
        data['time'] = self.GetBootTime()
        data['system'] = self.GetSystemVersion()
        data['os'] = self.GetOSInfo()
        data['is_windows'] = self.isWindows
        return data

    def GetMemInfo(self):
        memInfo = myos.GetMemInfo()
        return memInfo

    def GetLoadAverage(self):
        data = myos.GetLoadAverage()
        return data

    def GetNetWork(self):
        data = myos.GetNetWork()
        return data

    def GetCpuInfo(self, interval=1):
        data = myos.GetCpuInfo(interval)
        return data

    def GetCpuUse(self, interval=1):
        data = myos.GetCpuUsed(interval)
        return data

    def GetBootTime(self):
        data = myos.GetBootTime()
        return data

    def GetDiskInfo(self):
        data = myos.GetDiskInfo()
        return data

    def GetSystemVersion(self):
        data = myos.GetSystemVersion()
        return data

    def GetOSInfo(self):
        data = myos.getOsInfo()
        return data


if __name__ == '__main__':
    qs = system().GetSystemAllInfo()
    print(qs)

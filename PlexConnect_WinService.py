"""
PlexConnect_WinService
Starter script to run PlexConnect as a Windows Service

prerequisites:
http://sourceforge.net/projects/pywin32/

usage:
python PlexConnect_WinService.py <command>
with <command> = install, start, stop or remove

sources:
http://stackoverflow.com/questions/32404/can-i-run-a-python-script-as-a-service-in-windows-how
http://code.activestate.com/recipes/551780/
http://docs.activestate.com/activepython/2.4/pywin32/win32service.html
...and others
"""

import win32serviceutil
import win32service

import PlexConnect



class AppServerSvc(win32serviceutil.ServiceFramework):
    _svc_name_ = "PlexConnect-Service"
    _svc_display_name_ = "PlexConnect-Service"
    _svc_description_ = "Description"
    
    def __init__(self,args):
        win32serviceutil.ServiceFramework.__init__(self,args)
    
    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        PlexConnect.cmdShutdown()
    
    def SvcDoRun(self):
        self.ReportServiceStatus(win32service.SERVICE_RUNNING)
        running = PlexConnect.startup()
        
        while running:
            running = PlexConnect.run(timeout=10)
        
        PlexConnect.shutdown()
        
        self.ReportServiceStatus(win32service.SERVICE_STOPPED)



if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(AppServerSvc)

import win32serviceutil
import win32service
import win32event
import servicemanager
import psutil
import time

BLOCKED_APPS = ["Discord.exe", "FortniteClient-Win64-Shipping.exe"]
BLOCKED_SITES = [
    "www.twitch.tv",
    "www.youtube.com"
]
HOSTS_PATH = r"C:\Windows\System32\drivers\etc\hosts"
REDIRECT_IP = "127.0.0.1"

class ProductivityService(win32serviceutil.ServiceFramework):
    _svc_name_ = "pyDuctive"
    _svc_display_name_ = "Productivity Blocker Service"
    _svc_description_ = "Blocks distracting websites and apps during work hours."

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.running = True

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.running = False

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, ""))
        self.main()

    def block_apps(self):
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'] in BLOCKED_APPS:
                proc.terminate()

    def block_websites(self):
        with open(HOSTS_PATH, 'r+') as file:
            content = file.read()
            for site in BLOCKED_SITES:
                if site not in content:
                    file.write(f"{REDIRECT_IP} {site}\n")

    def unblock_websites(self):
        with open(HOSTS_PATH, 'r+') as file:
            lines = file.readlines()
        with open(HOSTS_PATH, 'w') as file:
            for line in lines:
                if not any(site in line for site in BLOCKED_SITES):
                    file.write(line)

    def main(self):
        # Make sure to unblock websites if service is stopped
        while self.running:
            self.block_apps()
            self.block_websites()
            time.sleep(5)

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(ProductivityService)


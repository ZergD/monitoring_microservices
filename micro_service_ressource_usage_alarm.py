"""
@Author: Marc Mozgawa
@Date 11/07/21

This file starts the Alarm agent/microservice
"""
import json

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from timeloop import Timeloop
from datetime import timedelta, datetime
import click
import psutil
import time
import requests
import pprint
import socket
import os

REST_API_ADDRESS = "http://127.0.0.1:8000/ressources-usage/save-all"

tl = Timeloop()

# example
DDD = {'AdAppMgrSvc.exe': [0.13514532373320998, 0.0],
       'AdAppMgrUpdater.exe': [0.07299209258131334, 0.0],
       'AdobeIPCBroker.exe': [0.059472701899789704, 0.0],
       'ApplicationFrameHost.exe': [0.19706095702624085, 0.0],
       'CCXProcess.exe': [0.019167113540381232, 0.0],
       'CompPkgSrv.exe': [0.0492088611277907, 0.0],
       'Docker Desktop.exe': [0.3798358694455471, 0.0],
       'FNPLicensingService64.exe': [0.053708476326818896, 0.0],
       'FileCoAuth.exe': [0.12237280729776481, 0.0],
       'GameBar.exe': [0.01887996577198601, 0.0],
       'GameBarFTServer.exe': [0.08011519420977063, 0.0],
       'GamingServices.exe': [0.14242480971027982, 0.0],
       'GamingServicesNet.exe': [0.017755303679104713, 0.0],
       'GoogleCrashHandler.exe': [0.006556540711690959, 0.0],
       'GoogleCrashHandler64.exe': [0.006365108866094141, 0.0],
       'HPNetworkCommunicator.exe': [0.06234247252893193, 0.0],
       'LocationNotificationWindows.exe': [0.011557697677907784, 0.0],
       'LsaIso.exe': [0.012897720597085499, 0.0],
       'MemCompression': [4.087729146910302, 0.0],
       'Microsoft.Notes.exe': [0.6318108964103862, 0.0],
       'Microsoft.Photos.exe': [0.07102767554120774, 0.0],
       'MicrosoftEdgeUpdate.exe': [0.06286143229785454, 0.0],
       'MoUsoCoreWorker.exe': [1.4066948023621733, 0.0],
       'MsMpEng.exe': [1.2125612153178338, 0.0],
       'NVDisplay.Container.exe': [0.15322688311028537, 0.0],
       'NVIDIA Share.exe': [0.28936518727338756, 0.0],
       'NVIDIA Web Helper.exe': [0.05750061550051643, 0.0],
       'NisSrv.exe': [0.05483434695407896, 0.0],
       'OriginWebHelperService.exe': [0.0950877870550436, 0.0],
       'PnkBstrA.exe': [0.03740099683347799, 0.0],
       'Registry': [0.5508410677781199, 0.0],
       'RuntimeBroker.exe': [0.12999761969562865, 0.0],
       'ScanToPCActivationApp.exe': [0.08592703603726488, 0.0],
       'SearchApp.exe': [0.5725563784732018, 0.0],
       'SearchFilterHost.exe': [0.0444817997586784, 0.0],
       'SearchIndexer.exe': [0.3115959354639451, 0.0],
       'SearchProtocolHost.exe': [0.05026608700233675, 0.0],
       'SecurityHealthService.exe': [0.07716806227370752, 0.0],
       'SecurityHealthSystray.exe': [0.053235697677844945, 0.0],
       'SettingSyncHost.exe': [0.09098803479178078, 0.0],
       'SgrmBroker.exe': [0.05243055032109103, 0.0],
       'ShellExperienceHost.exe': [0.3782453979186094, 0.0],
       'Spotify.exe': [0.40931299062831283, 0.0],
       'StartMenuExperienceHost.exe': [0.4140006126350814, 0.0],
       'System': [0.027009119095254813, 0.0],
       'System Idle Process': [4.7857961399204075e-05, 0.0],
       'SystemSettings.exe': [0.019348635404072154, 0.0],
       'Taskmgr.exe': [0.328953873039311, 0.0],
       'TextInputHost.exe': [0.2821712655303345, 0.0],
       'TiWorker.exe': [0.17739989131456968, 0.0],
       'Time.exe': [0.23206325482474055, 0.0],
       'TrustedInstaller.exe': [0.045024770084371196, 0.0],
       'UserOOBEBroker.exe': [0.05711751010244705, 0.0],
       'Video.UI.exe': [0.015649553377539732, 0.0],
       'WUDFHost.exe': [0.027853333534336774, 0.0],
       'WmiPrvSE.exe': [0.05626899811511419, 0.0],
       'YourPhone.exe': [0.07280057372124125, 0.0],
       'armsvc.exe': [0.03314163826894882, 0.0],
       'audiodg.exe': [0.07647218817841304, 0.0],
       'backgroundTaskHost.exe': [0.18960127857329673, 0.0],
       'bash.exe': [0.040774983112121875, 0.0],
       'chrome.exe': [0.4319238863418123, 0.0],
       'cmd.exe': [0.03567008009298991, 0.0],
       'com.docker.backend.exe': [0.18616698642915233, 0.0],
       'com.docker.cli.exe': [0.13043155624226413, 0.0],
       'com.docker.dev-envs.exe': [0.07358935027130037, 0.0],
       'com.docker.proxy.exe': [0.09745959620009431, 0.0],
       'com.docker.service': [0.2630205880575045, 0.0],
       'conhost.exe': [0.04830322709046052, 0.0],
       'csrss.exe': [0.028896996027549915, 0.0],
       'ctfmon.exe': [0.12285839641115372, 0.0],
       'dllhost.exe': [0.0501492817490804, 0.0],
       'docker.exe': [0.13618587183332903, 0.0],
       'dwm.exe': [0.43975843215404137, 0.0],
       'explorer.exe': [1.056200795685983, 0.0],
       'firefox.exe': [0.8536535599729709, 0.0],
       'fontdrvhost.exe': [0.019071995842100314, 0.0],
       'fsnotifier64.exe': [0.014285601477662417, 0.0],
       'git-bash.exe': [0.026154375904665027, 0.0],
       'gitkraken.exe': [0.5489781187223467, 0.0],
       'hpwuschd2.exe': [0.034621609469187846, 0.0],
       'java.exe': [0.4528264715011266, 0.0],
       'jcef_helper.exe': [0.20533827711856087, 0.0],
       'jenkins.exe': [0.0964905933351983, 0.0],
       'jhi_service.exe': [0.024263986429396468, 0.0],
       'jusched.exe': [0.08919708835933475, 0.0],
       'lsass.exe': [0.13844997156040645, 0.0],
       'mintty.exe': [0.09918900889611099, 0.0],
       'node.exe': [0.28639678513225814, 0.0],
       'notepad++.exe': [0.1377680850420118, 0.0],
       'null': [0.2340493602228075, 0.0],
       'nvcontainer.exe': [0.18089715199311296, 0.0],
       'nvsphelper64.exe': [0.0696954525029106, 0.0],
       'powershell.exe': [0.2996855874543129, 0.0],
       'pycharm64.exe': [10.535138370309808, 0.0],
       'python.exe': [0.15805316725409962, 0.0],
       'rundll32.exe': [0.03271091661635599, 0.0],
       'services.exe': [0.06710882637203391, 0.0],
       'sihost.exe': [0.16891588329286955, 0.0],
       'smss.exe': [0.006460824788892549, 0.0],
       'spoolsv.exe': [0.08656417536175126, 0.0],
       'sppsvc.exe': [0.07343804176707865, 0.0],
       'svchost.exe': [0.07112463192036195, 0.0],
       'taskhostw.exe': [0.1262625960492668, 0.0],
       'vmcompute.exe': [0.06468649565581319, 0.0],
       'vmmem': [82.999205318550967, 0.0],
       'vmms.exe': [0.17328626024250107, 0.0],
       'vmwp.exe': [0.08414130563919761, 0.0],
       'vpnkit-bridge.exe': [0.07925469839553792, 0.0],
       'vpnkit.exe': [0.0704577959890373, 0.0],
       'wininit.exe': [0.02537859835038393, 0.0],
       'winlogon.exe': [0.060598707882900185, 0.0],
       'wsl.exe': [0.03632932034071724, 0.0],
       'wslhost.exe': [0.031428566596423756, 0.0]}


@click.command()
@click.option("--debug", is_flag=True, help="Allows to see the full logs")
def run(debug):
    if debug:
        print("Debug is True")
    else:
        print("Debug is False")

    start_process()


@tl.job(interval=timedelta(seconds=10))
def start_monitoring_all_processes_from_DB():
    """
    Function gets started by tl.start()
    It is run as a thread every 10secs

    Every 10 seconds:
       - gets all information about all mem and cpu usage
       - if a mem or cpu usage is > 80% then:
           - For the moment it just prints out the information on the console.
           - print alarm msg ?

           Optionnal for later ?
           - post alarm msg to server
           - Send a POST request to monitoring_REST_server to tell him alarm ? And do somth with it ?
    """
    print("Starting micro service ressource usage Alarm...")
    response = requests.get("http://127.0.0.1:8000/ressources-usage/get-all")
    print(response)
    print("------------------")

    json_response = response.json()
    dict_json_response = json.loads(json_response)

    # parse all data and check if cpu_usage or mem_usage > 80%
    for key in dict_json_response.keys():
        # [0] mem_usage should always be first ?
        if DDD[key][0] > 80.0 or DDD[key][1] > 80.0:
            print("ALERTE SERVICE ALARM ROUGE - Le process {} est en sur-utilisation.".format(key))

    # here we could get the detailed version ("http://127.0.0.1:8000/ressources-usage/get-all-detailed")
    # we would have more history about the usage
    # Compute some prediction. And based on those prediction.
    # loop through all of them, and if cpu_usage or mem_usage > 80%
    # Then => print message in AMBER this time.
    pass


def start_process():
    """
    Starts the periodic "start_monitoring_specific_processes" calls with tl.start()
    """
    # while This run. If False. Then stop looping.
    bool_agent_power_status = True

    # will automatically shut down the jobs gracefully when the program is killed with block=True
    # This start the functions using the decorator tl.job()
    tl.start()
    while bool_agent_power_status:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            tl.stop()
            break


if __name__ == '__main__':
    run()

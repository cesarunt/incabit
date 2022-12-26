import psutil
from flask import render_template
from setting.config import cfg

global limitUsePercentCPU

limitUsePercentCPU = cfg.PROCESS.LIMIT_CPU


# Validate the processing previous to clic Process button
def get_viewProcess_CPU():
    process = True
    # Validate if server is processing by process limit
    percentAverage, percentTotal = get_useProcess_CPU()

    if (percentAverage>limitUsePercentCPU or percentTotal>limitUsePercentCPU):
        process = False
    
    return process

# Validate the processing when select the service (MASK, DISTANCE, ANALYTICS)
def get_viewService_CPU(service):
    # Validate if server is processing by process limit
    percentAverage, percentTotal = get_useProcess_CPU()

    if (percentAverage>limitUsePercentCPU or percentTotal>limitUsePercentCPU):
        process = "active"
        viewService = render_template(template_name_or_list=service, active = process, active_image="active show", active_video="", active_stream="")
    else:
        viewService = render_template(template_name_or_list=service, active_image="active show", active_video="", active_stream="")

    return viewService

def get_useProcess_CPU():
    # CPU usage
    sum_cpu = 0
    percentAverage = 0
    for i, percentage in enumerate(psutil.cpu_percent(percpu=True, interval=1)):
        # print(f"Core {i}: {percentage}%")
        sum_cpu += percentage
    # print(f"Total CPU Usage: {psutil.cpu_percent()}%")
    percentAverage = round(sum_cpu / psutil.cpu_count(), 2)
    percentTotal = round(psutil.cpu_percent(), 2)
    print('\nCalculate Percentage: ( Average %s , Total %s )'%(percentAverage, percentTotal))
   
    return percentAverage, percentTotal

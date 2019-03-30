# -*- coding: utf-8 -*-
"""
celery 任务示例

本地启动celery命令: python  manage.py  celery  worker  --settings=settings
周期性任务还需要启动celery调度命令：python  manage.py  celerybeat --settings=settings
"""
import base64
import datetime
import json
import time

import requests
from celery import task
from celery.schedules import crontab
from celery.task import periodic_task

from blueking.component.shortcuts import get_client_by_user
from common.log import logger
from conf.default import BK_PAAS_HOST, APP_ID, APP_TOKEN
from home_application.common_esb import fast_execute_script, get_job_instance_log
from home_application.models import JobHistory, HostInfo, HostPerformance


@task()
def async_task(x, y):
    """
    定义一个 celery 异步任务
    """
    # import time
    # time.sleep(20)
    # logger.error(u"celery 定时任务执行成功，执行结果：{:0>2}:{:0>2}".format(x, y))
    # return x + y
    pass


def execute_task():
    """
    执行 celery 异步任务

    调用celery任务方法:
        task.delay(arg1, arg2, kwarg1='x', kwarg2='y')
        task.apply_async(args=[arg1, arg2], kwargs={'kwarg1': 'x', 'kwarg2': 'y'})
        delay(): 简便方法，类似调用普通函数
        apply_async(): 设置celery的额外执行选项时必须使用该方法，如定时（eta）等
                      详见 ：http://celery.readthedocs.org/en/latest/userguide/calling.html
    """
    # now = datetime.datetime.now()
    # logger.error(u"celery 定时任务启动，将在60s后执行，当前时间：{}".format(now))
    # 调用定时任务
    # async_task.apply_async(args=[now.hour, now.minute], eta=now + datetime.timedelta(seconds=60))
    pass


@periodic_task(run_every=crontab(minute='*/5', hour='*', day_of_week="*"))
def get_time():
    """
    celery 周期任务示例

    run_every=crontab(minute='*/5', hour='*', day_of_week="*")：每 5 分钟执行一次任务
    periodic_task：程序运行时自动触发周期任务
    """
    # execute_task()
    # now = datetime.datetime.now()
    # logger.error(u"celery 周期任务调用成功，当前时间：{}".format(now))
    pass


@periodic_task(run_every=crontab(minute='*/1', hour='*', day_of_week='*'))
def get_job_instance_status():
    logger.info(u"已启动作业状态查询")
    all_history = JobHistory.objects.all()
    for obj in all_history:
        if obj.job_status not in [3, 4]:
            url_status = BK_PAAS_HOST + '/api/c/compapi/v2/job/get_job_instance_status/'
            url_log = BK_PAAS_HOST + '/api/c/compapi/v2/job/get_job_instance_log/'
            params = {
                "bk_app_code": APP_ID,
                "bk_app_secret": APP_TOKEN,
                "bk_username": "admin",
                "bk_biz_id": obj.bk_biz_id,
                "job_instance_id": obj.job_instance_id
            }
            response_status = requests.post(url_status, json.dumps(params), verify=False)
            response_log = requests.post(url_log, json.dumps(params), verify=False)
            data_status = json.loads(response_status.content)
            data_log = json.loads(response_log.content)
            if data_status['result']:
                history_obj = JobHistory.objects.get(bk_biz_id=obj.bk_biz_id, job_instance_id=obj.job_instance_id)
                history_obj.job_status = data_status['data']['job_instance']['status']
                if data_log['result']:
                    history_obj.job_log = json.dumps(data_log['data'])
                    history_obj.save()


@periodic_task(run_every=crontab(minute='*/1', hour='*', day_of_week='*'))
def get_performance():
    host_info_list = HostInfo.objects.filter(is_delete=False)

    ip_list = []
    if not host_info_list:
        return
    else:
        username = host_info_list[0].last_user
        bk_biz_id = host_info_list[0].bk_biz_id

    for host_info in host_info_list:
        ip_list.append({
            'ip': host_info.bk_host_innerip,
            'bk_cloud_id': host_info.bk_cloud_id
        })

    client = get_client_by_user(username)
    script_content = '''#!/bin/bash
        cat /proc/loadavg
        '''

    data = {
        'ip_list': ip_list,
        'bk_biz_id': bk_biz_id
    }
    res = fast_execute_script(client, 'admin', data, base64.b64encode(script_content))
    time.sleep(5)
    if res['data']:
        params = {}
        params.update({'bk_biz_id': data['bk_biz_id'], 'job_instance_id': res['data']['job_instance_id']})
        res = get_job_instance_log(client, 'admin', params)

        for i in range(5):
            if res['data'][0]['status'] != 3:
                time.sleep(2)
                res = get_job_instance_log(client, 'admin', params)
            else:
                break

        if res['data'][0]['status'] == 3:
            # 处理性能数据
            try:
                pfm_data = res['data'][0]['step_results'][0]['ip_logs']
            except KeyError:
                pfm_data = []
            for item in pfm_data:
                result = item['log_content'].split(' ')
                load_5 = result[1]
                mem = result[1]
                disk = result[2]
                cpu = result[3]
                ip = item['ip']
                host_info = HostInfo.objects.get(bk_host_innerip=ip)
                host_pfm = HostPerformance.objects.create(
                    bk_host_innerip=host_info,
                    check_time=datetime.datetime.strptime(check_time, "%Y-%m-%d %H:%M:%S"),
                    mem=mem,
                    disk=disk,
                    cpu=cpu
                )
            now = datetime.datetime.now()
            logger.info(u"主机{}完成一条性能查询：{}".format(host_pfm.bk_host_innerip, now))

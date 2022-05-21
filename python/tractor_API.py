import os
import sys
import time
import tractor.api.query as tq

tq.setEngineClientParam(hostname='123.456.78.09', port=00, user="user", debug=False)

def nimby_ON():

    nimby_ON_blades = tq.blades("nimby", columns=["profile", "ipaddr", "name", "nimby", "heartbeattime"])

    nimby_ON_list = []

    for nb_blade in nimby_ON_blades:
        if nb_blade['profile'] == 'user':
            tm = time.mktime(time.strptime(nb_blade['heartbeattime'].split('.')[0], '%Y-%m-%d %H:%M:%S'))
            if int(time.time()) - int(tm) < 1000:
                nimby_ON_list.append((nb_blade['name'], nb_blade['ipaddr']))

    return nimby_ON_list

def nimby_OFF():

    nimby_OFF_blades = tq.blades("not nimby", columns=["profile", "ipaddr", "name", "nimby"])

    nimby_OFF_list = []

    for notnb_blade in nimby_OFF_blades:
        if notnb_blade['profile'] == 'user':
            nimby_OFF_list.append((notnb_blade['name'], notnb_blade['ipaddr']))

    return nimby_OFF_list

def retry_blade(host):
    blade_ID = {}
    jid = {}
    tid = {}

    for blade in tq.blades("name=" + host, columns=['bladeid']):
        blade_ID[host] = blade['bladeid']

    for invocation in tq.invocations('active', columns=['bladeid', 'jid', 'tid']):
        if invocation['bladeid'] == blade_ID[host]:
            jid[host] = invocation['jid']
            tid[host] = invocation['tid']

    if jid.get(host) is not None:
        for job in tq.jobs('active'):
            if jid[host] == job['jid']:
                job_name = job['spoolfile'].split('/')[-1].split('.')[0]

        command = "rsh {h} ps ax|grep {j}|grep -v grep|awk '{{print $1}}'".format(h=host, j=job_name)
        command_mantra = "rsh {h} ps ax|grep mantra|grep -v grep|awk '{{print $1}}'".format(h=host)
        pid = ' '.join(os.popen(command).read().strip().split('\n'))
        pid_mantra = ' '.join(os.popen(command_mantra).read().strip().split('\n'))
        os.system("rsh {h} kill -9 {p} {m}".format(h=host, p=pid, m=pid_mantra))
        tq.retry({"jid": jid[host], "tid": tid[host]})

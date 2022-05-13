import os
import sys
import getopt
sys.path.append('/core/Linux/APPZ/renderFam/tractor/pixar/Tractor-2.2/lib/python2.7/site-packages')
import tractor.api.query as tq


class bcolors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def help():
    print "usage: yslow [options]"
    print "\n"
    print "\033[93mOptions:\033[0m"
    print " -h, --help        Show this help message"
    print " -a, --all         Execute all of cleaning options"
    print " -c, --check       Check system status"
    print " -m, --memory      Drop the cache memory"
    print " -k, --kill        Kill process by name"
    print "                   (nuke, rv, argos, clarisse)"
    print "\n"
    print "\033[93mExample:\033[0m"
    print " yslow -a             # clean up all VFX programs and cache memory"
    print " yslow -c             # show system status check"
    print " yslow -k nuke -m     # kill Nuke process and drop cache memory"
    print " yslow -k clarisse    # kill clarisse process"
    print " yslow -k 12345       # kill Tractor Farm Job ID"
    print "\n"
    return


def check():
    os.system("""
    RUNNING=$(top -b -n1 | awk '{print $3,$4,$5,$6}' | head -n 1 | tail -n +1)
    USED=$(top -b -n1 | awk '{print $2}' | head -n 3 | tail -n +3)
    USED=$(top -b -n1 | awk '{print $2}' | head -n 3 | tail -n +3)
    USED=$(echo $USED | cut -d'%' -f 1)
    FREE=$(top -b -n1 | awk '{print $5}' | head -n 3 | tail -n +3)
    FREE=$(echo $FREE | cut -d'%' -f 1)
    USING=$(echo $USED | cut -d'%' -f 1)
    USING_ROUNDUP=$(echo $USED | awk '{printf "%.0f", $1+$2}')

    echo "    __    __   _______   _______    "
    echo "   |  \  /  | |   _   | |_____  |   "
    echo "   |   \/   | |  |_|  |  _____| |   "
    echo "   |        | |   _   | |_____  |   "
    echo "   |  |\/|  | |  |_|  |  _____| |   "
    echo "   |__|  |__| |_______| |_______|   "
    echo "                                    "
    echo "\33[93m\033[1m  PC RUNNING: $RUNNING\33[0m"
    echo " "
    echo "\33[92m  CPU\33[0m $USED% used"
    """)
    # print "{c}  Memory status:{e}".format(c=bcolors.GREEN, e=bcolors.ENDC)
    os.system("""TOTAL=`free | awk '/^Mem:/    {{ print $2 }}'`
    USED=`free | awk '/^Mem:/    {{ print $3 }}'`
    FREE=`free | awk '/^Mem:/    {{ print $4 }}'`
    USING=$(($USED*100/$TOTAL))
    echo "\33[92m  Memory\33[0m $(echo "scale=2; $USED / 1024^2" | bc) GB of $(echo "scale=2; $TOTAL / 1024^2" | bc) GB used"


    # progress bar
    #for ((i=1; i <= $USING; i++))
    #do
    #    output="\r"

    #    output="$output["
    #    total=$(($i/2))
    #    count=0

    #    while [ $count -lt $total ]; do
    #        output="$output#"
    #        let count=$count+1
    #    done

    #    let total=50-$total
    #    count=0

    #    while [ $count -lt $total ]; do
    #        output="$output "
    #        let count=$count+1
    #    done

    #    output="$output] $i% using..."
    #    echo -ne "$output"

    #    sleep .02
    #done
    """)
    print "\n"
    print "{c}  Running 'Houdini':{e}".format(c=bcolors.GREEN, e=bcolors.ENDC)
    os.system("ps ax|grep /opt/hfs | grep -v 0:00")
    print "\n"
    print "{c}  Running 'Katana':{e}".format(c=bcolors.GREEN, e=bcolors.ENDC)
    os.system("ps ax|grep /opt/Katana | grep -v 0:00")
    print "\n"
    print "{c}  Running 'Maya':{e}".format(c=bcolors.GREEN, e=bcolors.ENDC)
    os.system("ps ax|grep /usr/autodesk/maya | grep -v 0:00")
    print "\n"
    print "{c}  Running 'clarisse':{e}".format(c=bcolors.GREEN, e=bcolors.ENDC)
    os.system("ps ax|grep /opt/clarisse | grep -v 0:00")
    print "\n"
    print "{c}  Running 'Nuke':{e}".format(c=bcolors.GREEN, e=bcolors.ENDC)
    os.system("ps ax|grep /opt/Nuke | grep -v 0:00")
    print "\n"
    print "{c}  Running 'Rv':{e}".format(c=bcolors.GREEN, e=bcolors.ENDC)
    os.system("ps ax|grep /opt/rv-Linux | grep -v 0:00")
    print "\n"
    # print "{c}CPU used rank:{e}".format(c=bcolors.GREEN, e=bcolors.ENDC)
    # os.system("echo \"`ps -eo ppid,user,bsdstart,bsdtime,%mem,%cpu,args --sort=-%cpu | /usr/bin/head -n 5`\"\n")
    print "{c}  Memory usage TOP 5:{e}".format(c=bcolors.GREEN, e=bcolors.ENDC)
    os.system("echo \"   `ps -eo pmem,pcpu,vsize,args | sort -rk 1 | head -n 5 | cut -c -100`\"\n")
    # os.system("for ((i=1; i <= 10; i++)); do echo -ne =; sleep 0.2; done")

def _kill(proc_real, title):
    if proc_real != "":
        os.system("kill -9 $(ps ax|grep {p} | grep -v grep | awk '{{ print $1 }}')".format(p=proc_real))
        os.system("pkill -9 {0}".format(title))
        print ">>>  ok"
        print "{c}Kill '{p}' process ... {g}Done{e}".format(c=bcolors.RED, p=title, g=bcolors.GREEN, e=bcolors.ENDC)
    else:
        print "{c}Couldn't find any process named by '{p}'.{e}".format(c=bcolors.YELLOW, p=title, e=bcolors.ENDC)

def nuke_kill(proc_real, title):
    if proc_real != "":
        # os.system("kill -9 $(ps ax|grep {p} |grep -v grep |grep {t}|grep -Eo ^[0-9]+)".format(p=proc_real, t=title))
        os.system("kill -9 $(ps ax|grep {p} |grep -v grep |grep {t}|awk '{{ print $1 }}')".format(p=proc_real, t=title))
        print "{c}Kill '{p}' process ... {g}Done{e}".format(c=bcolors.RED, p=title, g=bcolors.GREEN, e=bcolors.ENDC)
    else:
        print "{c}Couldn't find any process named by '{p}'.{e}".format(c=bcolors.YELLOW, p=title, e=bcolors.ENDC)

def kill_proc(proc):
    proc_real = ""
    # remapping process name
    if proc == "nuke":
        _kill("/opt/Nuke", 'Nuke')
    elif proc == "rv":
        _kill("/opt/rv-Linux", 'RV')
    elif proc == "mocha":
        _kill("/opt/isl/mocha", 'mocha')
    elif proc == "argos":
        _kill("python\ main.py", 'Argos')
    elif proc == "clarisse":
        _kill("/opt/clarisse", 'clarisse')
    elif proc == "maya":
        _kill("/usr/autodesk/maya", 'maya')
    elif proc == "katana":
        _kill("/opt/Katana", 'katanaBin')
    elif proc == "hrender":
        _kill("/opt/hfs", 'hrender')
    elif proc == "hbatch":
        _kill("/opt/hfs", 'hbatch')
    else:
        farm = ['192.168.10.11']

        farm_ip = farm[0]

        piece = proc.split(',')
        if piece[0].startswith('t'):
            farm_ip = farm[int(piece[0][-1])-1]
            piece.pop(0)
        
        hostname = os.environ.get('HOSTNAME', 'UNKNOWN')
        if hostname in ['gisub', 'joonhyung', 'sungku', 'yanghae']:
            condition = ''
        else:
            condition = 'and Job.owner=%s ' % 'gisub' #hostname

        if not piece[0].startswith('rf'):
            tq.setEngineClientParam(hostname=farm_ip, port=80, user="root", debug=False)

        for job in piece:
            # blades = tq.blades("state=error or state=active {0}and Job.jid={1}".format(condition, int(job)))
            if job.startswith('rf'):
                blades = [{"name":job}]
            else:
                #job id
                blades = tq.blades("state=error or state=active and Job.jid={0}".format(int(job)))
                blade_list = [] #Append all rf numbers
                blade_new_list = [] #Remove duplicate rf numbers
                for blade in blades:
                    blade_list.append(blade['name'])
                for bl in blade_list:
                    if bl not in blade_new_list:
                        blade_new_list.append(bl)
                jobs = tq.jobs("active", columns=["jid", "owner", "title", "tags"])

            if len(blades):
                for blade in blade_new_list:
                    # os.popen("rsh %s python /core/Linux/APPZ/shell/yslow.py -k nuke" % blade['name'])
                    os.popen("rsh %s python /core/Linux/APPZ/shell/yslow.py -k maya" % blade)
                    os.popen("rsh %s python /core/Linux/APPZ/shell/yslow.py -k clarisse" % blade)
                    os.popen("rsh %s python /core/Linux/APPZ/shell/yslow.py -k hrender" % blade)
                    os.popen("rsh %s python /core/Linux/APPZ/shell/yslow.py -k hbatch" % blade)
                    os.popen("rsh %s python /core/Linux/APPZ/shell/yslow.py -k katana" % blade)
                    os.popen("rsh %s rm -rf /var/temp/*.mb" % blade)
                    os.popen("rsh %s rm -rf /var/temp/Maya*" % blade)
                    os.popen("rsh %s rm -rf /var/temp/Pixar" % blade)
                    os.popen("rsh %s rm -rf /var/temp/houdini_temp" % blade)
                    os.popen("rsh %s rm -rf /var/temp/*katana" % blade)
                    for n_job in jobs:
                        if 'nuke' in n_job['tags']:
                            if int(n_job['jid']) == int(job):
                                job_title = n_job['title'].split(' ')[2]
                                os.popen("rsh %s python /core/Linux/APPZ/shell/yslow.py -n %s" % (blade, job_title))
                    print 'kill blade  : %s' % blade
                #tq.delete("jid=%s" % job)

                if job.startswith('rf'):
                    print 'Farm %s has been deleted.' % blade
                else:
                    print 'Job ID %d has been deleted.' % int(job)
            else:
                print "It couldn't find any Job ID %d or you can't delete the other's Job." % int(job)                

        tq.closeEngineClient()


def drop_cache():
    os.system("/core/Linux/bin/drop_cache")
    print "{c}Drop the cache memory ... {g}Done{e}".format(c=bcolors.RED, g=bcolors.GREEN, e=bcolors.ENDC)


def main(argv):
    try:
        opts, args = getopt.getopt(argv, "hcamk:n:", ["help", "check", "all", "memory", "kill=", "nuke="])
    except getopt.GetoptError as err:
        print str(err)
        help()
        sys.exit(1)

    if len(opts) == 0:
        check()
        print "\n\n ... typing {c}'yslow -h'{e} for more options.".format(c=bcolors.GREEN, e=bcolors.ENDC)
        sys.exit()

    for opt, arg in opts:
        if opt in ("-c", "--check"):
            check()
        elif opt in ("-a", "--all"):
            drop_cache()
            kill_proc("nuke")
            kill_proc("maya")
            kill_proc("clarisse")
            kill_proc("hrender")
            kill_proc("hbatch")
            kill_proc("katana")
            kill_proc("rv")
            kill_proc("mocha")
        elif opt in ("-m", "--memory"):
            drop_cache()
        elif opt in ("-k", "--kill"):
            proc = arg
            kill_proc(proc)
        elif opt in ("-n", "--nuke"):
            title = arg
            nuke_kill("/opt/Nuke", title)
        elif opt in ("-h", "--help"):
            help()
            sys.exit()

    return


if __name__ == "__main__":
    main(sys.argv[1:])


#yslow -k 51814,51915,12345
#yslow-k t3,51814


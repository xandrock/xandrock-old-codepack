import struct
import binascii
import codecs
import sys, re, os
import subprocess
import datetime
import platform
import string
import time
import shutil
from set_env import*


nowT = datetime.datetime.now().strftime('%Y%m%d')

factor = '';
for i in range(1, len(sys.argv) - 1, 2):
    if sys.argv[i] == '-h':
        print('parameters:\n    -v : version\n    -f : build project filter factor')
        exit(0)
    if sys.argv[i] == '-v' and i < len(sys.argv) - 1:
        nowT = sys.argv[i+1]
        continue;
    if sys.argv[i] == '-f' and i < len(sys.argv) - 1:
        factor = sys.argv[i+1]
        continue;
    print('unknow parameter, print -h to show help message', sys.argv[i]);
    exit(1);

subprocess.call('git reset --hard & git pull', shell = True)

#sys.stdout=open('buildlog.log','w')

fp = codecs.open('./common/imcp.proto', 'r', encoding='utf-8')
lines = fp.readlines()
fp.close()

fpw = codecs.open('./common/imcp.proto', 'w', encoding='utf-8')
for line in lines:
    line = re.sub(r'buildno\s*=\s*4\[default=\d+\]', 'buildno=4[default='+ nowT + ']', line)
    fpw.write(line)
fpw.close()

os.chdir('./common')
subprocess.call('protoc --cpp_out=../include imcp.proto', shell = True)
os.chdir('../')

if not os.path.exists('build'):
    os.mkdir('build');
os.chdir('./build')
subprocess.call('rm *', shell = True)
os.chdir('../')

osver = platform.platform()
sourceDir = os.path.abspath('.')
for path, folders, files in os.walk('.'):  
    for f in files:
        if not f.startswith('imcp_') and (len(factor) == 0 or factor in f):
            if osver.startswith('Window'):
                if f.endswith('x86-win32.pro'):
                    os.chdir(path)
                    subprocess.call('rm Makefile*', shell = True)
                    cmd = '\"' + VSDir + '\\vcvarsall.bat\"  x86 & ' + Qt32 + '\\qmake ' + f + ' & jom clean & jom -j4 >' + sourceDir + '/build/' + f +'.buildlog'
                    print cmd;
                    subprocess.call(cmd, shell = True)
                    os.chdir(sourceDir)
                if f.endswith('x86-win64.pro'):
                    os.chdir(path)
                    subprocess.call('rm Makefile*', shell = True)
                    cmd = '\"' + VSDir + '\\vcvarsall.bat\"  amd64 & ' + Qt64 + '\\qmake ' + f + ' & jom clean & jom -j4 > ' + sourceDir + '/build/' + f +'.buildlog'
                    print cmd;
                    subprocess.call(cmd, shell = True)
                    os.chdir(sourceDir)
            if osver.startswith('Linux'):
                if f.endswith('x86-linux32.pro'):
                    os.chdir(path)
                    subprocess.call('rm Makefile*', shell = True)
                    subprocess.call(Qt32 + '/qmake ' + f, shell = True)
                    subprocess.call('make clean', shell = True)
                    subprocess.call('make -j 4 2> ' + sourceDir + '/build/' + f +'.buildlog', shell = True)
                    os.chdir(sourceDir)
                if f.endswith('x86-linux64.pro'):
                    os.chdir(path)
                    subprocess.call('rm Makefile*', shell = True)
                    subprocess.call(Qt64 + '/qmake ' + f, shell = True)
                    subprocess.call('make clean', shell = True)
                    subprocess.call('make -j 4 2> ' + sourceDir + '/build/' + f +'.buildlog', shell = True)
                    os.chdir(sourceDir)
                if f.endswith('arm-linux.pro'):
                    os.chdir(path)
                    subprocess.call('rm Makefile*', shell = True)
                    subprocess.call(QtEmb + '/qmake ' + f, shell = True)
                    subprocess.call('make clean', shell = True)
                    subprocess.call('make -j 4 2> ' + sourceDir + '/build/' + f +'.buildlog', shell = True)
                    os.chdir(sourceDir)
subprocess.call('git reset --hard', shell = True)

print '\n\n\nChecking Error......\n\n\n'
bError = 0
os.chdir('./build')
for path, folders, files in os.walk('.'):  
    for f in files:
        if f.endswith('.buildlog'):
            fp = codecs.open(os.path.join(path, f), 'r')
            lines = fp.readlines()
            fp.close()
            for line in lines:
                if line.find(' error') != -1 or line.find(' Error') != -1:
                    print line
                    bError = bError + 1
os.chdir('../')

if bError > 0:
    print '\n\n\n\n\n\n\n\n\n  Error Detected in this building process, Project Build Failed!!!!!!!'
    exit(0)

os.chdir('../release')

if osver.startswith('Window'):
    for path, folders, files in os.walk('.'):  
        for f in files:
            if f.endswith('.pdb') or f.endswith('.ilk') or f.endswith('.exp') or f.endswith('.lib') or f.endswith('.embed.manifest'):
                os.remove(os.path.join(path, f))
            if f == 'imcpsa.exe':
                shutil.copy('../source/agent/imcpsa.conf.sample', os.path.join(path, 'imcpsa.conf'))
            if f == 'imcpcs.exe':
                shutil.copy('../source/core/imcpcs.conf.sample', os.path.join(path, 'imcpcs.conf'))
                shutil.copy('../source/core/imcpcs_zh.qm', os.path.join(path, 'imcpcs_zh.qm'))
                shutil.copy('../design/db_sql/imcp.dat.sample', os.path.join(path, 'imcp.dat'))
                shutil.copy('../design/db_sql/imcphist.dat.sample', os.path.join(path, 'imcphist.dat'))
            if f == 'idbg.exe':
                shutil.copy('../source/idebugger/idebugger_zh.qm', os.path.join(path, 'idebugger_zh.qm'))
                shutil.copy('../source/idebugger/qt_zh_CN.qm', os.path.join(path, 'qt_zh_CN.qm'))
                shutil.copy('../source/idebugger/scripttools_zh_CN.qm', os.path.join(path, 'scripttools_zh_CN.qm'))
                shutil.copy('../source/idebugger/idebugger.conf.sample', os.path.join(path, 'idebugger.conf'))
            if f == 'ialarm.exe':
                shutil.copy('../source/ialarm/ialarm_zh.qm', os.path.join(path, 'ialarm_zh.qm'))
                shutil.copy('../source/ialarm/ialarm.conf.sample', os.path.join(path, 'ialarm.conf'))
            if f == 'agentmgr.exe':
                shutil.copy('../source/agentmgr/agentmgr.conf.sample', os.path.join(path, 'agentmgr.conf'))
            if f == 'webint.exe':
                if os.path.exists(os.path.join(path,'webint.fcg')):
                    os.remove(os.path.join(path,'webint.fcg'))	
                os.rename(os.path.join(path,'webint.exe'), os.path.join(path,'webint.fcg'))
                shutil.copy('../source/webint/webint_zh.qm', os.path.join(path, 'webint_zh.qm'))
                shutil.copy('../source/webint/webint.conf.sample', os.path.join(path, 'webint.conf'))
            if f == 'ipersist.exe':
                shutil.copy('../source/ipersist/ipersist_zh.qm', os.path.join(path, 'ipersist_zh.qm'))
                shutil.copy('../source/ipersist/ipersist.conf.sample', os.path.join(path, 'ipersist.conf'))
                shutil.copy('../design/db_sql/imcphist.dat.sample', os.path.join(path, 'imcphist.dat'))
            if f == 'dh104.exe':
                shutil.copy('../source/dh104/port.ini', os.path.join(path, 'port.ini'))
                shutil.copy('../source/dh104/DH104.ini', os.path.join(path, 'DH104.ini'))
            if f == 'thirdtester.exe':
                shutil.copy('../source/thirddatatester/tirdtester_zh.qm', os.path.join(path, 'tirdtester_zh.qm'))
if osver.startswith('Linux'):
    for path, folders, files in os.walk('.'):  
        for f in files:
            if f.find('.') == -1 or f.find('.so') >= 0:
                subprocess.call('arm-linux-strip ' + os.path.join(path, f), shell = True)
            if f == 'imcpsa':
                shutil.copy('../source/agent/imcpsa.conf.sample', os.path.join(path, 'imcpsa.conf'))
            if f == 'imcpcs':
                shutil.copy('../source/core/imcpcs.conf.sample', os.path.join(path, 'imcpcs.conf'))
                shutil.copy('../source/core/imcpcs_zh.qm', os.path.join(path, 'imcpcs_zh.qm'))
                shutil.copy('../design/db_sql/imcp.dat.sample', os.path.join(path, 'imcp.dat'))
                shutil.copy('../design/db_sql/imcphist.dat.sample', os.path.join(path, 'imcphist.dat'))
            if f == 'ialarm':
                shutil.copy('../source/ialarm/ialarm_zh.qm', os.path.join(path, 'ialarm_zh.qm'))
                shutil.copy('../source/ialarm/ialarm.conf.sample', os.path.join(path, 'ialarm.conf'))
            if f == 'agentmgr':
                shutil.copy('../source/agentmgr/agentmgr.conf.sample', os.path.join(path, 'agentmgr.conf'))
            if f == 'webint':
                if os.path.exists(os.path.join(path,'webint.fcg')):
                    os.remove(os.path.join(path,'webint.fcg'))
                os.rename(os.path.join(path,'webint'), os.path.join(path,'webint.fcg'))
                shutil.copy('../source/webint/webint_zh.qm', os.path.join(path, 'webint_zh.qm'))
                shutil.copy('../source/webint/webint.conf.sample', os.path.join(path, 'webint.conf'))
            if f == 'ipersist':
                shutil.copy('../source/ipersist/ipersist_zh.qm', os.path.join(path, 'ipersist_zh.qm'))
                shutil.copy('../source/ipersist/ipersist.conf.sample', os.path.join(path, 'ipersist.conf'))
                shutil.copy('../design/db_sql/imcphist.dat.sample', os.path.join(path, 'imcphist.dat'))
            if f == 'dh104':
                shutil.copy('../source/dh104/port.ini', os.path.join(path, 'port.ini'))
                shutil.copy('../source/dh104/DH104.ini', os.path.join(path, 'DH104.ini'))
               

if osver.startswith('Window'):
    subprocess.call('\"' + RarDir + '/WinRar\" a -sfx imcp-backend_arm-win32_' + nowT + '.rar ./arm-win', shell = True)
    subprocess.call('\"' + RarDir + '/WinRar\" a -sfx imcp-backend_x86-win32_' + nowT + '.rar ./x86-win32', shell = True)
    subprocess.call('\"' + RarDir + '/WinRar\" a -sfx imcp-backend_x86-win64_' + nowT + '.rar ./x86-win64', shell = True)
if osver.startswith('Linux'):
    subprocess.call('tar -zcvf imcp-backend_arm-linux32_' + nowT + '.tar.bz2 ./arm-linux', shell = True)
    subprocess.call('tar -zcvf imcp-backend_x86-linux32_' + nowT + '.tar.bz2 ./x86-linux32', shell = True)
    subprocess.call('tar -zcvf imcp-backend_x86-linux64_' + nowT + '.tar.bz2 ./x86-linux64', shell = True)


time.sleep(3)
            

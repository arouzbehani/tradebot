import datetime


strd=''
strd += '****************************************************************'



fname = str(datetime.datetime.now()).split('.')[0].replace(':',"_") + '.txt'
f = open(fname, "w")

f.write(strd)
f.close()
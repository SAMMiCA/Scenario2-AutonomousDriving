import os
from os.path import isfile, join
path_rgb= './rgb'
path_seg= './seg'
files1 = [f for f in os.listdir(path_seg) if os.path.isfile(join(path_seg, f))]

for i in range(len(files1)):
    if os.path.isfile (path_rgb+'/'+str(files1[i])) == False:
        os.remove(path_seg+'/'+str(files1[i]))

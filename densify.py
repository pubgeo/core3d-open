import numpy as np
import cv2
import random

# fill gaps in a point cloud by adding noise to xy coordinates
def densify(inpath, outpath, hrad_meters=1.0):
    # read ASCII XYZ file
    print('reading file...')
    fid = open(inpath,'r')
    lines = fid.readlines()
    fid.close()
    num = len(lines)
    x = np.zeros(num)
    y = np.zeros(num)
    z = np.zeros(num)
    for k in range(num):
        xyz = lines[k].split()
        x[k] = float(xyz[0])
        y[k] = float(xyz[1])
        z[k] = float(xyz[2])
    xyz = None
    # write new ASCII XYZ file
    print('writing file...')
    random.seed(0)
    fid = open(outpath,'w')
    for k in range(len(x)):
        xx = x[k] + random.uniform(-hrad_meters, hrad_meters)
        yy = y[k] + random.uniform(-hrad_meters, hrad_meters)
        zz = z[k]
        fid.write(str(xx) + ' ' + str(yy) + ' ' + str(zz) + '\n')
    fid.close()

# run a test
if __name__ == "__main__":
    densify(sys.argv[1], sys.argv[2])



import sys
import os
from osgeo import gdal
import numpy as np
import json
import cv2
from PIL import Image

def imageLoad(filename):
    im = gdal.Open(filename, gdal.GA_ReadOnly)
    band = im.GetRasterBand(1)
    img = band.ReadAsArray(0, 0, im.RasterXSize, im.RasterYSize)
    transform = im.GetGeoTransform()
    return img, transform

def getNoDataValue(filename):
    im = gdal.Open(filename, gdal.GA_ReadOnly)
    band = im.GetRasterBand(1)
    nodata = band.GetNoDataValue()
    return nodata

def getMetadata(inputinfo):
    if isinstance(inputinfo,gdal.Dataset):
        dataset = inputinfo
        FLAG_CLOSE = False
    elif isinstance(inputinfo,str):
        filename = inputinfo
        if not os.path.isfile(filename):
            raise IOError('Cannot locate file <{}>'.format(filename))
        dataset = gdal.Open(filename, gdal.GA_ReadOnly)
        FLAG_CLOSE = True
    else:
        raise IOError('Unrecognized getMetadata input')
    meta = {
        'RasterXSize':  dataset.RasterXSize,
        'RasterYSize':  dataset.RasterYSize,
        'RasterCount':  dataset.RasterCount,
        'Projection':   dataset.GetProjection(),
        'GeoTransform': list(dataset.GetGeoTransform()),
    }
    if FLAG_CLOSE: dataset = None
    return meta

def imageWarp(file_src, file_dst, offset=None, interp_method=gdal.gdalconst.GRA_Bilinear, noDataValue=None):
    # destination metadata
    meta_dst = getMetadata(file_dst)
    # GDAL memory driver
    mem_drv = gdal.GetDriverByName('MEM')
    # copy source to memory
    tmp = gdal.Open(file_src, gdal.GA_ReadOnly)
    dataset_src = mem_drv.CreateCopy('',tmp)   
    tmp = None
    # change no data value to new "noDataValue" input if necessary,
    # making sure to adjust the underlying pixel values
    band = dataset_src.GetRasterBand(1)
    NDV = band.GetNoDataValue()
    if noDataValue is not None and noDataValue != NDV:
        if NDV is not None:            
            img = band.ReadAsArray()
            img[img==NDV] = noDataValue
            band.WriteArray(img)
        band.SetNoDataValue(noDataValue)        
        NDV = noDataValue
    # source metadata
    meta_src = getMetadata(dataset_src)
    # Apply registration offset
    if offset is not None:

        # offset error: offset is defined in destination projection space,
        # and cannot be applied if source and destination projections differ
        if meta_src['Projection'] != meta_dst['Projection']:
            print('IMAGE PROJECTION\n{}'.format(meta_src['Projection']))
            print('OFFSET PROJECTION\n{}'.format(meta_dst['Projection']))
            raise ValueError('Image/Offset projection mismatch')

        transform = meta_src['GeoTransform']
        transform[0] += offset[0]
        transform[3] += offset[1]
        dataset_src.SetGeoTransform(transform)
    # no reprojection necessary
    if meta_src == meta_dst:
        print('  No reprojection')
        dataset_dst = dataset_src
    # reprojection
    else:
        keys = [k for k in meta_dst if meta_dst.get(k) != meta_src.get(k)]
        print('  REPROJECTION (adjusting {})'.format(', '.join(keys)))
        # file, xsz, ysz, nbands, dtype
        dataset_dst = mem_drv.Create('', meta_dst['RasterXSize'], meta_dst['RasterYSize'], 
            meta_src['RasterCount'], gdal.GDT_Float32)
        dataset_dst.SetProjection(meta_dst['Projection'])
        dataset_dst.SetGeoTransform(meta_dst['GeoTransform'])
        if NDV is not None:
            band = dataset_dst.GetRasterBand(1)
            band.SetNoDataValue(NDV)
            band.Fill(NDV)
        # input, output, inputproj, outputproj, interp
        gdal.ReprojectImage(dataset_src, dataset_dst, meta_src['Projection'],
             meta_dst['Projection'], interp_method)
    # read & return image data
    img = dataset_dst.GetRasterBand(1).ReadAsArray()    
    return img

def convert_for_eval(dsm_path):
    # load DSM and CLS
    src_ds = gdal.Open(dsm_path)
    projection = src_ds.GetProjection()
    raster_x_size = src_ds.RasterXSize
    raster_y_size = src_ds.RasterYSize
    ulx, xres, xskew, uly, yskew, yres  = src_ds.GetGeoTransform()
    band = src_ds.GetRasterBand(1)
    nodata = band.GetNoDataValue()
    dsm = band.ReadAsArray(0, 0, src_ds.RasterXSize, src_ds.RasterYSize)
    cls_path = dsm_path.replace('DSM','CLS')
    cls = imageWarp(dsm_path.replace('DSM','CLS'), dsm_path).astype(np.uint8)
    # resample DSM and CLS to 50cm if not already
    gsd=0.5
    cols = int(raster_x_size * xres / gsd)
    rows = int(raster_y_size * -yres / gsd)
    dsm = cv2.resize(dsm,(cols,rows),interpolation=cv2.INTER_NEAREST)
    cls = cv2.resize(cls,(cols,rows),interpolation=cv2.INTER_NEAREST)
    # convert DSM to decimeters for smaller integer files
    dsm[dsm == nodata] = np.nan
    zoffset = np.nanmin(dsm)
    dsm -= zoffset
    zscale=0.1
    dsm = (dsm / zscale).astype(np.uint16)
    nodata = 65535
    dsm[np.isnan(dsm)] = nodata
    # save DSM and CLS
    dsm = Image.fromarray(dsm)
    dsm.save(dsm_path.replace('.tif','.png'))
    cls = Image.fromarray(cls)
    cls.save(cls_path.replace('.tif','.png'))
    # write JSON metadata
    json_path = dsm_path.replace('.tif','.json')
    with open(json_path, "w") as outfile:
        metadata = {
            "easting": np.float64(ulx),
            "northing": np.float64(uly),
            "gsd": np.float64(gsd),
            "zoffset": np.float64(zoffset),
            "zscale": np.float64(zscale),
            "nodata": np.float64(nodata)
        }
        json.dump(metadata, outfile)

if __name__ == "__main__":
    convert_for_eval(sys.argv[1])





# -*- coding: utf-8 -*-

import gdal, os
from LandsatBasicUtils.MetadataReader import LandsatMetadataReader
from LandsatBasicUtils.BandCalibrator import LandsatBandCalibrator

class AlbedoRetriever():
    A_pd = 0.03

    def __init__(self, metadata_file, temp_dir, albedo_method='olmedo', correction_method='raw',
                        dem_file=None,
                        angles_file=None,
                        usgs_utils=None,
                        cygwin_bash_exe_path=None):

        self.metadata_file = metadata_file
        self.metadata = LandsatMetadataReader(metadata_file)
        self.dataset_directory = os.path.dirname(metadata_file)
        self.temp_dir = temp_dir
        self.dem_file = dem_file

        if albedo_method not in ['tasumi','olmedo','liang','beg']:
            raise TypeError('Unsupported albedo method. Supported: tasumi, olmedo, liang, beg')

        self.albedo_method = albedo_method

        if correction_method not in ['raw','dos','srem', 'mixed_v1']:
            raise TypeError('Unsupported correction method. Supported: raw, dow, srem')
        self.correction_method = correction_method

        if albedo_method in ['beg']:
            self.correction_method = 'raw'

        self.angles_file = angles_file
        self.usgs_utils = usgs_utils
        self.cygwin_bash_exe_path = cygwin_bash_exe_path

    def get_albedo_as_array(self):
        # These methods are over SR
        # Olmedo: 0.246, 0.146, 0.191, 0.304, 0.105, 0.008 | https://rdrr.io/cran/water/src/R/water_netRadiation.G.R
        # Tasumi: 0.254, 0.149, 0.147, 0.311, 0.103, 0.036 | Tasumi, M., Allen, R. G. and Trezza, R.: At-surface reflectance and albedo from satellite for operational calculation of land surface energy balance, J. Hydrol. Eng., 13(2), 51–63, doi:10.1061/(ASCE)1084-0699(2008)13:2(51), 2008.
        # Liang: 0.356, 0, 0.130, 0.373, 0.085, 0.072 | Liang, S. (2000). Narrowband to broadband conversions of land surface albedo: I. Algorithms. Remote Sensing of Environment, 76(1), 213-238

        # These methods are over TOA
        # Beg: 0.356*b2 + 0.326*b3 + 0.138*b4 + 0.084*b5 + 0.056*b6 + 0.041*b7 | Ayad Ali Faris Beg, Ahmed H. Al-Sulttani, Adrian Ochtyra, Anna Jarocińska and Adriana Marcinkowska: Estimation of Evapotranspiration Using SEBAL Algorithm and Landsat-8 Data—A Case Study: Tatra Mountains Region, J. Geol. Resour. Eng., 4(6), 257–270, doi:10.17265/2328-2193/2016.06.002, 2016.

        # STEP 1. Get bands 2-7 reflectances
        print('Obtaining bands 2-7 reflectance. Current correction method: %s' % self.correction_method)
        bands = range(2, 8)
        bands_arrays = []
        if self.correction_method == 'raw':
            for band in bands:
                print ('Processing band %s' % band)
                current_band_path = os.path.join(self.dataset_directory, self.metadata.bands[str(band)]['file_name'])
                current_band_calibrator = LandsatBandCalibrator(current_band_path, self.metadata_file)
                current_band_reflectance = current_band_calibrator.get_reflectance_as_array()
                bands_arrays.append(current_band_reflectance)

        if self.correction_method == 'dos':
            for band in bands:
                print('Processing band %s' % band)
                current_band_path = os.path.join(self.dataset_directory, self.metadata.bands[str(band)]['file_name'])
                current_band_calibrator = LandsatBandCalibrator(current_band_path, self.metadata_file)
                current_band_reflectance = current_band_calibrator.get_dos_corrected_reflectance_as_array()
                bands_arrays.append(current_band_reflectance)

        if self.correction_method == 'srem':
            from SREMPyLandsat.SREMPyLandsat import SREMPyLandsat
            for band in bands:
                print('Processing band %s' % band)
                srem = SREMPyLandsat(mode='landsat-usgs-utils')
                data = {'band': os.path.join(self.dataset_directory, self.metadata.bands[str(band)]['file_name']),
                        'metadata': self.metadata_file,
                        'angles_file': self.angles_file,
                        'usgs_util_path': self.usgs_utils,
                        'temp_dir': self.temp_dir,
                        'cygwin_bash_exe_path': self.cygwin_bash_exe_path}
                srem.set_data(data)
                current_band_reflectance = srem.get_srem_surface_reflectance_as_array()
                bands_arrays.append(current_band_reflectance)

        if self.correction_method == 'mixed_v1':
            # Empirical optimal combination: b2 - DOS, b3 - srem, b4 - srem, b5 - srem, b6 - raw, b7 - raw
            from SREMPyLandsat.SREMPyLandsat import SREMPyLandsat
            for band in bands:
                print('Processing band %s' % band)
                current_band_path = os.path.join(self.dataset_directory, self.metadata.bands[str(band)]['file_name'])
                if band == 2:
                    print ('Process with DOS')
                    current_band_calibrator = LandsatBandCalibrator(current_band_path, self.metadata_file)
                    current_band_reflectance = current_band_calibrator.get_dos_corrected_reflectance_as_array()
                    bands_arrays.append(current_band_reflectance)
                if band in [3,4,5]:
                    print('Process with SREM')
                    srem = SREMPyLandsat(mode='landsat-usgs-utils')
                    data = {'band': current_band_path,
                            'metadata': self.metadata_file,
                            'angles_file': self.angles_file,
                            'usgs_util_path': self.usgs_utils,
                            'temp_dir': self.temp_dir,
                            'cygwin_bash_exe_path': self.cygwin_bash_exe_path}
                    srem.set_data(data)
                    current_band_reflectance = srem.get_srem_surface_reflectance_as_array()
                    bands_arrays.append(current_band_reflectance)
                if band in [6,7]:
                    print('Process as RAW')
                    current_band_calibrator = LandsatBandCalibrator(current_band_path, self.metadata_file)
                    current_band_reflectance = current_band_calibrator.get_reflectance_as_array()
                    bands_arrays.append(current_band_reflectance)

        print ('Preparing coefficients. Current method is: %s' % self.albedo_method)
        if self.albedo_method == 'tasumi':
            coefs = [0.254, 0.149, 0.147, 0.311, 0.103, 0.036]
        if self.albedo_method == 'olmedo':
            coefs = [0.246, 0.146, 0.191, 0.304, 0.105, 0.008]
        if self.albedo_method == 'liang':
            coefs = [0.356, 0, 0.130, 0.373, 0.085, 0.072]
        if self.albedo_method == 'beg':
            coefs = [0.356, 0.326, 0.138, 0.084, 0.056, 0.041]
        print ('Coefficients are: %s' % str(coefs))


        if self.albedo_method in ['tasumi','olmedo','liang']:
            print ('Calculating albedo...')
            albedo = coefs[0]*bands_arrays[0] + coefs[1]*bands_arrays[1] + coefs[2]*bands_arrays[2] + coefs[3]*bands_arrays[3] + coefs[4]*bands_arrays[4] + coefs[5]*bands_arrays[5]
            if self.albedo_method == 'liang':
                print ('Liang method correction: -0.0018')
                albedo = albedo - 0.0018

        elif self.albedo_method in ['beg']:
            etalon_ds = gdal.Open(os.path.join(self.dataset_directory, self.metadata.bands['2']['file_name']))
            geoTransform = etalon_ds.GetGeoTransform()
            projection = etalon_ds.GetProjection()
            xMin = geoTransform[0]
            yMax = geoTransform[3]
            xMax = xMin + geoTransform[1] * etalon_ds.RasterXSize
            yMin = yMax + geoTransform[5] * etalon_ds.RasterYSize
            xSize = etalon_ds.RasterXSize
            ySize = etalon_ds.RasterYSize

            print ('Recalculating DEM to scene domain')
            elevation_ds = gdal.Open(self.dem_file)
            elevation_ds_converted = gdal.Warp('',elevation_ds,format='MEM',outputBounds = (xMin, yMin, xMax, yMax), width=xSize, height=ySize, dstSRS=projection)
            elevation_array = elevation_ds_converted.GetRasterBand(1).ReadAsArray()

            print('beg calculations')
            A_TOA = coefs[0]*bands_arrays[0] + coefs[1]*bands_arrays[1] + coefs[2]*bands_arrays[2] + coefs[3]*bands_arrays[3] + coefs[4]*bands_arrays[4] + coefs[5]*bands_arrays[5]
            t_sw = 0.75 + 2 * 0.00001 * elevation_array
            albedo = (A_TOA - self.A_pd) / (t_sw * t_sw)

        albedo[albedo<0] = 0.0
        albedo[albedo>1] = 1.0
        return albedo

    def save_albedo_as_gtiff(self, new_file_path):
        albedo_array = self.get_albedo_as_array()
        etalon_ds = gdal.Open(os.path.join(self.dataset_directory, self.metadata.bands['2']['file_name']))
        driver = gdal.GetDriverByName("GTiff")
        dataType = gdal.GDT_Float32
        dataset = driver.Create(new_file_path, etalon_ds.RasterXSize, etalon_ds.RasterYSize,
                                etalon_ds.RasterCount, dataType)
        dataset.SetProjection(etalon_ds.GetProjection())
        dataset.SetGeoTransform(etalon_ds.GetGeoTransform())
        dataset.GetRasterBand(1).WriteArray(albedo_array)
        del dataset

#a = AlbedoRetriever(metadata_file='F:/LC08_L1TP_182019_20190830_20190903_01_T1/LC08_L1TP_182019_20190830_20190903_01_T1_MTL.txt',
#                    temp_dir='F:/',
#                    albedo_method='olmedo',
#                    correction_method='dos')

#print (a.metadata.bands['2']['file_name'])
#a.save_albedo_as_gtiff('F:/LC08_L1TP_182019_20190830_20190903_01_T1/olmedo_dos_albedo.tif')

#a = AlbedoRetriever(metadata_file='F:/LC08_L1TP_182019_20190830_20190903_01_T1/LC08_L1TP_182019_20190830_20190903_01_T1_MTL.txt',
#                    angles_file='F:/LC08_L1TP_182019_20190830_20190903_01_T1/LC08_L1TP_182019_20190830_20190903_01_T1_ANG.txt',
#                    temp_dir='F:/LC08_L1TP_182019_20190830_20190903_01_T1/temp',
#                    albedo_method='olmedo',
#                    correction_method='srem',
#                    usgs_utils='F:/software/l8_angles/l8_angles.exe',
#                    cygwin_bash_exe_path='C:/cygwin64/bin/bash.exe',
#                    dem_file='F:/LC08_L1TP_182019_20190830_20190903_01_T1/DEM.tif')
#
#a.save_albedo_as_gtiff('F:/LC08_L1TP_182019_20190830_20190903_01_T1/olmedo_srem_albedo.tif')

a = AlbedoRetriever(metadata_file='F:/LC08_L1TP_182019_20190830_20190903_01_T1/LC08_L1TP_182019_20190830_20190903_01_T1_MTL.txt',
                    angles_file='F:/LC08_L1TP_182019_20190830_20190903_01_T1/LC08_L1TP_182019_20190830_20190903_01_T1_ANG.txt',
                    temp_dir='F:/LC08_L1TP_182019_20190830_20190903_01_T1/temp',
                    albedo_method='beg',
                    correction_method='raw',
                    usgs_utils='F:/software/l8_angles/l8_angles.exe',
                    cygwin_bash_exe_path='C:/cygwin64/bin/bash.exe',
                    dem_file='F:/LC08_L1TP_182019_20190830_20190903_01_T1/DEM.tif')

a.save_albedo_as_gtiff('F:/LC08_L1TP_182019_20190830_20190903_01_T1/beg_raw_albedo.tif')
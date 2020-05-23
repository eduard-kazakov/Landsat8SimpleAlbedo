# Landsat8SimpleAlbedo
Simple class for retriving broadband albedo from Landsat 8 imagery

## Requirements

gdal, numpy

LandastBasicUtils | https://github.com/eduard-kazakov/LandastBasicUtils 

Optional requirement: SREMPy-landsat  | https://github.com/eduard-kazakov/SREMPy-landsat. If installed, additional option of reflectance correction is available.

## References

Tasumi, M., Allen, R. G. and Trezza, R.: At-surface reflectance and albedo from satellite for operational calculation of land surface energy balance, J. Hydrol. Eng., 13(2), 51–63, doi:10.1061/(ASCE)1084-0699(2008)13:2(51), 2008.

Liang, S. (2000). Narrowband to broadband conversions of land surface albedo: I. Algorithms. Remote Sensing of Environment, 76(1), 213-238

Ayad Ali Faris Beg, Ahmed H. Al-Sulttani, Adrian Ochtyra, Anna Jarocińska and Adriana Marcinkowska: Estimation of Evapotranspiration Using SEBAL Algorithm and Landsat-8 Data—A Case Study: Tatra Mountains Region, J. Geol. Resour. Eng., 4(6), 257–270, doi:10.17265/2328-2193/2016.06.002, 2016.

https://rdrr.io/cran/water/src/R/water_netRadiation.G.R

## Installation

```bash
pip install git+https://github.com/eduard-kazakov/Landsat8SimpleAlbedo
```

## Description

## Examples

```python
from Landsat8SimpleAlbedo.AlbedoRetriever import AlbedoRetriever

a = AlbedoRetriever(metadata_file='F:/LC08_L1TP_182019_20190830_20190903_01_T1/LC08_L1TP_182019_20190830_20190903_01_T1_MTL.txt',
                    temp_dir='F:/',
                    albedo_method='tasumi',
                    correction_method='dos')

a.save_albedo_as_gtiff('F:/LC08_L1TP_182019_20190830_20190903_01_T1/tasumi_dos_albedo.tif')
```

```python
from Landsat8SimpleAlbedo.AlbedoRetriever import AlbedoRetriever

a = AlbedoRetriever(metadata_file='F:/LC08_L1TP_182019_20190830_20190903_01_T1/LC08_L1TP_182019_20190830_20190903_01_T1_MTL.txt',
                    angles_file='F:/LC08_L1TP_182019_20190830_20190903_01_T1/LC08_L1TP_182019_20190830_20190903_01_T1_ANG.txt',
                    temp_dir='F:/LC08_L1TP_182019_20190830_20190903_01_T1/temp',
                    albedo_method='olmedo',
                    correction_method='srem',
                    usgs_utils='F:/software/l8_angles/l8_angles.exe',
                    cygwin_bash_exe_path='C:/cygwin64/bin/bash.exe',
                    )

a.save_albedo_as_gtiff('F:/LC08_L1TP_182019_20190830_20190903_01_T1/olmedo_srem_albedo.tif')
```
```python
from Landsat8SimpleAlbedo.AlbedoRetriever import AlbedoRetriever

a = AlbedoRetriever(metadata_file='F:/LC08_L1TP_182019_20190830_20190903_01_T1/LC08_L1TP_182019_20190830_20190903_01_T1_MTL.txt',
                    albedo_method='beg',
                    correction_method='raw',
                    dem_file='F:/LC08_L1TP_182019_20190830_20190903_01_T1/DEM.tif')

a.save_albedo_as_gtiff('F:/LC08_L1TP_182019_20190830_20190903_01_T1/beg_raw_albedo.tif')
```
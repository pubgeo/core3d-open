# CORE3D Open Evaluation Baseline Solution

## Competition Overview

The [CORE3D Open Evaluation](https://competitions.codalab.org/competitions/33641) CodaLab competition offers a public leaderboard to track progress toward accurate urban 3D building modeling with satellite images. IARPA’s CORE3D program has released satellite image data to enable public research, hosted by [SpaceNet on AWS](https://spacenet.ai/core3d/). JHU/APL has developed a baseline solution combining open source projects from Kitware and Cornell, discussed in this [IGARSS'21 paper](https://arxiv.org/abs/2107.04622). Detailed instructions are provided below for reproducing our baseline results.

## Metric Evaluation

For metric evaluation, 3D models must be provided as a 50cm raster Digital Surface Model (DSM) with valid height values (integer decimeters) for buildings and a raster classification (CLS) map indicating which pixels are labeled building. Submissions will be evaluated with an intersection over union (IOU) score with true positives requiring semantic correctness, height correctness (within one meter), and roof slope correctness (within five degrees). Examples are provided in the CodaLab competition bundle. Instructions are provided below for formatting files for submission.

## Terms and Conditions

This competition is provided as a public leaderboard only. All input data is available separately in the [CORE3D data set](https://spacenet.ai/core3d/). No prizes of any kind will be awarded.

Any scientific publication using the data shall refer to the following paper:

```
@inproceedings{hagstrom2021igarss,
	author={S. Hagstrom and H. W. Pak and S. Ku and S. Wang and G. Hager and M. Brown},
	booktitle={2021 IEEE Geoscience and Remote Sensing Symposium}, 
	title={Cumulative assessment for urban 3d modeling}, 
	year={2021}
}
```

## Acknowledgements

This work was supported by the Intelligence Advanced Research Projects Activity (IARPA) contract no. 2017-17032700004. Disclaimer: The views and conclusions contained herein are those of the authors and should not be interpreted as necessarily representing the official policies or endorsements, either expressed or implied, of IARPA or the U.S. Government.

We thank the developers of VisSat and Danesfield for their assistance and advice in facilitating our extension of their open source works.

References for open source works used to develop this baseline solution are cited below:

```
@inproceedings{Leotta_2019_CVPR_Workshops,
	author = {Leotta, Matthew J. and Long, Chengjiang and Jacquet, Bastien and Zins, Matthieu and Lipsa, Dan and Shan, Jie and Xu, Bo and Li, Zhixin and Zhang, Xu and Chang, Shih-Fu and Purri, Matthew and Xue, Jia and Dana, Kristin},
	title = {Urban Semantic 3D Reconstruction From Multiview Satellite Imagery},
	booktitle = {CVPRW},
	month = {June},
	year = {2019}
}

@inproceedings{VisSat19,
	title={{Leveraging Vision Reconstruction Pipelines for Satellite Imagery}},
	author={Zhang, Kai and Sun, Jin and Snavely, Noah},
	booktitle={ICCV Workshop on 3D Reconstruction in the Wild (3DRW)},
	year={2019}
}

@article{ipol.2017.179,
    title   = {{The Bilateral Filter for Point Clouds}},
    author  = {Digne, Julie and de Franchis, Carlo},
    journal = {{Image Processing On Line}},
    volume  = {7},
    pages   = {278--287},
    year    = {2017},
    doi     = {10.5201/ipol.2017.179},
}
```

## Instructions for Reproducing the Baseline Results

Please follow these instructions to reproduce our baseline results from the IGARSS paper. Baseline scores will differ slightly from those in the paper due to minor edits in the scoring function to run on CodaLab. Also, Kitware is actively developing Danesfield, so we expect other changes that will improve performance. If you find inconsistencies in our instructions versus the latest Danesfield release, please let us know and we'll try to keep this current.

### Download the competition bundle

Register for the [CodaLab](https://competitions.codalab.org/) contest and download the competition bundle. This includes detailed instructions for the competition and example submissions from the baseline solution.

### Download satellite images for the test sites from SpaceNet Data on AWS

Public satellite images for our test sites are available in the [CORE3D data set](https://spacenet.ai/core3d/) on the SpaceNet data repo on AWS, available to download at no cost.

### Clone COLMAP and VisSat repos, make a few modifications, and run on our data

* Clone the GitHub repo for COLMAP that has been adapted for [VisSat](https://github.com/Kai-46/ColmapForVisSat). Comment out the lines where ceres-solver is installed within the ubuntu1804_install_dependencies.sh script (lines 26-35). Install [ceres-solver 1.14.0](https://github.com/ceres-solver/ceres-solver/releases) (not the latest version).

* Follow the README instructions to install dependencies and install COLMAP.

* Clone the GitHub repo for [VisSat](https://github.com/Kai-46/VisSatSatelliteStereo).

* Within colmap_mvs_commands.py, add the following parameter as part of the `cmd` variable in the `run_photometeric_mvs` and `run_consistency_check` methods: `--PatchMatchStereo.max_image_size 5000`.

* Within aggregate_3d.ply, add the following parameter as part of the `cmd` variable in the `fuse` method: `--StereoFusion.min_num_pixels 2`.

* Within image_crop.py, assign `overlap_thresh` to 0.2 instead of 0.8.

* Follow the README instructions for the repo to install dependencies and run VisSat.

* The following JSONs are the configurations used in “aoi_config/MVS3DM_Explorer.json” for the Jacksonville, UCSD and Omaha test sites used for the competition:

```
Jacksonville:
{
  "dataset_dir”:<path_to_Jacksonville_images>,
  "work_dir": <path_to_working_directory>,
  "bounding_box": {
    "zone_number": 17,
    "hemisphere": "N",
    "ul_easting": 435525,
    "ul_northing": 3355525,
    "width": 1402.0,
    "height": 1448.0
  },
  "steps_to_run": {
    "clean_data": true,
    "crop_image": true,
    "derive_approx": true,
    "choose_subset": true,
    "colmap_sfm_perspective": true,
    "inspect_sfm_perspective": false,
    "reparam_depth": true,
    "colmap_mvs": true,
    "aggregate_2p5d": true,
    "aggregate_3d": true
  },
  "alt_min": -30.0,
  "alt_max": 120.0
}

UCSD:
{
  "dataset_dir": <path_to_UCSD_images>,
  "work_dir": <path_to_working_directory>,
  "bounding_box": {
    "zone_number": 11,
    "hemisphere": "N",
    "ul_easting": 477262,
    "ul_northing": 3638321,
    "width": 1003.0,
    "height": 997.0
  },
  "steps_to_run": {
    "clean_data": true,
    "crop_image": true,
    "derive_approx": true,
    "choose_subset": true,
    "colmap_sfm_perspective": true,
    "inspect_sfm_perspective": false,
    "reparam_depth": true,
    "colmap_mvs": true,
    "aggregate_2p5d": true,
    "aggregate_3d": true
  },
  "alt_min": -500.0,
  "alt_max": 500.0
}

Omaha:
{
  "dataset_dir": <path_to_Omaha_images>,
  "work_dir": <path_to_working_directory>,
  "bounding_box": {
    "zone_number": 15,
    "hemisphere": "N",
    "ul_easting": 252753,
    "ul_northing": 4573181,
    "width": 1018.0,
    "height": 977.0
  },
  "steps_to_run": {
    "clean_data": true,
    "crop_image": true,
    "derive_approx": true,
    "choose_subset": true,
    "colmap_sfm_perspective": true,
    "inspect_sfm_perspective": false,
    "reparam_depth": true,
    "colmap_mvs": true,
    "aggregate_2p5d": true,
    "aggregate_3d": true
  },
  "alt_min": 1000.0,
  "alt_max": 1500.0
}
```

### Download point cloud bilateral filter, and post-process the point clouds

* Convert the resulting .ply point cloud file into a .txt file using the following code snippet.

```
from lib.ply_np_converter import ply2np, np2ply
import csv
points, color, comments = ply2np(<path_to_ply_file>)
with open(‘converted_file.txt', 'w') as f:
    csv.writer(f, delimiter=' ').writerows(points)
```

* Fill in the gaps in the point cloud file using densify.py provided in this repo.

* Install the [point cloud bilateral filter](https://www.ipol.im/pub/art/2017/179/). Run the bilateral filter on the converted text file using the following parameters: -N 1 -r 2 -n 2

* Use LASTools to convert the resulting text file into LAS format, and also add the appropriate coordinate reference point. Example command: `wine txt2las -i filled_filtered_file.txt -utm 11S -target_utm 11S -o las_file_utm11S.las`


### Clone Kitware's Danesfield repo and run on our data

* Clone the GitHub repo for [Danesfield](https://github.com/Kitware/Danesfield).

* Run Danesfield using the converted LAS point cloud file and its corresponding images (and optionally the corresponding RPC files).

### Convert output file formats for evaluation on CodaLab

The DSM and CLS files produced are GeoTIFF, and pixel resolution can vary depending on your Danesfield options. The CodaLab evaluation function expects PNG images with geotags specified in JSON files, and pixel resolution should be 50cm. These constraints ensure that files are small and can be uploaded quickly. To convert your GeoTIFF files for submission, run the convert_for_eval.py script in this repo for each of the three test sites and then zip up the ouput nine files into submission.zip for upload.

```
python convert_for_eval.py UCSD_DSM.tif
python convert_for_eval.py OMAHA_DSM.tif
python convert_for_eval.py JAX_DSM.tif
```


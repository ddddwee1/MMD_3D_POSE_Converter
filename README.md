# MMD_3D_POSE_Converter

This tool is used to convert 17-point 3D skeleton into MMD motion (VMD) file. The code is naive and ugly but it works.

### Usage

```
1. Copy a reference vmd file for retrieve version and model information.

2. Place your 3D predictions in './pred3d/' folder, and save the file names as '%08d.mat'. Several samples are provided in the folder.

3. Edit your frame range in line 53, in convert_pose.py.

4. Edit your output filename in convert_pose.py, last line.

5. You can now import this into your MMD. Remember to 'OFF' the IK points.
```

#### License

This work is under WTFPL. 

```
You can do WHAT THE FUCK YOU WANT TO.
```

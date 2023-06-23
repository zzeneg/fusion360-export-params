# Fusion 360 - Export with parameters
Fusion 360 Add-In for exporting STLs with parameters from CSV file

Custom Add-In that helps with automatic STL export for parametrized components based on provided CSV file.
In Fusion 360 you can define your own parameters and use them in your sketches/bodies but there is no quick way to produce multiple STLs with different parameter values - you have to manually modify every parameter and export them manually one by one. This plugin solves that by reading the desired configuration from CSV file an exporting versions wtih all possible parameter combinations.

## Installation
1. Chekout or download this repo.
2. In Fusion 360 go to `UTILITIES` toolbar and click on `ADD-INS` button. 
    
    ![image](https://github.com/zzeneg/fusion360-export-params/assets/910255/9c76b509-ba86-4478-9125-3d0075d9e0d5)

3. In the opened window select `Add-Ins` tab.
4. Click green plus icon next to `My Add-Ins`. 
    
    ![image](https://github.com/zzeneg/fusion360-export-params/assets/910255/24de6cc5-51e0-4475-873a-988af343edc1)

5. Fusion 360 will open a file dialog in the default location. Go to the folder with downloaded repo and select `ExportWithParams` folder. Alternatively you can copy `ExportWithParams` folder to that default location and use it from there, whatever you prefer. Just note that if you rename/remove the folder the add-in will disappear from Fusion 360.
6. The plugin `ExportWithParams` should appear in the list. Select it and click `Run` (only for the first time, it should start automatically unless you disable that function).

    ![image](https://github.com/zzeneg/fusion360-export-params/assets/910255/ccfbe675-cbc7-4beb-8bcf-8d140cadc28c)

7. You should now see a new button next in the `ADD-INS` panel.

    ![image](https://github.com/zzeneg/fusion360-export-params/assets/910255/cd1475cc-9b31-4c0e-b8c3-1453b19fdd48)


## Usage
Create a model that uses parameters, then create a CSV file with mappings - first column is the component name, second is the parameter name used in that component, and next columns are parameter values in the form of expressions (e.g. number + unit).

For example, imagine we have a design `ExportParamsSample` where bodies in the root component uses parameters `modelSize` and `modelHeight`, and the `ChildComponent` uses `childModelWidth` parameter.

![image](https://github.com/zzeneg/fusion360-export-params/assets/910255/0741dbe4-9d61-4c01-9bda-5bf096e28f50)

In that case our CSV file may look like this:
```
ExportParamsSample, modelHeight, 20mm, 50mm
ExportParamsSample, modelSize, 50mm, 100mm
ChildComponent, childModelWidth, 20mm, 50mm, 100mm
```
`v1` suffix in the root component's name is ignored as it changes all the time.

AFter creating a CSV click an Add-In button in the UI and select
- CSV file with paramters
- Mesh Refinement level
- Output folder
  
  ![image](https://github.com/zzeneg/fusion360-export-params/assets/910255/61f19599-920c-456e-8e11-3b616776005f)

Similar to default STL export, only visible bodies will be exported.

With our sample results would be:

![image](https://github.com/zzeneg/fusion360-export-params/assets/910255/e4289f4e-eafb-419c-aba0-2a5301f6f7f0)

## Credits
<a href="https://www.flaticon.com/free-icons/stl" title="stl icons">STL icons created by Freepik - Flaticon</a>


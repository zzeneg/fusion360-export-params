from itertools import product
import re
import adsk.core
import adsk.fusion
import os
from .lib import fusion360utils as util

CMD_ID = "zzeneg_ExportWithParameters"
CMD_NAME = "Export With Parameters"
CMD_DESCRIPTION = "Export visible bodies using parameters from CSV file"

WORKSPACE_ID = "FusionSolidEnvironment"
PANEL_ID = "SolidScriptsAddinsPanel"
COMMAND_BESIDE_ID = "ScriptsManagerCommand"
# icons created by Freepik - Flaticon - https://www.flaticon.com/free-icons/stl
ICON_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources", "")

SELECT_CSV_BUTTON_ID = "SelectCSVButton"
MESH_REFINEMENT_DROPDOWN_ID = "MeshRefinementDropdown"
SELECT_EXPORT_BUTTON_ID = "SelectExportFolderButton"

_app = adsk.core.Application.get()
_ui = _app.userInterface
_local_handlers = []

_csvPath: str = None
_exportPath: str = None
_meshRefinement: int = 0


def run(context):
    try:
        workspace = _ui.workspaces.itemById(WORKSPACE_ID)
        panel = workspace.toolbarPanels.itemById(PANEL_ID)

        command_definition = _ui.commandDefinitions.itemById(CMD_ID)
        if command_definition is None:
            command_definition = _ui.commandDefinitions.addButtonDefinition(CMD_ID, CMD_NAME, CMD_DESCRIPTION, ICON_FOLDER)
            util.add_handler(command_definition.commandCreated, command_created)

        command_control = panel.controls.itemById(CMD_ID)
        if command_control is None:
            command_control = panel.controls.addCommand(command_definition, COMMAND_BESIDE_ID, False)

        command_control.isPromoted = True

    except:
        util.handle_error("run")


def stop(context):
    try:
        workspace = _ui.workspaces.itemById(WORKSPACE_ID)
        panel = workspace.toolbarPanels.itemById(PANEL_ID)

        command_control = panel.controls.itemById(CMD_ID)
        if command_control:
            command_control.deleteMe()

        command_definition = _ui.commandDefinitions.itemById(CMD_ID)
        if command_definition:
            command_definition.deleteMe()

    except:
        util.handle_error("stop")


def command_created(args: adsk.core.CommandCreatedEventArgs):
    global _csvPath, _exportPath, _meshRefinement

    inputs = args.command.commandInputs

    selectCsvButton = inputs.addBoolValueInput(SELECT_CSV_BUTTON_ID, "Select CSV", False, "", True)
    if _csvPath is not None:
        selectCsvButton.text = os.path.basename(_csvPath)

    meshRefinementDropdown = inputs.addDropDownCommandInput(
        MESH_REFINEMENT_DROPDOWN_ID, "Mesh Refinement", adsk.core.DropDownStyles.TextListDropDownStyle
    )
    meshRefinementDropdown.listItems.add("High", _meshRefinement == 0)
    meshRefinementDropdown.listItems.add("Medium", _meshRefinement == 1)
    meshRefinementDropdown.listItems.add("Low", _meshRefinement == 2)

    selectExportFolderButton = inputs.addBoolValueInput(SELECT_EXPORT_BUTTON_ID, "Export to", False, "", False)
    if _exportPath is not None:
        selectExportFolderButton.text = os.path.basename(_exportPath)

    util.add_handler(args.command.execute, command_execute, local_handlers=_local_handlers)
    util.add_handler(args.command.inputChanged, command_input_changed, local_handlers=_local_handlers)
    util.add_handler(args.command.validateInputs, command_validate_input, local_handlers=_local_handlers)
    util.add_handler(args.command.destroy, command_destroy, local_handlers=_local_handlers)


def command_execute(args: adsk.core.CommandEventArgs):
    global _csvPath, _exportPath, _meshRefinement

    design = adsk.fusion.Design.cast(_app.activeProduct)
    bodies = getBodies(design.rootComponent, [])
    util.log("BODIES: " + str(list(map(lambda x: f"{x[1]}_{x[0].name}", bodies))), force_console=True)

    csvValues = parseCsv(_csvPath)
    util.log("CSV COMBINATIONS: " + str(csvValues), force_console=True)

    for body, componentName in bodies:
        exportBody(body, componentName, csvValues.get(componentName), _exportPath, _meshRefinement)


def command_input_changed(args: adsk.core.InputChangedEventArgs):
    global _csvPath, _exportPath, _meshRefinement

    input = args.input
    inputs = args.inputs

    if input.id == SELECT_CSV_BUTTON_ID:
        _csvPath = selectCsv()
        if _csvPath is not None:
            selectFileButton = adsk.core.BoolValueCommandInput.cast(inputs.itemById(SELECT_CSV_BUTTON_ID))
            selectFileButton.text = os.path.basename(_csvPath)
    elif input.id == SELECT_EXPORT_BUTTON_ID:
        _exportPath = selectFolder()
        if _exportPath is not None:
            selectExportFolderButton = adsk.core.BoolValueCommandInput.cast(inputs.itemById(SELECT_EXPORT_BUTTON_ID))
            selectExportFolderButton.text = os.path.basename(_exportPath)
    elif input.id == MESH_REFINEMENT_DROPDOWN_ID:
        meshRefinementDropdown = adsk.core.DropDownCommandInput.cast(inputs.itemById(MESH_REFINEMENT_DROPDOWN_ID))
        _meshRefinement = meshRefinementDropdown.selectedItem.index


def command_validate_input(args: adsk.core.ValidateInputsEventArgs):
    global _csvPath, _exportPath

    args.areInputsValid = _csvPath is not None and _exportPath is not None


def command_destroy(args: adsk.core.CommandEventArgs):
    global _local_handlers
    _local_handlers = []


def selectFolder() -> str:
    folderDialog = _ui.createFolderDialog()
    folderDialog.title = "Select Export Folder"
    dialogResult = folderDialog.showDialog()
    if dialogResult == adsk.core.DialogResults.DialogOK:
        return folderDialog.folder


def selectCsv() -> str:
    fileDialog = _ui.createFileDialog()
    fileDialog.title = "Select CSV"
    fileDialog.filter = "*.csv"
    dialogResult = fileDialog.showOpen()
    if dialogResult == adsk.core.DialogResults.DialogOK:
        return fileDialog.filename


def parseCsv(csvPath: str) -> dict[str, list[tuple[tuple[str, str], ...]]]:
    csvValues: dict[str, dict[str, list[str]]] = {}

    for csvLine in open(csvPath):
        csvLineParts = csvLine.split(",")
        bodyName = csvLineParts[0].strip()
        paramName = csvLineParts[1].strip()
        paramValues = map(lambda x: x.strip(), csvLineParts[2::])
        csvValues.setdefault(bodyName, {})[paramName] = paramValues

    util.log("csv values: " + str(csvValues))
    csvValueCombinations: dict[str, list[tuple(str, str)]] = {}

    for bodyName, bodyParams in csvValues.items():
        bodyParamCombinations = {}
        for bodyParam, paramValues in bodyParams.items():
            bodyParamCombinations[bodyParam] = product([bodyParam], paramValues)

        bodyParamCombinations = list(product(*bodyParamCombinations.values()))
        csvValueCombinations[bodyName] = bodyParamCombinations

    return csvValueCombinations


def getBodies(component: adsk.fusion.Component, bodies: list[adsk.fusion.BRepBody]) -> list[tuple[adsk.fusion.BRepBody, str]]:
    if component.isBodiesFolderLightBulbOn:
        for body in component.bRepBodies:
            if body.isLightBulbOn:
                sanitizedName = re.sub(r" v\d$", "", component.name).strip()
                bodies.append((body, sanitizedName))
    for occurrence in component.occurrences:
        if occurrence.isLightBulbOn and not occurrence.isReferencedComponent:
            bodies = getBodies(occurrence.component, bodies)

    return bodies


def exportBody(
    body: adsk.fusion.BRepBody, componentName: str, paramCombinations: list[tuple[tuple[str, str], ...]], folder: str, meshRefinement: int
):
    design = adsk.fusion.Design.cast(_app.activeProduct)
    exportManager = design.exportManager
    userParameters = design.userParameters

    stlOptions = exportManager.createSTLExportOptions(body)
    stlOptions.meshRefinement = meshRefinement

    changedParameters = {}
    if paramCombinations is not None:
        util.log(f"EXPORT BODY WITH PARAMS: {componentName}_{body.name} - {str(paramCombinations)}", force_console=True)
        for paramCombination in paramCombinations:
            fileName = f"{componentName}_{body.name}"
            for param in paramCombination:
                paramName = param[0]
                paramValue = param[1]
                userParameter = userParameters.itemByName(paramName)
                if userParameter is not None:
                    if paramName not in changedParameters:
                        changedParameters[paramName] = userParameter.expression
                    userParameter.expression = paramValue
                    fileName = "_".join([fileName, paramName, str(paramValue)])
            fileName = os.path.normpath(os.path.join(folder, f"{fileName}.stl"))
            util.log(f"exporting to: {fileName}")
            stlOptions.filename = fileName
            adsk.doEvents()
            exportManager.execute(stlOptions)

        for key, value in changedParameters.items():
            userParameter = userParameters.itemByName(key)
            userParameter.expression = value

    else:
        util.log(f"EXPORT BODY: {componentName}_{body.name}", force_console=True)
        fileName = f"{componentName}_{body.name}.stl"
        fileName = os.path.normpath(os.path.join(folder, fileName))
        util.log(f"exporting to: {fileName}")
        stlOptions.filename = fileName
        adsk.doEvents()
        exportManager.execute(stlOptions)

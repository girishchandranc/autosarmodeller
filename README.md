[![Build Actions Status](https://github.com/girishchandranc/autosarfactory/workflows/Build/badge.svg)](https://github.com/girishchandranc/autosarfactory/actions)
# Autosar Modelling Tool
AutosarFactory provides nice methods to read/create/modify AUTOSAR compliant arxml files.

## How to use
- Clone the repository.
- Manually install the package.
    
    $ python setup.py install
> use `python3` if you have both `python2` and `python3` installed.

- Import the package `autosarfactory` to your python script.
- And, finally have fun with modelling AUTOSAR.

### Reading file
```python
files = ['component.arxml', 'datatypes.arxml']
root, status = autosarfactory.read(files)
```
The read method processes the input files and return the root node(with merged info of all the given files). The status gives an info if the file reading was successful.

### Creating new file
```python
newPack = autosarfactory.new_file('newFile.arxml', defaultArPackage = 'NewPack')
```
Creates a new arxml file with the given package name and returns the ARPackage object.
- If package name is not provided, default package name 'RootPackage' is used. 
- The method raises FileExistsError if the given file already exist. To avoid this, please pass the argument overWrite as True.

### Accessing attributes and references
Model elements have `get_<attribute/reference>` methods to access existing attribute and reference value.
> For multi-references, the method returns a list of values

### Modifying attributes/references
All the elements have `set_<attribute/reference>`methods to modify the attribute or reference value.
> For multi-references, there also exists methods `add_<reference>`, `remove_<reference>`

### Adding new model elements
All the parent classes have `new_<element>` methods to create an element.
```python
rootPack = autosarfactory.new_file('newFile.arxml', defaultArPackage = 'RootPack')
newPack = rootPack.new_ARPackage('NewPack')
#new applicaton component
asw1 = newPack.new_ApplicationSwComponentType('asw1')
asw1.new_PPortPrototype('outPort')

#new senderRecever interface
srIf = newPack.new_SenderReceiverInterface('srif1')
srIf.new_DataElement('de1')
```
### Accessing elements by path
Once the file is read by the tool, its possible to access elements by path.
```python
files = ['component.arxml', 'datatypes.arxml']
autosarfactory.read(files)
swc = autosarfactory.get_node('/Swcs/asw1')
uint8DataType = autosarfactory.get_node('/DataTypes/baseTypes/uint8')
```

### Saving options
#### Save
The tool provides `save` method to save the changes made to the model.
```python
files = ['component.arxml', 'datatypes.arxml']
autosarfactory.read(files)

rootPack = autosarfactory.new_file('newFile.arxml', defaultArPackage = 'RootPack')
newPack = rootPack.new_ARPackage('NewPack')

#new applicaton component
newcomp = newPack.new_ApplicationSwComponentType('newcomponent')
newcomp.new_PPortPrototype('outPort')

#new senderRecever interface
srIf = newPack.new_SenderReceiverInterface('srif1')
srIf.new_DataElement('de1')

#save changes
autosarfactory.save(['newFile.arxml'])
```
The `save` method accepts a list of file which needs to be saved. If no argument is provided, all the files(input, newly created) will be saved.

#### SaveAs
The tool provides `saveAs` method to save the changes made to the model into a single arxml file.
```python
files = ['component.arxml', 'datatypes.arxml']
autosarfactory.read(files)

rootPack = autosarfactory.new_file('newFile.arxml', defaultArPackage = 'RootPack')
newPack = rootPack.new_ARPackage('NewPack')

#new applicaton component
newcomp = newPack.new_ApplicationSwComponentType('newcomponent')
newcomp.new_PPortPrototype('outPort')

#new senderRecever interface
srIf = newPack.new_SenderReceiverInterface('srif1')
srIf.new_DataElement('de1')

#save changes
autosarfactory.saveAs('mergedFile.arxml')
```

### Autosar visualizer
The package also includes a graphical visualizer for the Autosar models which can be simply opened by passing the autosar root to the method `show_in_ui`.
For example:
```python
files = ['component.arxml', 'datatypes.arxml']
root,status = autosarfactory.read(files)
autosar_ui.show_in_ui(root)
```

Please see below a screenshot of the visualizer.

![AutosarVisualizer-2021-01-22 143059](https://user-images.githubusercontent.com/55708936/105509642-61e3ae00-5cd6-11eb-8a47-f45b8e44d683.jpg)


The visualizer mainly consists of 4 views.
- Autosar Explorer - A simple tree which shows all elements in the model.
- Property view - Info about property and its corresponding values of the selected element in autosar explorer.
- Referenced by view - This views list elements which references the selected element in autosar explorer.
- Search view - Provision to search any elements in the model. The type of search can be selected through a combobox at the top of the view. (Currently only searching by short name is implemented;this is planned to be extended in the future with other types of search e.g. search by refference, regular expressions...). 

## Examples
Please check the script inside the `Examples` folder which creates a basic communication matrix. 

For more information on the usage, please refer `tests/test_autosarmodel.py`.

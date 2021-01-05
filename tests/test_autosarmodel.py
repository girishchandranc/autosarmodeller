import os, sys, shutil
import pytest, filecmp

mod_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, mod_path)

from autosarmodeller import autosarmodeller

resourcesDir = os.path.join(os.path.dirname(__file__), 'resources')

input_files = [os.path.join(resourcesDir, 'components.arxml'), 
               os.path.join(resourcesDir, 'datatypes.arxml'),
               os.path.join(resourcesDir, 'interfaces.arxml')]

invalid_files = [os.path.join(resourcesDir, 'invalid.arxml')]

def teardown():
    """ teardown any state that was previously setup.
    """
    autosarmodeller.reinit()
    assert (autosarmodeller.get_root() is None), 'Root should be None'

def test_model_load_invalid_input():
    """
    Tests if the model is not loaded when invalid files are passed.
    """
    root, status = autosarmodeller.read(invalid_files)
    assert (root is None), 'Root should be None'
    assert (status is False), 'status is False for invalid file'
    teardown()

def test_model_load():
    """
    Tests if the model is properly loaded when arxml files are passed.
    """
    root, status = autosarmodeller.read(input_files)
    assert (root is not None), 'Root should not be None'
    assert (status), 'status is True when the file is loaded properly'
    assert (len(root.get_arPackages()) > 0), 'arpackages count should be greater than 0'
    teardown()

def test_model_create_new_file():
    """
    Tests if the new autosar file is properly created.
    """
    packageName = 'myPack_12345'
    filePath = os.path.join(resourcesDir, 'newFile.arxml')

    arPackage = autosarmodeller.create_new_file(filePath,overWrite=True,defaultArPackage=packageName)
    assert (arPackage is not None), 'ArPackage should not be None'
    assert (arPackage.name == packageName), 'ArPackage should be '+ packageName
    assert (os.path.isfile(filePath)), 'File should exist'
    teardown()

def test_model_access():
    """
    Tests if the root node contans the merged entities from all files(input and created).
    """
    root, status = autosarmodeller.read(input_files)
    assert (root is not None), 'root should not be None'
    assert (len(root.get_arPackages()) == 3), '3 Ar-packages expected'
    
    swcPackage = next((x for x in root.get_arPackages() if x.name == 'Swcs'), None)
    assert (swcPackage is not None), 'swcPackage should not be None'
    assert (len(swcPackage.get_elements()) == 3), '3 elements expected'

    asw1 = next((x for x in swcPackage.get_elements() if x.name == 'asw1'), None)
    asw2 = next((x for x in swcPackage.get_elements() if x.name == 'asw2'), None)
    Comp = next((x for x in swcPackage.get_elements() if x.name == 'Comp'), None)

    assert (asw1 is not None), 'asw1 should not be None'
    assert(isinstance(asw1, autosarmodeller.ApplicationSwComponentType)), 'asw1 should be an instance of ApplicationSwComponentType'
    assert (asw2 is not None), 'asw2 should not be None'
    assert(isinstance(asw2, autosarmodeller.ApplicationSwComponentType)), 'asw2 should be an instance of ApplicationSwComponentType'
    assert (Comp is not None), 'Comp should not be None'
    assert(isinstance(Comp, autosarmodeller.CompositionSwComponentType)), 'Comp should be an instance of CompositionSwComponentType'

    ifPackage = next((x for x in root.get_arPackages() if x.name == 'Interfaces'), None)
    assert (ifPackage is not None), 'ifPackage should not be None'
    assert (len(ifPackage.get_elements()) == 1), '1 element expected'
    
    srIf = next((x for x in ifPackage.get_elements() if x.name == 'srif1'), None)
    assert (srIf is not None), 'srIf should not be None'
    assert (isinstance(srIf, autosarmodeller.SenderReceiverInterface)), 'should be an instance of SenderReceiverInterface'

    assert (len(srIf.get_dataElements()) == 1), '1 element expected'
    vdp = next((x for x in srIf.get_dataElements() if x.name == 'de1'), None)
    assert (vdp is not None), 'vdp should not be None'
    assert (isinstance(vdp, autosarmodeller.VariableDataPrototype)), 'should be an instance of VariableDataPrototype'

    teardown()

def test_model_path():
    """
    Tests if the path returns the node.
    """
    autosarmodeller.read(input_files)
    asw1 = autosarmodeller.get_node('/Swcs/asw1')
    assert (asw1 is not None), 'asw1 should not be None'
    assert(isinstance(asw1, autosarmodeller.ApplicationSwComponentType)), 'asw1 should be an instance of ApplicationSwComponentType'
    assert (asw1.name == 'asw1'), 'name should be asw1'

    vdp = autosarmodeller.get_node('/Interfaces/srif1/de1')
    assert (vdp is not None), 'vdp should not be None'
    assert(isinstance(vdp, autosarmodeller.VariableDataPrototype)), 'vdp should be an instance of VariableDataPrototype'
    assert (vdp.name == 'de1'), 'name should be de1'

def test_model_reference():
    """
    Tests if the referenced nodes are properly read from the file.
    """
    autosarmodeller.read(input_files)
    port = autosarmodeller.get_node('/Swcs/asw1/outPort')
    assert (port is not None), 'port should not be None'
    assert(isinstance(port, autosarmodeller.PPortPrototype)), 'port should be an instance of PPortPrototype'

    srIf = port.get_providedInterface()
    assert (srIf is not None), 'srIf should not be None'
    assert(isinstance(srIf, autosarmodeller.SenderReceiverInterface)), 'srIf should be an instance of SenderReceiverInterface'
    assert (srIf.path == '/Interfaces/srif1'), 'path should be /Interfaces/srif1'

    vdp = next(iter(srIf.get_dataElements()))
    refType = vdp.get_type()
    assert (refType is not None), 'refType should not be None'
    assert(isinstance(refType, autosarmodeller.ImplementationDataType)), 'refType should be an instance of ImplementationDataType'
    assert (refType.name == 'uint8'), 'name should be uint8'
    assert (refType.path == '/DataTypes/ImplTypes/uint8'), 'path should be /DataTypes/ImplTypes/uint8'

    baseType = next(iter(refType.get_swDataDefProps().get_swDataDefPropsVariants())).get_baseType()
    assert (baseType is not None), 'baseType should not be None'
    assert(isinstance(baseType, autosarmodeller.SwBaseType)), 'baseType should be an instance of SwBaseType'
    assert (baseType.name == 'uint8'), 'name should be uint8'
    assert (baseType.path == '/DataTypes/baseTypes/uint8'), 'path should be /DataTypes/baseTypes/uint8'
    teardown()

def test_model_read_attributes():
    """
    Tests if the attributes are properly read from the file.
    """
    autosarmodeller.read(input_files)
    te = autosarmodeller.get_node('/Swcs/asw1/beh1/te_5ms')
    assert (te is not None), 'te should not be None'
    assert(te.get_period(), 0.005), 'value of period should be 0.005'

    vdp = autosarmodeller.get_node('/Interfaces/srif1/de1')
    assert (vdp is not None), 'vdp should not be None'
    assert(isinstance(vdp.get_initValue(), autosarmodeller.NumericalValueSpecification)), 'init value should be an instance of NumericalValueSpecification'
    assert(vdp.get_initValue().get_value().get() == '1'), 'init value should be 1'

def test_model_modify():
    """
    Tests if the elements in the model can be modified
    """
    autosarmodeller.read(input_files)
    te = autosarmodeller.get_node('/Swcs/asw1/beh1/te_5ms')
    assert (te is not None), 'te should not be None'
    assert(te.get_period(), 0.005), 'value of period should be 0.005'
    te.set_period(2000)
    assert(te.get_period(), 2000), 'value of period should be 2000'

def test_model_create_entity():
    """
    Tests if the elements can be created and added to the model
    """
    autosarmodeller.read(input_files)
    pack = autosarmodeller.get_node('/Interfaces')
    assert (isinstance(pack, autosarmodeller.ARPackage)), 'should be instance of ARPackage'

    csif = pack.create_ClientServerInterface('csif')
    op1 = csif.create_Operation('op1')
    arg1 = op1.create_Argument('arg1')
    arg1.set_type(autosarmodeller.get_node('/DataTypes/ImplTypes/uint8'))

    assert (len(pack.get_elements()) == 2), '2 elements expected'
    csInterafce = next((x for x in pack.get_elements() if x.name == 'csif'), None)
    assert (csInterafce is not None), 'csInterafce should not be None'
    assert (isinstance(csInterafce, autosarmodeller.ClientServerInterface)), 'should be an instance of ClientServerInterface'
    assert(csInterafce.path, '/Interfaces/csif'), 'path should be /Interfaces/csif'

    assert (len(csInterafce.get_operations()) == 1), '1 operation expected'
    operation = next(iter(csInterafce.get_operations()))
    assert (isinstance(operation, autosarmodeller.ClientServerOperation)), 'should be an instance of ClientServerOperation'
    assert(operation.name, 'op1'), 'name should be op1'
    assert(operation.path, '/Interfaces/csif/op1'), 'path should be /Interfaces/csif/op1'

    assert (len(operation.get_arguments()) == 1), '1 argument expected'
    argument = next(iter(operation.get_arguments()))
    assert (isinstance(argument, autosarmodeller.ArgumentDataPrototype)), 'should be an instance of ArgumentDataPrototype'
    assert(argument.name, 'arg1'), 'name should be arg1'
    assert(isinstance(argument.get_type(), autosarmodeller.ImplementationDataType)), 'type should be ImplementationDataType'
    assert(argument.get_type().path, '/DataTypes/ImplTypes/uint8'), 'path of type should be /DataTypes/ImplTypes/uint8'

    teardown()


def test_model_save():
    """
    Tests if the model is saved after making changes.
    """
    autosarmodeller.read(input_files)
    te = autosarmodeller.get_node('/Swcs/asw1/beh1/te_5ms')
    assert (te is not None), 'te should not be None'
    assert(te.get_period(), 0.005), 'value of period should be 0.005'
    te.set_period(2000)

    #copy the input files to a difference location and compare between the old and new files.
    componentArxml = os.path.join(resourcesDir, 'components.arxml')
    tempDir = os.path.join(resourcesDir,"temp")
    tempComponentArxml = os.path.join(tempDir, 'components.arxml')

    os.mkdir(tempDir)
    shutil.copy(componentArxml, tempDir)

    autosarmodeller.save()
    assert (filecmp.cmp(componentArxml, tempComponentArxml) is False), "files should be different"

    #copy back the originalfile
    shutil.copy(tempComponentArxml, resourcesDir)
    shutil.rmtree(tempDir)
    teardown()

def test_model_saveas():
    """
    Tests if the model is saved to a single file with saveas.
    """
    autosarmodeller.read(input_files)
    te = autosarmodeller.get_node('/Swcs/asw1/beh1/te_5ms')
    assert (te is not None), 'te should not be None'
    assert(te.get_period(), 0.005), 'value of period should be 0.005'
    te.set_period(2000)

    mergedArxml = os.path.join(resourcesDir, 'merged.arxml')
    autosarmodeller.saveAs(mergedArxml,overWrite=True)
    assert (os.path.isfile(mergedArxml)), 'file should be created after saveAs'
    os.remove(mergedArxml)
    teardown()

def test_model_read_saved_file():
    """
    Test if the value saved to the file is read back.
    """
    autosarmodeller.read(input_files)
    te = autosarmodeller.get_node('/Swcs/asw1/beh1/te_5ms')
    assert (te is not None), 'te should not be None'
    assert(te.get_period(), 0.005), 'value of period should be 0.005'
    te.set_period(2000)

    #copy the input files to a difference location and compare between the old and new files.
    componentArxml = os.path.join(resourcesDir, 'components.arxml')
    tempDir = os.path.join(resourcesDir,"temp")
    tempComponentArxml = os.path.join(tempDir, 'components.arxml')

    os.mkdir(tempDir)
    shutil.copy(componentArxml, tempDir)

    autosarmodeller.save()
    teardown()

    autosarmodeller.read([componentArxml])
    te = autosarmodeller.get_node('/Swcs/asw1/beh1/te_5ms')
    assert (te is not None), 'te should not be None'
    assert(te.get_period(), 2000), 'value of period should be 2000'
    
    #copy back the originalfile
    shutil.copy(tempComponentArxml, resourcesDir)
    shutil.rmtree(tempDir)
    teardown()

def test_model_exception_when_create_new_file():
    """
    Test if an exception is raised when the file exists during new file creation
    """
    newFile = os.path.join(resourcesDir, 'newFile.arxml')
    autosarmodeller.create_new_file(newFile, overWrite=True)

    with pytest.raises(FileExistsError) as cm:
        autosarmodeller.create_new_file(newFile)
        assert ('File {} already exists. If it needs overwriting, then please set True for argument overWrite.'.format(newFile) == str(cm.exception)) 
    
    teardown()

def test_model_exception_when_no_short_name_for_referrable_types():
    """
    Test if an exception is raised when short name is not provided for referrable types
    """
    autosarmodeller.read(input_files)
    asw1 = autosarmodeller.get_node('/Swcs/asw1')

    with pytest.raises(autosarmodeller.NoShortNameException) as cm:
        asw1.create_PPortPrototype()
        assert ('name should not be None for Referrable objects' == str(cm.exception)) 
    
    teardown()

def test_model_exception_when_invalid_child_or_ref_added():
    """
    Test if an exception is raised when an invalid child is added to a node.
    Or an invalid reference value is set.
    """
    autosarmodeller.read(input_files)
    asw1 = autosarmodeller.get_node('/Swcs/asw1')
    asw1.create_PPortPrototype('p1')

    #duplicate child addition
    with pytest.raises(autosarmodeller.InvalidRefOrChildNodeException) as cm:
        asw1.create_PPortPrototype('p1')
        assert ('Operation not possible. A node with name {} already present in {}.'.format('p1', asw1) == str(cm.exception)) 
    
    srIf = autosarmodeller.SenderReceiverInterface()
    srIf.name = 'srIf'
    
    #invaid child addition
    with pytest.raises(autosarmodeller.InvalidRefOrChildNodeException) as cm:
        asw1.add_port(srIf)
        assert ('Operation not possible. {} should be an instance of PortPrototype or its sub-classes'.format(srIf) == str(cm.exception)) 

    te = autosarmodeller.get_node('/Swcs/asw1/beh1/te_5ms')
    #invalid refeerence setting
    with pytest.raises(autosarmodeller.InvalidRefOrChildNodeException) as cm:
        te.set_startOnEvent(srIf)
        assert ('Operation not possible. {} should be an instance of RunnableEntity or its sub-classes'.format(srIf) == str(cm.exception)) 

    teardown()

"""
def test_model_create():
    #rootNode = autosarmodeller.read(files)
    dtPack = autosarmodeller.create_new_file('dataTypes.arxml', defaultArPackage = 'DataTypes', overWrite = True)
    baseTypePack = dtPack.create_ARPackage('baseTypes')
    uint8BaseType = baseTypePack.create_SwBaseType('uint8')

    implTypePack = dtPack.create_ARPackage('ImplTypes')
    uint8 = implTypePack.create_ImplementationDataType('uint8')
    uint8.create_SwDataDefProps().create_SwDataDefPropsVariant().set_baseType(uint8BaseType)
    
    ifPack = autosarmodeller.create_new_file('interface.arxml', defaultArPackage = 'Interfaces', overWrite = True)
    srIf = ifPack.create_SenderReceiverInterface('srif1')
    vdp = srIf.create_DataElement('de1')
    vdp.set_type(uint8)
    vdp.create_NumericalValueSpecification().create_Value().set('1')
    
    swcPack = autosarmodeller.create_new_file('components.arxml', defaultArPackage = 'Swcs', overWrite = True)
    asw1 = swcPack.create_ApplicationSwComponentType('asw1')
    port1 = asw1.create_PPortPrototype('outPort')
    port1.set_providedInterface(srIf)

    beh1 = asw1.create_InternalBehavior('beh1')
    te1 = beh1.create_TimingEvent('te_5ms')
    te1.set_period(0.005)
    
    run1 = beh1.create_Runnable('Runnable_1')
    run1.set_symbol('Run1')
    te1.set_startOnEvent(run1)
    
    dsp = run1.create_DataSendPoint('dsp')
    var = dsp.create_AccessedVariable().create_AutosarVariable()
    var.set_portPrototype(port1)
    var.set_targetDataPrototype(vdp)

    asw2 = swcPack.create_ApplicationSwComponentType('asw2')
    port2 = asw2.create_RPortPrototype('inPort')
    port2.set_requiredInterface(srIf)

    beh2 = asw2.create_InternalBehavior('beh1')
    dre = beh2.create_DataReceivedEvent('DRE_Vdp')
    data = dre.create_Data()
    data.set_contextRPort(port2)
    data.set_targetDataElement(vdp)
    
    run2 = beh2.create_Runnable('Runnable_2')
    run2.set_symbol('Run2')
    dre.set_startOnEvent(run2)
    
    dra = run2.create_DataReceivePointByArgument('dra')
    var_dra = dra.create_AccessedVariable().create_AutosarVariable()
    var_dra.set_portPrototype(port2)
    var_dra.set_targetDataPrototype(vdp)

    # composition and connectors.
    composition = swcPack.create_CompositionSwComponentType('Comp')
    asw1_proto = composition.create_Component('asw1_proto')
    asw2_proto = composition.create_Component('asw2_proto')
    asw1_proto.set_type(asw1)
    asw2_proto.set_type(asw2)

    conn1 = composition.create_AssemblySwConnector('conn1')
    provider = conn1.create_Provider()
    provider.set_contextComponent(asw1_proto)
    provider.set_targetPPort(port1)
    required = conn1.create_Requester()
    required.set_contextComponent(asw2_proto)
    required.set_targetRPort(port2)

    canNetworkPack = autosarmodeller.create_new_file('CanNetwork.arxml', defaultArPackage = 'Can', overWrite = True)
    signalsPack = canNetworkPack.create_ARPackage('signals')
    systemsignalsPack = canNetworkPack.create_ARPackage('systemsignals')
    syssig1 = systemsignalsPack.create_SystemSignal('syssig1')

    sig1 = signalsPack.create_ISignal('sig1')
    sig1.set_length(4)
    sig1.set_dataTypePolicy(autosarmodeller.DataTypePolicyEnum.VALUE_LEGACY)
    sig1.set_iSignalType(autosarmodeller.ISignalTypeEnum.VALUE_PRIMITIVE)
    sig1.set_systemSignal(syssig1)

    ecuPack = canNetworkPack.create_ARPackage('ecus')
    ecu1 = ecuPack.create_EcuInstance('ecu1')

    sysPack = canNetworkPack.create_ARPackage('system')
    system = sysPack.create_System('CanSystem')
    sysMapping = system.create_Mapping('Mappings')
    srMapping = sysMapping.create_SenderReceiverToSignalMapping('outportToSig1Mapping')
    srMapping.set_systemSignal(syssig1)
    mapDe = srMapping.create_DataElement()
    mapDe.set_contextPort(port1)
    mapDe.set_targetDataPrototype(vdp)

    rootComp = system.create_RootSoftwareComposition('rootSwcom')
    rootComp.set_softwareComposition(composition)

    swctoEcuMp = sysMapping.create_SwMapping('SwcMapping')
    swctoEcuMp.set_ecuInstance(ecu1)
    swcMap1 = swctoEcuMp.create_Component()
    swcMap1.set_contextComposition(rootComp)
    swcMap1.add_contextComponent(asw1_proto)
    swcMap1.add_contextComponent(asw2_proto)
    


    autosarmodeller.save()
    autosarmodeller.saveAs('merged.arxml', overWrite = True)

    print('yes')

"""
"""
def test_load_created_model():
    rootNode = autosarmodeller.read(['merged.arxml'])
    print('yes')
"""
"""
def test_large_model_load():
    rootNode = autosarmodeller.read(large_files)
    print('yes')
"""
from src.config import SimulationConfig, quantity_unit_stripper
from src.boilerplate_manager import BoilerplateManager
from src.parameter_editor import ParameterEditor
from src.spectrum_generator import SpectrumGenerator
from src.run_preparer import RunPreparer
from src.simulation_runner import SimulationRunner


class Orchestrator:
    def __init__(self, project_root: str) -> None:
        self.project_root = project_root
        self.boilerplate_manager = BoilerplateManager(project_root)

    def run_dicom_simulation(self, config: SimulationConfig) -> str:
        self.boilerplate_manager.reset_tmp()
        editor = ParameterEditor(config)
        editor.edit_main_file(self.boilerplate_manager.get_headsource_path())
        editor.edit_sub_file(self.boilerplate_manager.get_tmp_path("patientDICOM.txt"))
        voltage, _ = quantity_unit_stripper(config.imaging.anode_voltage)
        exposure, _ = quantity_unit_stripper(config.imaging.exposure)
        histories = str(
            int(config.imaging.sequential_times) * int(config.general.histories)
        )
        SpectrumGenerator.generate(voltage, exposure, histories, self.project_root)
        preparer = RunPreparer(self.project_root)
        rundir = preparer.prepare_dicom_run(config)
        SimulationRunner.run_dicom(config.general.topas_directory, rundir)
        return rundir

    def run_ctdi_simulation(self, config: SimulationConfig) -> str:
        self.boilerplate_manager.reset_tmp()
        editor = ParameterEditor(config)
        editor.edit_main_file(self.boilerplate_manager.get_headsource_path())
        voltage, _ = quantity_unit_stripper(config.imaging.anode_voltage)
        exposure, _ = quantity_unit_stripper(config.imaging.exposure)
        SpectrumGenerator.generate(
            voltage, exposure, config.general.histories, self.project_root
        )

        phantom_size_num = config.ctdi.phantom_size.split()[0]
        phantom_file = "CTDIphantom_" + phantom_size_num + ".txt"
        editor.edit_sub_file(self.boilerplate_manager.get_tmp_path(phantom_file))

        preparer = RunPreparer(self.project_root)
        rundir = preparer.prepare_ctdi_run(config)

        commands = preparer._generate_plug_files(
            config.ctdi.phantom_size, rundir, config.general.topas_directory
        )
        SimulationRunner.run_ctdi(config.general.topas_directory, rundir, commands)
        return rundir

    def prepare_only(self, config: SimulationConfig) -> str:
        self.boilerplate_manager.reset_tmp()
        editor = ParameterEditor(config)
        editor.edit_main_file(self.boilerplate_manager.get_headsource_path())

        if config.imaging.simulation_type == "DICOM":
            editor.edit_sub_file(
                self.boilerplate_manager.get_tmp_path("patientDICOM.txt")
            )
            voltage, _ = quantity_unit_stripper(config.imaging.anode_voltage)
            exposure, _ = quantity_unit_stripper(config.imaging.exposure)
            histories = str(
                int(config.imaging.sequential_times) * int(config.general.histories)
            )
            SpectrumGenerator.generate(voltage, exposure, histories, self.project_root)
            preparer = RunPreparer(self.project_root)
            return preparer.prepare_dicom_run(config)
        else:
            voltage, _ = quantity_unit_stripper(config.imaging.anode_voltage)
            exposure, _ = quantity_unit_stripper(config.imaging.exposure)
            SpectrumGenerator.generate(
                voltage,
                exposure,
                config.general.histories,
                self.project_root,
            )
            phantom_size_num = config.ctdi.phantom_size.split()[0]
            phantom_file = "CTDIphantom_" + phantom_size_num + ".txt"
            editor.edit_sub_file(self.boilerplate_manager.get_tmp_path(phantom_file))
            preparer = RunPreparer(self.project_root)
            rundir = preparer.prepare_ctdi_run(config)
            preparer._generate_plug_files(
                config.ctdi.phantom_size, rundir, config.general.topas_directory
            )
            return rundir

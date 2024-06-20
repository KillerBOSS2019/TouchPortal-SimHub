from plugin import Plugin, EntryGenerator, PluginCategories, Language
import requests
from TouchPortalAPI import TYPES
import json
from threading import Thread
from time import sleep, time

entry = EntryGenerator()

@entry.plugin_info(api=7, version=100, name="SimHub", id="killerboss2019.TouchPortalSimHub")
@entry.add_configuration(colorDark="#19647E", colorLight="#28AFB0", parentCategory=PluginCategories.games)
@entry.add_start_cmd(system="windows", cmd="%TP_PLUGIN_FOLDER%TouchPortalSimHub\\TP_SimHub.exe")
@entry.create_category(id="simhub", name="SimHub", imagepath="%TP_PLUGIN_FOLDER%TouchPortalSimHub//simhub.png")
class TouchPortalSimHub(Plugin):
    brake = entry.create_state(id="brake", type="text", desc="Brake", category="Brakes", default="0")
    brakes_temperature_avg = entry.create_state(id="brakes_temperature_avg", type="text", desc="Brakes Temperature Avg", category="Brakes", default="0")
    brakes_temperature_max = entry.create_state(id="brakes_temperature_max", type="text", desc="Brakes Temperature Max", category="Brakes", default="0")
    brakes_temperature_min = entry.create_state(id="brakes_temperature_min", type="text", desc="Brakes Temperature Min", category="Brakes", default="0")
    brakes_temperature_frontleft = entry.create_state(id="brakes_temperature_frontleft", type="text", desc="Brakes Temperature Front Left", category="Brakes", default="0")
    brakes_temperature_frontright = entry.create_state(id="brakes_temperature_frontright", type="text", desc="Brakes Temperature Front Right", category="Brakes", default="0")
    brakes_temperature_rearleft = entry.create_state(id="brakes_temperature_rearleft", type="text", desc="Brakes Temperature Rear Left", category="Brakes", default="0")
    brakes_temperature_rearright = entry.create_state(id="brakes_temperature_rearright", type="text", desc="Brakes Temperature Rear Right", category="Brakes", default="0")

    best_lap_time = entry.create_state(id="best_lap_time", type="text", desc="Best Lap Time", default="00:00:00")
    all_time_best = entry.create_state(id="all_time_best", type="text", desc="All Time Best", default="00:00:00")

    car_damage1 = entry.create_state(id="car_damage1", type="text", desc="Car Damage 1", category="Car Damage", default="0")
    car_damage2 = entry.create_state(id="car_damage2", type="text", desc="Car Damage 2", category="Car Damage", default="0")
    car_damage3 = entry.create_state(id="car_damage3", type="text", desc="Car Damage 3", category="Car Damage", default="0")
    car_damage4 = entry.create_state(id="car_damage4", type="text", desc="Car Damage 4", category="Car Damage", default="0")
    car_damage5 = entry.create_state(id="car_damage5", type="text", desc="Car Damage 5", category="Car Damage", default="0")
    car_damage_avg = entry.create_state(id="car_damage_avg", type="text", desc="Car Damage Avg", category="Car Damage", default="0")
    car_damage_max = entry.create_state(id="car_damage_max", type="text", desc="Car Damage Max", category="Car Damage", default="0")
    car_damage_min = entry.create_state(id="car_damage_min", type="text", desc="Car Damage Min", category="Car Damage", default="0")

    car_model = entry.create_state(id="car_model", type="text", desc="Car Model", default="Unknown")
    clutch = entry.create_state(id="clutch", type="text", desc="Clutch", default="0")

    completed_laps = entry.create_state(id="completed_laps", type="text", desc="Completed Laps", default="0")
    current_lap = entry.create_state(id="current_lap", type="text", desc="Current Lap", default="0")
    current_lap_time = entry.create_state(id="current_lap_time", type="text", desc="Current Lap Time", default="00:00:00")

    fuel = entry.create_state(id="fuel", type="text", desc="Fuel", default="0")
    fuel_percent = entry.create_state(id="fuel_percent", type="text", desc="Fuel Percent", default="0")
    throttle = entry.create_state(id="throttle", type="text", desc="Throttle", default="0")
    gear = entry.create_state(id="gear", type="text", desc="Gear", default="0")

    def __init__(self):
        super().__init__(self.__plugin_info__.get("id"))
        self.on(TYPES.onConnect, self.on_connect)

        self.control_mapper_roles = []
        self.updated_roles = False

    def populate_roles(self):
        try:
            response = requests.get("http://localhost:8888/api/ControlMapper/GetRoles")
        except requests.exceptions.ConnectionError:
            print("SimHub not running")
            return
        
        print("roles status code: ", response.status_code)
        if response.status_code == 200 and not self.updated_roles:
            self.control_mapper_roles = json.loads(response.text)
            self.choiceUpdate("killerboss2019.TouchPortalSimHub.trigger_mapper_role.simhub_role", self.control_mapper_roles)
            self.updated_roles = True

    def on_connect(self, data):
        print("Starting TouchPortal SimHub Plugin")

        if not self.control_mapper_roles:
            self.populate_roles()

        print("Starting state update thread")
        Thread(target=self.state_update).start()

    def update_states(self, data):
        self.stateUpdate(self.brake, data.get("brake", "0"))
        self.stateUpdate(self.brakes_temperature_avg, data.get("brakesTemperatureAvg", "0"))
        self.stateUpdate(self.brakes_temperature_max, data.get("brakesTemperatureMax", "0"))
        self.stateUpdate(self.brakes_temperature_min, data.get("brakesTemperatureMin", "0"))
        self.stateUpdate(self.brakes_temperature_frontleft, data.get("brakesTemperatureFrontLeft", "0"))
        self.stateUpdate(self.brakes_temperature_frontright, data.get("brakesTemperatureFrontRight", "0"))
        self.stateUpdate(self.brakes_temperature_rearleft, data.get("brakesTemperatureRearLeft", "0"))
        self.stateUpdate(self.brakes_temperature_rearright, data.get("brakesTemperatureRearRight", "0"))

        self.stateUpdate(self.best_lap_time, data.get("bestLapTime", "00:00:00"))
        self.stateUpdate(self.all_time_best, data.get("allTimeBest", "00:00:00"))

        self.stateUpdate(self.car_damage1, data.get("carDamage1", "0"))
        self.stateUpdate(self.car_damage2, data.get("carDamage2", "0"))
        self.stateUpdate(self.car_damage3, data.get("carDamage3", "0"))
        self.stateUpdate(self.car_damage4, data.get("carDamage4", "0"))
        self.stateUpdate(self.car_damage5, data.get("carDamage5", "0"))
        self.stateUpdate(self.car_damage_avg, data.get("carDamageAvg", "0"))
        self.stateUpdate(self.car_damage_max, data.get("carDamageMax", "0"))
        self.stateUpdate(self.car_damage_min, data.get("carDamageMin", "0"))

        self.stateUpdate(self.car_model, data.get("carModel", "Unknown"))
        self.stateUpdate(self.clutch, data.get("clutch", "0"))

        self.stateUpdate(self.completed_laps, data.get("completedLaps", "0"))
        self.stateUpdate(self.current_lap, data.get("currentLap", "0"))
        self.stateUpdate(self.current_lap_time, data.get("currentLapTime", "00:00:00"))

        self.stateUpdate(self.fuel, data.get("fuel", "0"))
        self.stateUpdate(self.fuel_percent, data.get("fuelPercent", "0"))
        self.stateUpdate(self.throttle, data.get("throttle", "0"))
        self.stateUpdate(self.gear, data.get("gear", "0"))

    def state_update(self):
        # print("testing state update")
        start_time = time()
        while self.isConnected():
            # if time() - start_time > 300:
            #     self.disconnect()
            #     break
            url = "http://localhost:8888/Api/GetGameData"
            try:
                # print("Attmeping to get data")
                response = requests.get(url)
            except requests.exceptions.ConnectionError:
                continue
            
            # print("state_update status code: ", response.status_code)
            if not response.status_code == 200:
                continue

            if not self.populate_roles:
                self.populate_roles()

            data = json.loads(response.text)
            # print(data)
            self.update_states(data)
            sleep(0.1)
            
            

    def trigger_role(self, trigger):
        base_url = "http://localhost:8888/api/ControlMapper/"
        press_url = base_url + "StartRole/"
        release_url = base_url + "StopRole/"

        request_form_data = {
            "roleName": trigger,
            "ownerId": self.__plugin_info__.get("id")
        }
        press = requests.post(press_url, data=request_form_data)
        release = requests.post(release_url, data=request_form_data)
        print(f"Triggered role {trigger}")

    @entry.add_format(language=Language.English, format="Trigger Control Mapper $[simhub_role]")
    @entry.add_data(id="simhub_role", type="choice", valueChoices=[""], default="")
    @entry.add_action(category="simhub", id="trigger_mapper_role", name="Trigger Control Mapper Role")
    def trigger_mapper_role(self, data):
        role = data.get("simhub_role")
        if not role:
            print("No role selected")
            return
        print(data, "triggering role")
        self.trigger_role(role)
    

touchportal_simhub = TouchPortalSimHub()
if __name__ == "__main__":
    touchportal_simhub.connect()
else:
    TP_PLUGIN_INFO = touchportal_simhub.__entry__["TP_PLUGIN_INFO"]
    TP_PLUGIN_CATEGORIES = touchportal_simhub.__entry__["TP_PLUGIN_CATEGORIES"]
    TP_PLUGIN_ACTIONS = touchportal_simhub.__entry__["TP_PLUGIN_ACTIONS"]
    TP_PLUGIN_STATES = touchportal_simhub.__entry__["TP_PLUGIN_STATES"]
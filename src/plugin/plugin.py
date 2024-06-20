from TouchPortalAPI import Client
from TouchPortalAPI import TYPES
from .EntryHandler import EntryHandler

class action:
    data: dict = {}
    type: str = "action"
    actionId: str = ""
    entry: dict = {}

    def __init__(self, entry):
        self.entry = entry

        self.data = self.__process_data(entry.get("data", []))
        self.type = entry.get("type", "action")
        self.actionId = entry.get("actionId", "")

    def __process_data(self, data: dict):
        action_data = {}

        for d in data:
            action_data[d.get("id")] = d.get("value")
        
        return action_data

    def get(self, key: str):
        for k, v in self.data.items():
            if k.split(".")[-1] == key:
                return v
    
    def __str__(self):
        return f"Action: {self.actionId} with data: {self.data}"

class Plugin(Client):
    def __init__(self, pluginId: str):
        super().__init__(pluginId)
        self.__entry__ = {}
        self.__action_handlers__ = {}
        self.__setting_handlers__ = {}

        self.finalize_entry()
        self.generate_action_handlers()

        self.on(TYPES.onAction, self.action_handler)
        self.on(TYPES.onConnect, self.on_connect_handler)
        self.on(TYPES.onSettingUpdate, lambda data: self.setting_handler(data.get("values", [])))

    def generate_action_handlers(self):
        for func in dir(self):
            if (func := getattr(self, func)) and callable(func):
                if "__actions__" in dir(func):
                    data = func.__actions__
                    self.__action_handlers__[data.get("id")] = func

    def setting_handler(self, data: dict):
        for setting in data:
            key, value = list(setting.items())[0]
            self.__setting_handlers__[key] = value

    def action_handler(self, data: dict):
        action_id = data.get("actionId")
        if action_id in self.__action_handlers__:
            self.__action_handlers__[action_id](action(data))

    def on_connect_handler(self, data: dict):
        self.setting_handler(data.get("settings", []))
        ...

    def finalize_entry(self):
        entry_handler = EntryHandler()
        self.__entry__ = entry_handler.generate(self)

    def settingUpdate(self, setting: callable, settingValue: str):
        """Update a setting value
        
        Allows developers to update a setting value using settings that you have decorated with the @entry.add_setting decorator.
        """
        settingName = setting.__setting__["name"]
        return super().settingUpdate(settingName, settingValue)
    
    def getSettings(self, setting: callable):
        """Get a setting value
        
        Allows developers to get a setting value using settings that you have decorated with the @entry.add_setting decorator.
        """
        settingName = setting.__setting__["name"]
        return self.__setting_handlers__.get(settingName, "")
    
    def stateUpdate(self, state:dict, stateValue: str):
        stateId = state.get("id")

        return super().stateUpdate(stateId, stateValue)
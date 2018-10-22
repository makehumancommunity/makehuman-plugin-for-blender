from .sync_ops import SyncOperator

class FetchServerData(SyncOperator):
    def __init__(self, functionName, readyFunction, expectBinary=False, params=None):
        super().__init__(functionName)
        self.readyFunction = readyFunction
        self.binary = expectBinary
        self.executeJsonCall(expectBinaryResponse=expectBinary, params=params)

    def callback(self, json_obj):
        if self.binary:
            self.readyFunction(json_obj)
        else:
            self.readyFunction(json_obj.data)

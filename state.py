class StateNode():
    """
    Класс для хранения состояния обходов одного космического аппарата.
    * name - совпадает с номером космического аппарата
    * isVisited - булева переменная, использующаяся при обходах
    * hopCount - массив (число шлюзов) * (число эпох), содержащий расстояние до шлюза в конкретную эпоху
    * pathToGateway - список из (число эпох) массивов, содержащих ближайший путь до шлюза 
                      в конкретную эпоху
    """
    def __init__(self, spacecraftName, epochCount, gatewayCount):
        self.name = spacecraftName
        self.isVisited = False
        self.hopCount = [[0 for j in range(epochCount)] for i in range(gatewayCount)]
        self.pathToGateway = [[] for i in range(epochCount)]

    def __str__(self):
        return f"Node_{self.name}: {self.hopCount}, {self.pathToGateway}"

class GroupState():
    """
    Класс, хранящий информацию о результатах и состояниях обходов орбитальной группировки.
    Объединяет несколько экземпляров класса StateNode.
    * nodeList - массив из состояний всех космических аппаратов орбитальной группировки
    * currentEpoch - номер текущей эпохи
    * currentGateway - номер шлюза, до которого ищутся расстояния
    """
    def __init__(self, spacecraftCount, epochCount, gatewayCount):
        self.nodeList = [StateNode(name, epochCount, gatewayCount)
                         for name in range(1, spacecraftCount + 1)]
        self.currentEpoch = 0
        self.currentGateway = 0

    def __getitem__(self, nodeName):
        return self.nodeList[nodeName - 1]

    def updateNode(self, nodeName, **kwargs):
        node = self[nodeName]
        for key, value in kwargs.items():
            if key == "hopCount":
                node.hopCount[self.currentGateway][self.currentEpoch] = value
            elif key == "pathToGateway":
                node.pathToGateway[self.currentEpoch] = value
            elif key == "isVisited":
                node.isVisited = value
            else:
                raise ValueError(F"Incorrect attribute {key}")

    def __str__(self):
        stringList = [str(node) for node in self.nodeList]
        return "\n".join(stringList)

    def clearVisits(self):
        for node in self.nodeList:
            node.isVisited = False

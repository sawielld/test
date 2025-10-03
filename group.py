import numpy as np
from state import GroupState

class Spacecraft():
    """
    Класс, содержащий информацию об одном космическом аппарате.
    * name - номер аппарата
    * connections - массив из номеров аппаратов, с которыми он связан
    * gateway - номер шлюза, с которым связан аппарат (0, если связей нет)
    """
    def __init__(self, name, connections=[], gateway=0):
        self.name = name
        self.connections = connections
        self.gateway = gateway

    def update(self, connections=[], gateway=0):
        self.connections = connections
        self.gateway = gateway

    def __str__(self):
        stringData = f"Spacecraft_{self.name}: connections {self.connections}, gateway {self.gateway}"
        return stringData

class OrbitalGroup():
    """
    Класс для хранения информации обо всех космических аппаратах.
    Объединяет несколько экземпляров класса Spacecraft.
    * spacecraftList - массив из всех космических аппаратов (Spacecraft)
    * spacecraftCount - колличество аппаратов
    * epochCount - количество эпох, на которые создаётся группировка
    * gatewayCount - число шлюзовых станций
    * state - экземпляр класс GroupState, хранящий информацию об обходах и путях
    """
    def __init__(self, *, spacecraftCount, epochCount, gatewayCount):
        self.spacecraftList = [Spacecraft(name) for name in range(1, spacecraftCount + 1)]
        self.spacecraftCount = spacecraftCount
        self.epochCount = epochCount
        self.gatewayCount = gatewayCount
        self.state = GroupState(spacecraftCount, epochCount, gatewayCount)

    def __getitem__(self, spacecraftName):
        return self.spacecraftList[spacecraftName - 1]

    def __str__(self):
        stringList = [str(spacecraft) for spacecraft in self.spacecraftList]
        return "\n".join(stringList)

    def update(self, *, namedConnectionList, gatewayList):
        if len(namedConnectionList) != self.spacecraftCount \
                or len(gatewayList) != self.spacecraftCount:
            raise ValueError("Spacecraft and gateway connection lists have inappropraite lengths")
        for spacecraft, connections, gateway in \
                        zip(self.spacecraftList, namedConnectionList, gatewayList):
            spacecraft.update(connections, gateway)

    def updateFromTables(self, *, unitConnectionSquare, gatewayList):
        spacecraftCount = self.spacecraftCount
        namesSquare = np.repeat(np.arange(1, spacecraftCount + 1).reshape(1, spacecraftCount),
                          spacecraftCount,
                          axis=0)
        namedConnectionSquare = unitConnectionSquare * namesSquare
        namedConnectionList = [oneSpacecraftConnection[oneSpacecraftConnection != 0].tolist()
                               for oneSpacecraftConnection in namedConnectionSquare]
        self.update(namedConnectionList=namedConnectionList, gatewayList=gatewayList.tolist())

    def findPathsToTheGateway(self, gatewayName, epochNumber):
        """
        Ключевая функция поиска расстояний от всех аппаратов до конкретного шлюза.
        Параллельно обновляются пути к ближайшему шлюзу.
        """
        self.state.clearVisits()
        self.state.currentGateway = gatewayName - 1
        self.state.currentEpoch = epochNumber
        bfsQueue = []
        # В начале обхода в очередь добавляются вершины на расстоянии 1
        for spacecraft in self.spacecraftList:
            if spacecraft.gateway == gatewayName:
                bfsQueue.append(spacecraft.name)
                self.state.updateNode(nodeName=spacecraft.name,
                                      isVisited=True,
                                      hopCount=1,
                                      pathToGateway=[-gatewayName])

        while (len(bfsQueue) > 0):
            # Достаём из очереди предка
            ancestorName = bfsQueue.pop(0)
            ancestor = self[ancestorName]
            ancestorNode = self.state[ancestorName]

            for descendantName in ancestor.connections:
                descendantNode = self.state[descendantName]
                if descendantNode.isVisited:
                    continue
                bfsQueue.append(descendantName) # Добавляем непосещённого потомка в очередь
                ancestorPath = ancestorNode.pathToGateway[epochNumber]
                ancestorHopCount = ancestorNode.hopCount[gatewayName - 1][epochNumber]

                if len(ancestorPath) + 1 < len(descendantNode.pathToGateway[epochNumber]) \
                   or len(descendantNode.pathToGateway[epochNumber]) == 0:
                    self.state.updateNode(nodeName=descendantName,
                                          isVisited=True,
                                          hopCount=ancestorHopCount + 1,
                                          pathToGateway=[ancestorName] + ancestorPath) # путь обновляется
                else:
                    self.state.updateNode(nodeName=descendantName,
                                          isVisited=True,
                                          hopCount=ancestorHopCount + 1) # путь не обновляется

    def loadHopCountToMatrix(self):
        hopCountMatrix = [node.hopCount for node in self.state.nodeList]
        return np.array(hopCountMatrix)

    def getPath(self, spacecraftName, epochNumber):
        return self.state[spacecraftName].pathToGateway[epochNumber]

    def savePathsToFile(self, filename):
        with open(filename, "w") as file:
            file.write(f"{self.spacecraftCount} {self.epochCount}\n")
            for spacecraftName in range(1, self.spacecraftCount + 1):
                for epochNumber in range(self.epochCount):
                    pathToWrite = self.getPath(spacecraftName, epochNumber)
                    for vertex in pathToWrite:
                        file.write(f"{vertex} ")
                    file.write("\n")

from group import OrbitalGroup
import numpy as np 
from numpy import genfromtxt

unitConnectionTable = genfromtxt("./islConnetivity.csv", delimiter=',', dtype=int)
gatewayTable = genfromtxt("./gatewayIdxsBySat.csv", delimiter=',', dtype=int)

# Создаём орбитальную группировку требуемого размера
spacecraftCount = unitConnectionTable.shape[0]
epochCount = gatewayTable.shape[1]
gatewayCount = 8
singlePolarGlobal = OrbitalGroup(spacecraftCount=spacecraftCount,
                       epochCount=epochCount,
                       gatewayCount=gatewayCount)

# Каждую эпоху связи в группировке обновляются, в цикле считаются расстояния до каждого шлюза
# и пути к ближайшему шлюзу
for epochNumber in range(epochCount):
    singlePolarGlobal.updateFromTables(unitConnectionSquare=
                                                unitConnectionTable[:,epochNumber * spacecraftCount: \
                                                                     (epochNumber + 1) * spacecraftCount],
                                       gatewayList=gatewayTable[:,epochNumber].reshape(-1))
    for gatewayName in range(1, gatewayCount + 1):
        singlePolarGlobal.findPathsToTheGateway(gatewayName=gatewayName, epochNumber=epochNumber)

# Записываем кратчайшие расстояния до шлюзов в массив и сохраняем в файл
hopCountResult = singlePolarGlobal.loadHopCountToMatrix()
np.save('hopCountResult.npy', hopCountResult)
# Записываем пути до ближайших шлюзов в файл
singlePolarGlobal.savePathsToFile("paths.txt")
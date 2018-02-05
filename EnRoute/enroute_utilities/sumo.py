import sumolib

def get_closest_edges(net_file_path,camerasdf,net_obj=None):
    """

    :param net_file_path: path to sumo compatible .net.xml file
    :param camerasdf: pandas dataframe of cameras
    :param net_obj: net object is already loaded it can be passed over (this method returns the obj too)
    :return returns a new camerasdf with closest edge values by using the provided net file
    :rtype: (sumo net file obj, camerasdf with closest edge)
    """

    if net_obj is None:
        mynet = sumolib.net.readNet(net_file_path)
    else:
        mynet = net_obj

    def getEdges(row, radius=100):
        lon = row[2]
        lat = row[1]
        x, y = mynet.convertLonLat2XY(lon, lat)
        edges = mynet.getNeighboringEdges(x, y, radius)
        while (len(edges) < 3):
            radius *= 2
            edges = mynet.getNeighboringEdges(x,y,radius)
        distancesAndEdges = sorted([(dist, edge) for edge, dist in edges])
        dist1, closestEdge1 = distancesAndEdges[0]
        dist2, closestEdge2 = distancesAndEdges[1]
        dist3, closestEdge3 = distancesAndEdges[2]
        return closestEdge1.getID(),closestEdge2.getID(),closestEdge3.getID()

    return mynet,camerasdf.apply(getEdges, axis=1)


def get_formatted_OD(x,camerasdf,no_of_cameras):
    """

    :param x: x vector corresponding to flat OD values
    :param camerasdf: pandas dataframe of cameras
    :param no_of_cameras: number of cameras (len(camerasdf))
    :return: a list of strings to be treated as seperate lines
    """
    #lines = ["$O;", "* From-Time To-Time", "0.00 0.30", "* Factor", "1.00", "* O/Ds:"]
    lines = ["$O;", "* From-Time To-Time", "0.00 1.00", "* Factor", "1.00", "* O/Ds:"]
    for i in range(no_of_cameras):
        cid1 = camerasdf.loc[i, "CAMERA_ID"]
        for j in range(no_of_cameras):
            st = '{:6d}\t{:6d}\t{:12.4f}'.format(cid1, camerasdf.loc[j, "CAMERA_ID"], x[i * no_of_cameras + j])
            lines.append(st)

    return lines
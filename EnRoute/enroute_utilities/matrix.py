import numpy as np
import pandas as pd


def get_distance_matrix(distdf, camerasdf):
    """
    :param distdf: pandas dataframe containing pairwise distances of cameras in its third column
    :param camerasdf: pandas dataframe containing camera definitions (used for index extraction,
                      mapping id to matrix i or j)
    :return distance matrix (numpy matrix)
    """

    _m = np.zeros((len(camerasdf), len(camerasdf)))

    def assign_values_from_cameradist_to_matrix(row):
        c1 = camerasdf[camerasdf["CAMERA_ID"] == row[0]].index[0]
        c2 = camerasdf[camerasdf["CAMERA_ID"] == row[1]].index[0]
        _m[c1, c2] = row[2]
        _m[c2, c1] = row[2]

    distdf[["CAMERA_ID_FROM", "CAMERA_ID_TO", "TIME"]].apply(assign_values_from_cameradist_to_matrix, axis=1)

    return _m


def get_A_matrix(a, pdf, no_of_cameras):
    """
    :param a: 2d list of lists correponding to shortest paths
     a[0][1]:
     [([0, 1], 22.0),
      ([0, 26, 1], 23.0),
      ([0, 30, 1], 24.0),
      ([0, 15, 1], 25.0),
      ([0, 29, 1], 25.0)]
    :param pdf: probability distribution function used to get prob of trip (based on time duration)
    :return: A matrix such that each cell[i][j] in it corresponds to the probability value of i-th segment being in
    j-th OD pair
    """
    for _list in a:
        for _idx, __list in enumerate(_list):
            _sum = 0
            for idx, _tuple in enumerate(__list):
                __list[idx] = (_tuple[0], _tuple[1],
                               pdf(_tuple[1]))  # time is in minutes, lognorm uses seconds (lognorm divided by 60)
                _sum += __list[idx][2]
            for idx, _tuple in enumerate(__list):
                __list[idx] = (_tuple[0], _tuple[1], _tuple[2] / _sum)  # value/total => ratio

    a_mtx = np.zeros((no_of_cameras ** 2, no_of_cameras ** 2))
    for _idx, _list in enumerate(a):
        for __idx, __list in enumerate(_list):
            for _tuple in (__list):
                path = _tuple[0]
                for i in range(len(path) - 1):
                    # _idx = 0, __idx = 1 => all __list elements are paths between _idx and __idx
                    a_mtx[path[i] * no_of_cameras + path[i + 1], _idx * no_of_cameras + __idx] += _tuple[2]
    return a_mtx

#If time in minutes in None flowsdf should be actually the count of cars
def get_b_vector_lognorm(flowsdf, distdf, lnpdf, time_in_minutes=None):
    temp = flowsdf.copy(deep=True)

    if time_in_minutes is not None:
        temp["Flow"] *= time_in_minutes

    # flowsdf = flowsdf.merge(camerasdf, left_on="Detector", right_on="CAMERA_ID", how="right")[["CAMERA_ID", "Flow"]]
    # flowsdf = flowsdf.fillna(0)  # to handle the cameras that may not be in this time windows but are in camerasdf
    temp["fake_key"] = 1
    cross_flows = temp.merge(temp, on="fake_key")[["Detector_x", "Flow_x", "Detector_y"]]
    cross_flows.loc[cross_flows["Detector_x"] == cross_flows["Detector_y"], "Flow_x"] = 0
    cross_flows.columns = ["D1", "Flow", "D2"]
    camera_flow_time_df = cross_flows.merge(distdf[["CAMERA_ID_FROM", "CAMERA_ID_TO", "TIME"]], how="left",
                                            left_on=["D1", "D2"], right_on=["CAMERA_ID_FROM", "CAMERA_ID_TO"])
    camera_flow_time_df = camera_flow_time_df[["D1", "D2", "Flow", "TIME"]]
    flow_time_groups = camera_flow_time_df.groupby("D1")

    # lognorm_res = pd.DataFrame(columns=["D1", "D2", "new_flow"])
    lognorm_res = []
    for name, group in flow_time_groups:
        subgroup = group.loc[group["D1"] != group["D2"]]
        index_of_self = (group[group["D1"] == group["D2"]]).index.tolist()[0]
        flow = subgroup["Flow"].iloc[0]
        subgroup["prob"] = lnpdf(subgroup["TIME"])
        subgroup["%_prob"] = (subgroup["prob"] / subgroup["prob"].sum())
        subgroup["new_flow"] = subgroup["%_prob"] * flow
        # lognorm_res = lognorm_res.append(subgroup.loc[:index_of_self, ["D1", "D2", "new_flow"]])
        # lognorm_res = lognorm_res.append(group.loc[index_of_self, ["D1", "D2", "new_flow"]])
        # lognorm_res = lognorm_res.append(subgroup.loc[index_of_self:, ["D1", "D2", "new_flow"]])
        lognorm_res.extend(subgroup.loc[:index_of_self, "new_flow"].tolist())
        lognorm_res.append(0)
        lognorm_res.extend(subgroup.loc[index_of_self:, "new_flow"].tolist())

    return lognorm_res

# def get_b_vector_inverse_distance():
# uniform_res = pd.DataFrame(columns=["D1", "D2", "new_flow"])
# for name, group in flow_time_groups:
#     subgroup = group.loc[group["D1"] != group["D2"]]
#     index_of_self = (group[group["D1"] == group["D2"]]).index.tolist()[0]
#     flow = subgroup["Flow"].iloc[0]
#     subgroup.loc[:, "1_OVER_TIME"] = 1 / subgroup["TIME"]
#     subgroup.loc[:, "%_INV_TIME"] = subgroup["1_OVER_TIME"] / subgroup["1_OVER_TIME"].sum()
#     subgroup["new_flow"] = subgroup["%_INV_TIME"] * flow
#     uniform_res = uniform_res.append(subgroup.loc[:index_of_self, ["D1", "D2", "new_flow"]])
#     uniform_res = uniform_res.append(group.loc[index_of_self, ["D1", "D2", "new_flow"]])
#     uniform_res = uniform_res.append(subgroup.loc[index_of_self:, ["D1", "D2", "new_flow"]])
# uniform_res.fillna(0, inplace=True)

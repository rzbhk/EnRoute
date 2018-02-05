from lxml import etree


def get_taz_xml_root(camerasdf):
    root = etree.Element('tazs')
    for i in camerasdf.itertuples():
        ed = i[4]+" "+i[5]+" "+i[6]
        s = str(i[1])
        root.append(etree.Element("taz", id=s, edges=ed))
    return root
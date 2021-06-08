wbc_cell_hierarchy = [
    {'is_group':True,
     'name':"Granulocytes",
     'elements':{"gn":"Neutrophil","gb":"Basophil","ge":"Eosinophil","bc":"Band cell"}},
    {'is_group':False,
     'name':"",
     'elements':{"ly":"Lymphocyte"}},
    {'is_group':False,
     'name':"Monocyte",
     'elements':{"mo":"Monocyte"}},
    {'is_group':True,
     'name':"Malignant",
     'elements':{"bl":"Blast"}},
    {'is_group':True,
     'name':"Artefacts",
     'elements':{"poor":"Incomplete WBC","multi":"Multiple WBC","null":"No WBC",
                 "dead":"No WBC","imma":"Immature RBC","reti":"Reticulocyte",
                 "dead":"Dead WBC"}}]
wbc_cell_types = {}
for k in wbc_cell_hierarchy:
    for kk in k['elements']:
        wbc_cell_types[kk] = k['elements'][kk]

rbc_cell_hierarchy = [
    {'is_group':False,
     'name':"",
     'elements':{"no":"Normal"}},
    {'is_group':False,
     'name':"",
     'elements':{"imma":"Immature RBC"}},
    {'is_group':True,
     'name':"Abnormal (same shape)",
     'elements':{"sp":"Spherocyte","tc":"Target cell"}},
    {'is_group':True,
     'name':"Abnormal (deformed)",
     'elements':{"ir":"Irregularly contracted","da":"Dacrocyte","ke":"Keratocyte",
                 "ec":"Echinocyte","el":"Eliptocyte","ac":"Acanthocyte"}},
    {'is_group':True,
     'name':"Artefacts",
     'elements':{"poor":"Incomplete RBC","multi":"Multiple RBC","null":"No RBC",
                 "pl":"Platelet/dye","npl":"Nearby platelet"}}]
rbc_cell_types = {}
for k in rbc_cell_hierarchy:
    for kk in k['elements']:
        rbc_cell_types[kk] = k['elements'][kk]

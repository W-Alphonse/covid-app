
template_restaurant = [
  {"room":"Salle 1", "zones":[
    {"zone":"Table 1"},
    {"zone":"Table 2"},
    {"zone":"Table 3"}
  ]},
  {"room":"Salle 1", "zones":[
    {"zone":"Table 4"},
    {"zone":"Table 5"}
  ]}
]

template_enterprise = [
  {"room":"Salles de réunion", "zones":[
    {"zone":"Salle 1"},
    {"zone":"Salle 2"},
    {"zone":"Salle 3"}
  ]},
  {"room":"Cantine", "zones":[
    {"zone":"Table 1"},
    {"zone":"Table 2"}
  ]},
  {"room":"Etage 3", "zones":[
    {"zone":"Bureau 301"},
    {"zone":"Bureau 302"},
    {"zone":"Bureau 303"}
  ]}
]

template_medical = [
  {"room":"Salles d'attente", "zones":[
    {"zone":"Salle 1"},
    {"zone":"Salle 2"},
    {"zone":"Salle 3"}
  ]},
  {"room":"Chambres étage 3", "zones":[
    {"zone":"301"},
    {"zone":"302"},
    {"zone":"303"}
  ]},
  {"room":"Réfectoire", "zones":[
    {"zone":"Table 1"},
    {"zone":"Table 2"}
  ]}
]

template_generic = [
  {"room":"Salle 1", "zones":[
    {"zone":"Table 1"},
    {"zone":"Table 2"},
    {"zone":"Table 3"}
  ]},
  {"room":"Etage 3", "zones":[
    {"zone":"Bureau 301"},
    {"zone":"Bureau 302"},
    {"zone":"Bureau 303"}
  ]}
]

RESTO = "RESTO"
ENTRE = "ENTRE"
ADMIN = "ADMIN"
MEDIC = "MEDIC"
AUTRE = "AUTRE"
#
TEMPLATES = {
    RESTO: template_restaurant,
    ENTRE: template_enterprise,
    ADMIN: template_enterprise,
    MEDIC: template_medical,
    AUTRE: template_generic,
}

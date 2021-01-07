from covcov.application import route_dispatcher
from covcov.infrastructure.db.database import Database

def purge_visit(nbr_days:int) -> int:
  pass


import random

# template = [
#   {"room":"Salle 1", "zones":[
#     {"zone":"Table 1"},
#     {"zone":"Table 2"},
#     {"zone":"Table 3"}
#   ]},
#   {"room":"Salles de réunion", "zones":[
#     {"zone":"Salle 1"},
#     {"zone":"Salle 2"}
#   ]}
# ]
#
# def populate_table(template):
#   rooms = template.copy()
#   for room in rooms:
#     room["room_id"] = make_id()
#     for zone in room['zones']:
#       zone["zone_id"] = make_id()
#   return rooms

def make_id(k=10):
  chars = list('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890')
  return ''.join(random.choices(chars, k=10))

def gen_room(description:str, auth_claim:dict, db: Database ) -> dict :
  room = {'id':make_id(), 'description':f'{description}', 'company_id':f'{auth_claim["sub"]}'}
  body = { 'method' : 'POST', 'room': room }
  route_dispatcher.dispatch(body, None, auth_claim , '/company_domain', db)
  return body

def gen_zone(room_id: str, description:str, auth_claim:dict, db: Database ) -> dict :
  zone = {'id':make_id(), 'description':f'{description}', 'room_id':f'{room_id}'}
  body = { 'method' : 'POST', 'zone': zone }
  route_dispatcher.dispatch(body, None, auth_claim , '/company_domain', db)
  return body


# if __name__ == '__main__':
#   # print( populate_table(template))
#   db = Database("database")
#   # 1 - Set the variables pulled out of the context
#   comp_id = '¤' + make_id()[:-1]
#   comp_name = comp_id
#   auth_claim = {'sub': comp_id,  'email': comp_name + '@gmail.com' }
#   # 2 - Set the payload
#   body = { 'method' : 'POST', 'company': {"name": f"{comp_name}" } }
#   route_dispatcher.dispatch(body, None, auth_claim , '/company_domain', db)
#   #
#   s1 = gen_room('Salle 1', auth_claim, db)
#   s2 = gen_room('Salle de réunion', auth_claim, db)
#   #
#   gen_zone(s1['room']['id'], 'Table 1', auth_claim, db)
#   gen_zone(s1['room']['id'], 'Table 2', auth_claim, db)
#   gen_zone(s1['room']['id'], 'Table 3', auth_claim, db)
#   #
#   gen_zone(s2['room']['id'], 'Salle 1', auth_claim, db)
#   gen_zone(s2['room']['id'], 'Salle 2', auth_claim, db)

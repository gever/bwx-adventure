

# create world
my_world = World()

# create locations
sidewalk = Location("Sidewalk", 
"""
You are standing in front of a large glass door.
The sign says 'Come In!'
""")

entrance_way = Location("The Entrance", "It's dusty in here, like no one has been here for a while")
intersection = Location("The Hallway", "It connects all the rooms")
bathroom = Location("The Bathroom", "This place needs a clean!")
my_room = Location("My Room",
"""
You are standing in your room, it's just as you left it 5 years ago
""")
secret_room = Location("Secret Room!", "This place is spooky")

# add locations to the world
my_world.add(sidewalk)
my_world.add(entrance_way)
my_world.add(intersection)
my_world.add(bathroom)
my_world.add(my_room)

# need to add a list of standard verbs like IN, OUT, ON, OFF, PICK_UP, PUT_DOWN, LOOK_AT, PUSH, PULL, SMELL, TASTE etc that anyone can use
# VERBS should be smart, so OPEN sets a flag that the object has been opened (if it is a container), ON tells a switch that it is now on. 

# create connections
front_door = Connection(sidewalk, entrance_way, "The Big Door", IN, OUT)
stairs = Connection(entrance_way, intersection, "The Long Stairs", UP, DOWN)
short_hall_to_bathroom = Connection(intersection, bathroom, "A Few Steps", NORTH, SOUTH)
door_to_my_room = Connection(intersection, my_room, "The Door to My Room", EAST, WEST)
secret_passage = Connection(my_room, secret_room, "A secret tunnel!", IN, OUT)
secret_passage.visible = False

# create things [thing_name, takeable_or_static, container_or_switch_or_simple, verb_message_object, ...]
door_key = Thing("key", TAKEABLE, SIMPLE, [LOOK_AT, "small tarnished brass key"], [PICK_UP, "the key is cold in your hands"], [DROP, "the key falls to the floor with a clang"], [USE, "the key makes a clicking noise in the door lock"]) 
light_switch = Thing("light switch", STATIC, SWITCH, [LOOK_AT, "it turns on the light in the room"], [ON, "the switch clicks and the room is bathed in light"], [OFF, "you are shrouded in darkness once again"])
dresser = Thing("dresser", STATIC, CONTAINER, [LOOK_AT, "the old dresser holds my clothes, and some secrets as well"]) 
dresser.opened = True # this item doesnt need to be explicitly opened, so we start out with it opened

# containers are "closed" be default, so they require an OPEN to work
top_dresser_drawer = Thing("top drawer", STATIC, CONTAINER, [LOOK_AT, "the top drawer of my dresser"], [OPEN, "the top drawer slides open"])
journal = Thing("my old journal", TAKEABLE, SIMPLE, [LOOK_AT, "my old school journal. it has only one page in it"], [OPEN, "the journal cracks open with age"], [READ, "The page reads: January first, i finally discovered the secret!"])

#put stuff in the drawer, and put the drawer in the dresser
top_dresser_drawer.put(journal)
dresser.put(top_dresser_drawer)

# place them in the world
entrance_way.put(door_key)
my_room.put(light_switch)
my_room.put(dresser)

# make relationships [required_thing, failure_string] required checks to see if the hero has the object or if the object is a switch
door_to_my_room.requires = [door_key, "The door is locked, maybe you need a key or something"]
my_room.requires = [light_switch, "You are standing in our room, but it's too dark to see anything"] 

# make the player and add them to the world
hero = Character(PLAYER)
sidewalk.add(hero)

# make a patrolling character. you cannot get passed them until they are inactive, SWAT does this automatically
spider = Character(PATROL, "Spider", short_hall_to_bathroom, [LOOK_AT, "Eeeew, there is a creepy spider hanging in front of the bathroom door"], [SWAT, "You swat at the spider and it goes away"])
short_hall_to_bathroom.add(spider)

# FOLLOWERs can maybe hold more inventory? maybe they can have traits that let them get through smaller passages, etc
dog = Character(FOLLOWER, "Your dog, Spot", hero, [LOOK_AT, "Your trusty black lab"])
sidewalk.add(dog)
'''
# maybe you can define a restriction and a failure message. 
front_door.restrict = [dog, "You are too big to fit through here, maybe a smaller creature could help?"]

# and you can tell a FOLLOWER things
> tell Spot to go in the Big Door
'''

# this gets called constantly, so kids can check state and trigger events
def update():
    global door_key, journal, secret_passage, secret_room
    
    # you can check to see if there are certain items in the inventory
    if (inventory_contains(door_key, journal))
        print("You hear a rumbling from the other side of the room, you see a secret passage!")
        secret_passage.visible = True

    # you can check to see if the hero has entered a room
    if (entering_room(secret_room))
        print("You hear a rumbling behind you, there is no way to get back to your room!")
        secret_passage.visible = False
        
    

# start the game
my_world.run(update)


import json

#Base class for all objects in the game that can be interacted with, such as items and rooms
class GameObject:
    def __init__(self, name, description):
        self.name = name
        self.description = description


    def interact(self, player):
        print(f"You look at the {self.name}: {self.description}")





#This class represents items in the game that the player can pick up and use
class Item(GameObject):
    def __init__(self, name, description, use_text):
        super().__init__(name, description)
        self.use_text = use_text


    def use(self, player):
        print(self.use_text)





#Represents a room in the game where the player can move, see items, and explore
class Room:
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.items = []
        self.exits = {}


    def describe(self):
        print(f"\n{self.name}")
        print(self.description)
        if self.items:
            print("You see:")
            for item in self.items:
                print(f"- {item.name}")
        print("Exits: " + ", ".join(self.exits.keys()) if self.exits else "Exits: None")


    def add_item(self, item):
        self.items.append(item)


    def connect(self, direction, room):
        self.exits[direction] = room





#Represents the player in the game. Tracks the player’s current location, inventory, and actions like moving, picking up items, and using items.
class Player:
    def __init__(self, starting_room):
        self.current_room = starting_room
        self.inventory = []


    def move(self, direction):
        if direction in self.current_room.exits:
            self.current_room = self.current_room.exits[direction]
            self.current_room.describe()
            return f"Player moved {direction} to {self.current_room.name}"
        else:
            print("You can't go that way.")
            return "Invalid move attempt."
        

    def pick_up(self, item_name):
        for item in self.current_room.items:
            if item.name.lower() == item_name:
                self.inventory.append(item)
                self.current_room.items.remove(item)
                print(f"You picked up the {item.name}.")
                return f"Player picked up {item.name}"
        print("That item isn't here.")
        return "Item not found."
    

    def use_item(self, item_name):
        for item in self.inventory:
            if item.name.lower() == item_name:
                item.use(self)
                return f"Player used {item.name}"
        print("You don't have that item.")
        return "Item not in inventory."





#Manages the game state, including rooms, player interactions, logging, and saving/loading game states.
class Game:
    def __init__(self):         #initializes the game’s state
        self.log_file = "gamelog.txt"
        self.clear_log()
        self.item_bank = {
            "Key": Item("Key", "An old key.", "You used the key. You found a HEAD in the drawer and scream!"),
            "Book": Item("Book", "A diary.", "You read the book. It seems to have some hidden spells."),
            "Flashlight": Item("Flashlight", "It flickers.", "You turn it on. The light is very weak."),
            "Coin": Item("Coin", "A strange old coin.", "You examine the ancient coin. It has a faint mark of a cross."),
            "Lantern": Item("Lantern", "Smells like oil.", "You light the lantern. Seems to be brighter than the flashlight."),
            "Map": Item("Map", "Shows a hidden room.", "You study the map. It looks like the basement is beneath the kitchen.")
        }
        self.rooms = self.create_world()
        self.player = Player(self.rooms["Foyer"])


#clears (or initializes) the game log file, essentially starting a fresh log when the game is run
    def clear_log(self):
        try:
            with open(self.log_file, "w") as f:
                f.write("=== Game Log: Echoes of Adkins House ===\n")
        except Exception:
            pass


#writes a message to the game log file. It appends the message passed as an argument to the log file.
    def log(self, message):
        try:
            with open(self.log_file, "a") as f:
                f.write(message + "\n")
        except Exception:
            pass



#creates the world of the game. It creates rooms like Foyer, Library, Kitchen, etc., and then connects them to each other using the connect() method.
    def create_world(self):
        foyer = Room("Foyer", "A dusty entrance hall.")
        library = Room("Library", "Old books surround you.")
        kitchen = Room("Kitchen", "A terrible smell lingers.")
        basement = Room("Basement", "Dark and cold. You hear something moving in the corner and the door shuts behind you...")
        attic = Room("Attic", "A creaky attic full of cobwebs.")
        dining = Room("Dining Room", "The table is set... but for whom?")
        secret = Room("Secret Study", "A hidden room filled with notes and maps.")


        # Connections
        foyer.connect("north", library)
        library.connect("south", foyer)
        library.connect("up", attic)
        attic.connect("down", library)

        library.connect("east", kitchen)
        kitchen.connect("west", library)
        kitchen.connect("down", basement)
        # No exits in Basement room
    
        foyer.connect("south", dining)
        dining.connect("north", foyer)
        dining.connect("east", secret)
        secret.connect("west", dining)



        # Items
        foyer.add_item(self.item_bank["Flashlight"])
        library.add_item(self.item_bank["Book"])
        kitchen.add_item(self.item_bank["Key"])
        attic.add_item(self.item_bank["Lantern"])
        dining.add_item(self.item_bank["Coin"])
        secret.add_item(self.item_bank["Map"])

        return {
            "Foyer": foyer,
            "Library": library,
            "Kitchen": kitchen,
            "Basement": basement,
            "Attic": attic,
            "Dining Room": dining,
            "Secret Study": secret
        }





#saves the current state of the game (e.g., player's current room, inventory, and room items) to a JSON file (savegame.json).
    def save_game(self):
        try:
            data = {
                "current_room": self.player.current_room.name,
                "inventory": [item.name for item in self.player.inventory],
                "room_items": {
                    name: [item.name for item in room.items] for name, room in self.rooms.items()
                }
            }
            with open("savegame.json", "w") as f:
                json.dump(data, f)
            print("Game saved.")
            self.log("Game saved.")
        except Exception as e:
            print("Save error:", e)
            self.log(f"Save error: {e}")





#loads the saved game state from savegame.json. It restores the player's current room, inventory, and the items present in each room.
    def load_game(self):
        try:
            with open("savegame.json", "r") as f:
                data = json.load(f)

            self.player.current_room = self.rooms.get(data.get("current_room"), self.rooms["Foyer"])
            self.player.inventory = [
                self.item_bank[name] for name in data.get("inventory", []) if name in self.item_bank
            ]
            for room_name, itemlist in data.get("room_items", {}).items():
                room = self.rooms.get(room_name)
                if room:
                    room.items = [
                        self.item_bank[name] for name in itemlist if name in self.item_bank
                    ]

            print("Game loaded.")
            self.log("Game loaded.")
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print("Load error:", e)
            self.log(f"Load error: {e}")
        except Exception as e:
            print("Unexpected load error:", e)
            self.log(f"Unexpected load error: {e}")





#displays the list of available commands that the player can enter during the game, such as move, look, pick up, use, save, load, and quit.
    def show_menu(self):
        print("\nCommands:")
        print("- move north/south/east/west/up/down")
        print("- look")
        print("- pick up [item]")
        print("- use [item]")
        print("- save")
        print("- load")
        print("- quit")







#main game loop 
    def run(self):
        print("Echoes of Adkins' House")
        self.player.current_room.describe()
        self.show_menu()

        while True:
            try:
                command = input("\n> ").lower().strip()

                if command.startswith("move "):
                    direction = command[5:].strip()
                    msg = self.player.move(direction)
                    self.log(msg)



                elif command == "look":
                    self.player.current_room.describe()
                    self.log("Player looked.")



                elif command.startswith("pick up"):
                    item_name = command[8:].strip()
                    if item_name:
                        msg = self.player.pick_up(item_name)
                        self.log(msg)
                    else:
                        print("You must specify an item to pick up.")



                elif command.startswith("use"):
                    item_name = command[4:].strip()
                    if item_name:
                        msg = self.player.use_item(item_name)
                        self.log(msg)
                    else:
                        print("You must specify an item to use.")



                elif command == "save":
                    self.save_game()



                elif command == "load":
                    self.load_game()



                elif command == "quit":
                    print("Thanks for playing!")
                    self.log("Player quit.")
                    break

                else:
                    print("Unknown command.")



            except (KeyboardInterrupt, EOFError):
                print("\nGame interrupted. Exiting...")
                self.log("Game interrupted.")
                break


            except Exception as e:
                print("An unexpected error occurred.")
                self.log(f"Runtime error: {e}")


if __name__ == "__main__":
    Game().run()

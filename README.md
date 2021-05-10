# PokeChain
A blockchain to play pokemon as a community

Hackathon project from Thurs 5/6/21 - Mon

Concept idea is to make a bot that presses controller inputs based on ending characters of the block hash. Anyone with the chain could run their own emulator and playback the run. 
Additionally, the run could be streamed to everyone by a single node on platforms such as Twitch, YouTube, and Facebook Live.
The controller input generators are known, i.e. ending in an 'a' presses 'left' on the dpad. Controller inputs are distributed evenly across the character set
Through this, participants could vote with their compute power for control of the character
Efficient mining will lead to random walk inputs. I have no idea how efficient random walk is at beating video games.


Current Features:
Decentralized nodes
Miner software that can mine randomly or for specific button inputs
Execute keyboard inputs based on block hashes
Dynamically scaling difficulty to target a specific average blocks per second

Coming Next:
External ip address discovery
Improvements to node registration and sharing of known nodes

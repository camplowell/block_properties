# Block Properties Utility
A utility to generate block.properties files for Optifine and IRIS shaders.

## The Library
The repository contains a large collection of preset tags that may be useful to shader developers. You can mix and match them  

### Bool tags
Many tags only have two real options: yes or no.

### Enum properties
Sometimes, it's a bit more granular. For example, some blocks are the bottom half of a tall plant. Others are the top half. A single block cannot be both, but they both sway.

### Special Cases
Sometimes, individual blocks need individual handling. They should have their own ID, but that shouldn't prevent the rest of your logic from detecting its other features.
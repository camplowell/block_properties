# Block Properties Utility
A utility to generate block.properties files for Optifine and IRIS shaders.

## The Library
The repository contains a large collection of preset tags that may be useful to shader developers.
You can mix and match them when generating block IDs for a specific shaderpack.

Included is a program that can be used to more easily query and edit the library.

Example Usages:
```
echo Create a new enumerated tag:
./library tag create sway -v lower upper full

echo Add blocks to the enum property
./library blocks minecraft:grass minecraft:tallgrass:half=lower -a sway:lower

echo Query the library
./library query sway:lower
```

### Bool tags
Many tags only have two real options: yes or no.

### Enum properties
Sometimes, it's a bit more granular. For example, some blocks are the bottom half of a tall plant. Others are the top half. A single block cannot be both, but they both sway.

## The Exporter
A `properties_config.json` file tells the exporter how to generate two files:
a `block.properties` file and a glsl decoder.
The decoder exposes a number of functions specified in the config to determine if a given ID matches each of the flags you specified in the decoder.

The query program supports a number of ways to combine the tags specified in the library:

`+` includes blocks that appear in either.  
`-` includes blocks that appear on the left, but not on the right.  
`&` includes blocks that appear in both the left and right inputs.  
`^` includes blocks that appear in either, but not both.

For a complete example of the configuration file, see `example/properties_config.json`
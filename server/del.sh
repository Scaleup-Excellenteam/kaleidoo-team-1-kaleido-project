# Remove all files from Audio directory
find ./Data/Data_Dumper/Audio/ -type f -exec rm {} +

# Remove all files from Video directory
find ./Data/Data_Dumper/Video/ -type f -exec rm {} +

# Remove all files from Text directory
find ./Data/Data_Dumper/Text/ -type f -exec rm {} +

# Remove all files from Garbage directory
find ./Data/Garbage/ -type f -exec rm {} +

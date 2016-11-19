# assetInfo

The assetInfo dict contains information about an asset, in practise data extracted when parsing an asset file.

The dict contains keys stemming from a few different sources:

* Keys in the body of the parsed file (for example obj_file in a clothes asset)
* Keys from the comment header of the parsed file (for example license)
* The raw unparsed data
* A few calculated or constant convenience keys

If an asset file has not set a key, the key is still available in the dict, but its value is set to None.

## Body keys

The following keys are always present for all types of assets:

* name -- the name of the asset, as set in the asset file
* uuid -- the unique hex identifier for the asset

### Proxy type assets

If the asset is a proxy type asset (for proxymesh, clothes, hair...), the following keys are also set

* basemesh -- version of basemesh, in practice always "hm08"
* obj_file -- The (usually relative) path to the object file
* max_pole -- The max pole setting
* z_depth
* x_scale
* y_scale
* z_scale

## Comment section keys

* license
* homepage
* author

## Raw data keys

Note that these might have been stripped if the strip argument was set to true in the openAssetFile() call.

* rawlines -- an array of the entire asset file, split into lines at newline
* rawkeys -- an array of all lines looking like keys, split at the first whitespace. Ie any line starting with a character and having at least a space in it.
* rawcommentkeys - same as rawkeys, but for lines starting with a #

## Calculated and convenience keys

* absolute path -- the full, absolute path to the asset
* type -- asset actual type (ie "proxy" for all types of clothes for example)
* extension -- for example .mhclo for clothes files
* basename -- the asset filename without path
* thumb_file -- absolute path to thumb file or None if not existing
* pertinentKeys -- an array with the names of all keys that would be relevant for this type of asset, whether they were set in the asset file or not
* pertinentCommentKeys -- same as pertinentKeys but for the comment section



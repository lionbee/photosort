# photosort

Sort photos into directories using Exif information.

## Usage

`./sort.py source target`

target cannot be a sub directory of the source folder

Files are sorted into the following structure.

`<target>/<exif year>/<exif month>/<exif day>_<exif time>_<original file name>`

Using this format each month contains all the photos taken in that month in chronologial order.

#!/usr/bin/python
"""helper script for calculating offset for binocular stimulus presentation
"""
import argparse
import pandas as pd
import os.path as op


def csv_to_binocular_offset(ipd_csv, subject_name, units='pix'):
    """Compute the binocular offset from the ipd_correction.csv file

    The ipd_correction.csv file contains all the information for the
    subjects we've run, and this little helper function will load it in
    and give you the average (horizontal, vertical) offset, in
    ``units``, for ``subject_name``.

    This gives the difference between their centers that you should
    use. It's up to you how exactly to do this, but I recommend moving
    the image in one eye forward by half this amount and the other
    backward by half this amount (separately for horizontal and
    vertical)

    Parameters
    ----------
    ipd_csv : str or pandas.DataFrame
        Either the DataFrame object containing this information or the
        path to the csv file containing the DataFrame
    subject_name : str
        The name of the subject to find the average binocular offset for
    units : {'pix', 'deg'}
        Whether to give the binocular offset in pixels or degrees

    Returns
    -------
    binocular_offset : list
        List of 2 ints (if ``units=='pix'``) or floats (if
        ``units=='deg'``) specifying the offset between the two images
        that you should be using for this subject. Note that since this
        is an average, the pixel value will probably not be an integer;
        in that case, you'll need to convert it to one yourself.

    """
    if isinstance(ipd_csv, str):
        ipd_csv = pd.read_csv(ipd_csv)
    ipd_csv = ipd_csv.query("subject_name==@subject_name")
    binocular_offset = [ipd_csv["ipd_correction_%s_horizontal" % units].mean(),
                        ipd_csv["ipd_correction_%s_vertical" % units].mean()]
    return binocular_offset


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=("Compute the binocular offset from the ipd_correction.csv file. The "
                     "ipd_correction.csv file contains all the information for the subjects we've"
                     " run, and this little helper function will load it in and give you the "
                     "average (horizontal, vertical) offset, in ``units``, for ``subject_name``."
                     "This script prints the difference between their centers that you should use"
                     ". It's up to you how exactly to do this, but I recommend moving the image in"
                     " one eye forward by half this amount and the other backward by half this "
                     "amount (separately for horizontal and vertical). Note that since this is an"
                     " average, the pixel value will probably not be an integer; in that case you"
                     "'ll need to convert it to one yourself"),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("subject_name", help="Name of the subject")
    parser.add_argument('--ipd_csv', '-i', help='Path to the ipd_correction.csv file',
                        default=op.expanduser("C:/Users/danielgurman/OneDrive - Meta/Documents/GitHub/margaret-river/haploscope_utils/ipd_correction.csv"))
    parser.add_argument('--units', '-u', default='pix',
                        help=("{pix, deg}. Whether to give the binocular offset in pixels or "
                              "degrees"))
    offset = csv_to_binocular_offset(**vars(parser.parse_args()))
    print("Horizontal: %s\nVertical: %s" % (offset[0], offset[1]))

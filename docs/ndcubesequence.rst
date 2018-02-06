==============
NDCubeSequence
==============

`~ndcube.NDCubeSequence` is a class for handling multiple
`~ndcube.NDCube` objects as though they were one contiguous data set.
Another way of thinking about it is that `~ndcube.NDCubeSequence`
provides the ability to manipulate a data set described by multiple
separate WCS transformations.

Regarding implementation, and `~ndcube.NDCubeSequence` instance is
effectively a list of `~ndcube.NDCube` instances with some helper
methods attached.

Initialization
--------------

To initialize the most basic `~ndcube.NDCube` object, all you need is
a list of `~ndcube.NDCube` instances.  So let us first define three 3-D
NDCubes for slit-spectrograph data as we did in the NDCube section of
this tutorial.  First we define the data arrays and WCS objects::
  
  >>> # Define data for cubes
  >>> import numpy as np
  >>> data0 = np.ones((3, 4, 5))
  >>> data1 = data0 * 2
  >>> data2 = data1 * 2
  
  >>> # Define WCS object for all cubes.
  >>> import astropy.wcs
  >>> wcs_input_dict = {
  ... 'CTYPE1': 'WAVE    ', 'CUNIT1': 'Angstrom', 'CDELT1': 0.2, 'CRPIX1': 0, 'CRVAL1': 10, 'NAXIS1': 5,
  ... 'CTYPE2': 'HPLT-TAN', 'CUNIT2': 'deg', 'CDELT2': 0.5, 'CRPIX2': 2, 'CRVAL2': 0.5, 'NAXIS2': 4,
  ... 'CTYPE3': 'HPLN-TAN', 'CUNIT3': 'deg', 'CDELT3': 0.4, 'CRPIX3': 2, 'CRVAL3': 1, 'NAXIS3': 3}
  >>> input_wcs = astropy.wcs.WCS(wcs_input_dict)

Let's also define an extra coordinate of time.  (See NDCube section of
this guide of more detail.) Let the slices along the 0th axis are
separated by one minute and the slices in preceding cube are followed
directly in time by the slices in the next::
  
  >>> from datetime import datetime, timedelta
  >>> timestamps0 = [datetime(2000, 1, 1)+timedelta(minutes=i) for i in range(data0.shape[0])]
  >>> timestamps1 = [timestamps0[-1]+timedelta(minutes=i+1) for i in range(data1.shape[0])]
  >>> timestamps2 = [timestamps1[-1]+timedelta(minutes=i+1) for i in range(data2.shape[0])]
  >>> extra_coords_input0 = [("time", 0, timestamps0)]
  >>> extra_coords_input1 = [("time", 0, timestamps1)]
  >>> extra_coords_input2 = [("time", 0, timestamps2)]
  
Now we can define our cubes.

  >>> from ndcube import NDCube
  >>> from ndcube import NDCubeSequence
  >>> # Define a mask such that all array elements are unmasked.
  >>> mask = np.empty(data0.shape, dtype=object)
  >>> mask[:, :, :] = False
  >>> cube_meta = {"Description": "This is example NDCube metadata."}
  >>> my_cube0 = NDCube(data0, input_wcs, uncertainty=np.sqrt(data0),
  ...                          mask=mask, meta=cube_meta, unit=None,
  ...                          extra_coords=extra_coords_input0)
  INFO: uncertainty should have attribute uncertainty_type. [astropy.nddata.nddata]
  >>> my_cube1 = NDCube(data1, input_wcs, uncertainty=np.sqrt(data1),
  ...                          mask=mask, meta=cube_meta, unit=None,
  ...                          extra_coords=extra_coords_input1)
  INFO: uncertainty should have attribute uncertainty_type. [astropy.nddata.nddata]
  >>> my_cube2 = NDCube(data2, input_wcs, uncertainty=np.sqrt(data2),
  ...                          mask=mask, meta=cube_meta, unit=None,
  ...                          extra_coords=extra_coords_input2)
  INFO: uncertainty should have attribute uncertainty_type. [astropy.nddata.nddata]

N.B. The above warnings are due to the fact that
`astropy.nddata.uncertainty` is recommended to have an
``uncertainty_type`` attribute giving a string describing the type of
uncertainty.  However, this is not required.

Finally, creating an `~ndcube.NDCubeSequence` becomes is simple::
  
  >>> my_sequence = NDCubeSequence([my_cube0, my_cube1, my_cube2])

While, each `~ndcube.NDCube` in the `~ndcube.NDCubeSequence` can have
its own meta, it is also possible to supply additional metadata upon
initialization of the `~ndcube.NDCubeSequence`.  This metadata may be
common to all sub-cubes or is specific to the sequence rather than the
sub-cubes. This metadata is input as a dictionary::

  >>> my_sequence_metadata = {"Description": "This is some sample NDCubeSequence metadata."}
  >>> my_sequence = NDCubeSequence([my_cube0, my_cube1, my_cube2],
  ...                                     meta=my_sequence_metadata)

and stored in the ``my_sequence.meta`` attribute.  Meanwhile, the
`~ndcube.NDCube` instances are stored in the ``my_sequence.data``.
However, analgously to `~ndcube.NDCube`, it is strongly advised that 
the data is manipulated by slicing the `~ndcube.NDCubeSequence` rather
than more manually delving into the ``.data`` attribute.  For more
explanation, see the section on :ref:`sequence_slicing`.

Common Axis
-----------

It is possible (although not required) to set a common axis of the
`~ndcube.NDCubeSequence`.  A common axis is defined as the axis of the
sub-cubes parallel to the axis of the sequence.

For example, assume the 0th axis of the sub-cubes, ``my_cube0``,
``my_cube1`` and ``my_cube2`` in the `~ndcube.NDCubeSequence`,
``my_sequence``, represent time as we have indicated by setting the
``time`` extra coordinate. In this case, ``my_cube0`` represents
observations taken from a period directly before ``my_cube1`` and
``my_cube2`` and the sub-cubes are  ordered chronologically in the
sequence.  Then moving along the 0th axis of one sub-cube and moving
along the sequence axis from one cube to the next both represent
movement in time.  The difference is simply size of the steps.
Therefore it can be said that the 0th axis of the sub-cubes is common
to the sequence. 

To define a common axis, set the kwarg during intialization of
the `~ndcube.NDCubeSequence` to the desired data axis number::

  >>> my_sequence = NDCubeSequence([my_cube0, my_cube1, my_cube2],
  ...                              meta=my_sequence_metadata, common_axis=0)

Defining a common axis enables the full range of the
`~ndcube.NDCubeSequence` features to be utilized including
`ndcube.NDCubeSequence.plot`,
`ndcube.NDCubeSequence.common_axis_extra_coords`, and 
`ndcube.NDCubeSequence.index_as_cube`. See following sections for
more details on these features.

Dimensions
----------

Analagous to `ndcube.NDCube.dimensions`, there is also a
`~ndcube.NDCubeSequence.dimensions` property for easily inspecting the
size and shape of an `~ndcube.NDCubeSequence` instance::

  >>> my_sequence.dimensions
  SequenceDimensionPair(shape=(3, <Quantity 3. pix>, <Quantity 4. pix>, <Quantity 5. pix>), axis_types=('Sequence Axis', 'HPLN-TAN', 'HPLT-TAN', 'WAVE'))

Like NDCube it returns a named tuple with a ``shape`` and ``axis_types``
where the values of the 0th sub-cube are returned as
`astropy.units.Quantity` and `str` objects, respectively.  In addition
however, another dimension is return at the start of the named tuple.
Its value is an `int` (not a Quantity) giving the number of sub-cubes
in the sequence.  Since this is not a WCS axis, its axis type is given
the label ``'Sequence Axis'``.

As the dimensions property returns a named tuple, the shape and axis
types can be accessed directly::

  >>> my_sequence.dimensions.shape
  (3, <Quantity 3. pix>, <Quantity 4. pix>, <Quantity 5. pix>)
  
  >>> my_sequence.dimensions.axis_types
  ('Sequence Axis', 'HPLN-TAN', 'HPLT-TAN', 'WAVE')

.. _sequence_slicing:

Slicing
-------
As with `~ndcube.NDCube`, slicing an `~ndcube.NDCubeSequence` using
the standard slicing API simulataneously slices the data arrays, WCS
objects, masks, uncertainty arrays, etc. in each relevant sub-cube.
For example, say we have three NDCubes in an `~ndcube.NDCubeSequence`,
each of shape ``(3, 4, 5)``.  Say we want to obtain a region of
interest between the 1st and 2nd pixels (inclusive) in the 2nd
dimension and 1st and 3rd pixels (inclusive) in the 3rd dimension of
the 0th slice along the 0th axis in only the 1st (not 0th) and 2nd
sub-cubes in the sequence. This would be a cumbersome slicing operation
if treating the sub-cube independently. (This would be made even worse
without the power of `~ndcube.NDCube` where the data arrays, WCS
objects, masks, uncertainty arrays, etc. would all have to be sliced
independently!) However, with `~ndcube.NDCubeSequence` this becomes as
simple as indexing a single array::

  >>> ######### Due to a bug, this currently doesn't work! #########
  >>> regions_of_interest_in_sequence = my_sequence[1:3, 0, 1:3, 1:4] # doctest: +SKIP
  >>> regions_of_interest_in_sequence.dimensions # doctest: +SKIP

This will return a new `~ndcube.NDCubeSequence` with 2 2-D NDCubes,
one for each region of interest from the 3rd slice along the 0th axis
in each original sub-cube.  If our regions of interest only came from
a single sub-cube - say the 0th and 1st slices along the 0th axis in
the 1st sub-cube - an NDCube is returned::

  >>> roi_from_single_subcube = my_sequence[1, 0:2, 1:3, 1:4]
  >>> roi_from_single_subcube.dimensions
  DimensionPair(shape=<Quantity [2., 2., 3.] pix>, axis_types=['HPLN-TAN', 'HPLT-TAN', 'WAVE'])

If a common axis has been defined for the `~ndcube.NDCubeSequence` one
can think of it as a contiguous data set with different sections along
the common axis described by different WCS translations.  Therefore it
would be useful to be able to index the sequence as though it were one
single cube.  This can be achieved with the
`ndcube.NDCubeSequence.index_as_cube` property.  In our above
example, ``my_sequence`` has a shape of ``(3, <Quantity 3.0 pix>,
<Quantity 4.0 pix>, <Quantity 5.0 pix>)`` and a common cube axis
of ``0``.  Therefore we can think of ``my_sequence`` as a having an effective
cube-like shape of ``(<Quantity 9.0 pix>, <Quantity 4.0 pix>,
<Quantity 5.0 pix>)`` where the first sub-cube extends along the 0th
cube-like axis from 0 to 3, the second from 3 to 6 and the third
from 6 to 9.  Say we want to extract the same region of interest as
above, i.e. ``my_sequence[1, 0:2, 1:3, 1:4]``.  Then this can be
acheived by entering::

  >>> roi_from_single_subcube = my_sequence.index_as_cube[3:5, 1:3, 1:4]
  >>> roi_from_single_subcube.dimensions
    SequenceDimensionPair(shape=(1, <Quantity 1. pix>, <Quantity 3. pix>, <Quantity 5. pix>), axis_types=('Sequence Axis', 'HPLN-TAN', 'HPLT-TAN', 'WAVE'))                                                                                                                  

In this case the entire region came from a single sub-cube.  However,
`~ndcube.NDCubeSequence.index_as_cube` also works when the region of
interest spans multiple sub-cubes in the sequence.  Say we want the
same region of interest in the 2nd and 3rd cube dimensions from the
final slice along the 0th cube axis of the 0th sub-cube, the whole 1st
sub-cube and the 0th slice of the 2nd sub-cube. In cube-like indexing
this corresponds to slices 2 to 7 along to the 0th cube axis::

  >>> roi_across_subcubes = my_sequence.index_as_cube[2:7, 1:3, 1:4]
  >>> roi_across_subcubes.dimensions
  SequenceDimensionPair(shape=(3, <Quantity 0. pix>, <Quantity 3. pix>, <Quantity 5. pix>), axis_types=('Sequence Axis', 'HPLN-TAN', 'HPLT-TAN', 'WAVE'))                                                                                                                  

In both the examples above, an `~ndcube.NDCubeSequence` object is
returned.  In the case of former example, this is despite the fact
that the region of interest only came from one sub-cube and so the
sequence axis is of length 1.  The only time an `~ndcube.NDCube`
object is returned is when a single slice along the common axis is
indexed. This API was chosen so that the object type returned is
predictable and doesn't depend on the (possibly different) shape of
the sub-cubes along the common axis. 

Common Axis Extra Coordinates
-----------------------------

If a common axis is defined, it may be useful to view the extra
coordinates along that common axis defined by each of the sub-cube
`~ndcube.NDCube._extra_coords` as if the `~ndcube.NDCubeSequence` were
one contiguous Cube.  This can be done using the
``common_axis_extra_coords`` property::

  >>> my_sequence.common_axis_extra_coords
  {'time': array([datetime.datetime(2000, 1, 1, 0, 0),
        datetime.datetime(2000, 1, 1, 0, 1),
        datetime.datetime(2000, 1, 1, 0, 2),
        datetime.datetime(2000, 1, 1, 0, 3),
        datetime.datetime(2000, 1, 1, 0, 4),
        datetime.datetime(2000, 1, 1, 0, 5),
        datetime.datetime(2000, 1, 1, 0, 6),
        datetime.datetime(2000, 1, 1, 0, 7),
        datetime.datetime(2000, 1, 1, 0, 8)], dtype=object)}

This returns a dictionary where each key gives the name of the
coordinate.  The value of each key are the values of that coordinate
at each pixel along the common axis.  Since all these coordinates must
be along the common axis, it is not necessary to supply axis
information as it is with `ndcube.NDCube.extra_coords` making
`ndcube.NDCubeSequence.common_axis_extra_coords` simpler.  Because
this property has a functional form and calculates the dictionary
each time from the constituent sub-cubes' `ndcube.NDCube.extra_coords`
attributes, `ndcube.NDCubeSequence. common_axis_extra_coords` is
effectively sliced when the `~ndcube.NDCubeSequence` is sliced, e.g.::

  >>> my_sequence[1:3].common_axis_extra_coords
  {'time': array([datetime.datetime(2000, 1, 1, 0, 3),
        datetime.datetime(2000, 1, 1, 0, 4),
        datetime.datetime(2000, 1, 1, 0, 5),
        datetime.datetime(2000, 1, 1, 0, 6),
        datetime.datetime(2000, 1, 1, 0, 7),
        datetime.datetime(2000, 1, 1, 0, 8)], dtype=object)}
  
Plotting
--------

The `ndcube.NDCubeSequence.plot` method allows the sequence to be animated as
though it were one contiguous `~ndcube.NDCube`. It has the same API and same
kwargs as `ndcube.NDCube.plot`.  See documentation for `ndcube.NDCube.plot` for more
details.


Explode Along Axis
------------------

During analysis of some data - say of a stack of images - it may be
necessary to make some different fine-pointing adjustments to each
image that isn't accounted for the in the original WCS translations in
your data, e.g. due to satellite wobble.  If these changes are not
describable with a single WCS object, it may be desirable to break up
the N-D sub-cubes of an `~ndcube.NDCubeSequence` into an sequence of
sub-cubes with dimension N-1. This would enable a separate WCS object
to be associated with each image and hence allow individual pointing
adjustments.

Rather than manually dividing the datacubes up and deriving the
corresponding WCS object for each exposure, `~ndcube.NDCubeSequence`
provides a useful method,
`~ndcube.NDCubeSequence.explode_along_axis`. To call it, simply provide
the number of the data cube axis along which you wish to break up the
sub-cubes::

  >>> exploded_sequence = my_sequence.explode_along_axis(0)

Assuming we are using the same ``my_sequence`` as above, with
dimensions.shape ``(3, <Quantity 3.0 pix>, <Quantity 4.0 pix>,
<Quantity 5.0 pix>)``, the ``exploded_sequence`` will be an 
`~ndcube.NDCubeSequence` of nine 2-D NDCubes each with shape
``(<Quantity 4.0 pix>, <Quantity 5.0 pix>)``.::

  >>> # Check old and new shapes of the squence
  >>> my_sequence.dimensions.shape
  (3, <Quantity 3. pix>, <Quantity 4. pix>, <Quantity 5. pix>)
  >>> exploded_sequence.dimensions.shape
  (9, <Quantity 4. pix>, <Quantity 5. pix>)

Note that any cube axis can be input.  A common axis need not be
defined.
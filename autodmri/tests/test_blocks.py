import numpy as np
from autodmri.blocks import extract_patches


def test_extract_patches_strided():

    image_shapes_1D = [(10,), (10,), (11,), (10,)]
    patch_sizes_1D = [(1,), (2,), (3,), (8,)]
    patch_steps_1D = [(1,), (1,), (4,), (2,)]

    expected_views_1D = [(10,), (9,), (3,), (2,)]
    last_patch_1D = [(10,), (8,), (8,), (2,)]

    image_shapes_2D = [(10, 20), (10, 20), (10, 20), (11, 20)]
    patch_sizes_2D = [(2, 2), (10, 10), (10, 11), (6, 6)]
    patch_steps_2D = [(5, 5), (3, 10), (3, 4), (4, 2)]

    expected_views_2D = [(2, 4), (1, 2), (1, 3), (2, 8)]
    last_patch_2D = [(5, 15), (0, 10), (0, 8), (4, 14)]

    image_shapes_3D = [(5, 4, 3), (3, 3, 3), (7, 8, 9), (7, 8, 9)]
    patch_sizes_3D = [(2, 2, 3), (2, 2, 2), (1, 7, 3), (1, 3, 3)]
    patch_steps_3D = [(1, 2, 10), (1, 1, 1), (2, 1, 3), (3, 3, 4)]

    expected_views_3D = [(4, 2, 1), (2, 2, 2), (4, 2, 3), (3, 2, 2)]
    last_patch_3D = [(3, 2, 0), (1, 1, 1), (6, 1, 6), (6, 3, 4)]

    image_shapes = image_shapes_1D + image_shapes_2D + image_shapes_3D
    patch_sizes = patch_sizes_1D + patch_sizes_2D + patch_sizes_3D
    patch_steps = patch_steps_1D + patch_steps_2D + patch_steps_3D
    expected_views = expected_views_1D + expected_views_2D + expected_views_3D
    last_patches = last_patch_1D + last_patch_2D + last_patch_3D

    for (image_shape, patch_size, patch_step, expected_view,
         last_patch) in zip(image_shapes, patch_sizes, patch_steps,
                            expected_views, last_patches):
        image = np.arange(np.prod(image_shape)).reshape(image_shape)
        patches = extract_patches(image, patch_size, patch_step, flatten=False)

        ndim = len(image_shape)

        assert patches.shape[:ndim] == expected_view
        last_patch_slices = tuple(slice(i, i + j, None) for i, j in
                                  zip(last_patch, patch_size))
        assert (patches[(-1, None, None) * ndim] ==
                image[last_patch_slices].squeeze()).all()

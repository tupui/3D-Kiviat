# coding: utf8
import os
import pytest
import numpy as np
import numpy.testing as npt
from mock import patch
from kiviat import Kiviat3D
from kiviat import Tree

try:
    import matplotlib.animation as manimation
    manimation.writers['ffmpeg']
    have_ffmpeg = True
except (RuntimeError, KeyError):
    have_ffmpeg = False


@pytest.fixture(scope="module")
def tmp(tmpdir_factory):
    """Create a common temp directory."""
    return str(tmpdir_factory.mktemp('tmp_test'))


class TestKiviat:

    @pytest.fixture(scope="session")
    def kiviat_data(self):
        sample = [[30, 4000], [15, 5000], [12, 1000], [20, 3000]]
        data = [[12], [15], [10], [17]]
        plabels = ['Ks', 'Q', '-']
        bounds = [[15.0, 2500.0], [60.0, 6000.0]]
        kiviat = Kiviat3D(sample, data, bounds=bounds, plabels=plabels)

        return kiviat

    @patch("matplotlib.pyplot.show")
    def test_kiviat_plot(self, mock_show, tmp):
        sample = [[30, 4000], [15, 5000], [12, 1000], [20, 3000]]
        data = [[12], [15], [10], [17]]
        functional_data = [[12, 300], [15, 347], [10, 200], [17, 247]]

        kiviat = Kiviat3D([[30], [15], [12], [20]], data)
        kiviat.plot()

        kiviat = Kiviat3D(sample, data)
        kiviat.plot(fill=False, ticks_nbr=12)

        kiviat = Kiviat3D(sample, functional_data)
        kiviat = Kiviat3D(sample, functional_data, stack_order='qoi', cbar_order='hdr')
        kiviat = Kiviat3D(sample, functional_data, stack_order='hdr', cbar_order='qoi')
        kiviat = Kiviat3D(sample, functional_data, stack_order=1, cbar_order='hdr')
        kiviat = Kiviat3D(sample, functional_data, idx=1, cbar_order='hdr',
                          range_cbar=[0, 1])
        kiviat.plot(fname=os.path.join(tmp, 'kiviat.pdf'))

    @pytest.mark.skipif(not have_ffmpeg, reason='ffmpeg not available')
    def test_kiviat_fhops(self, kiviat_data, tmp):
        kiviat_data.f_hops(frame_rate=40, ticks_nbr=30,
                           fname=os.path.join(tmp, 'kiviat_fill.mp4'))
        kiviat_data.f_hops(fname=os.path.join(tmp, 'kiviat.mp4'), fill=False)

    @patch("matplotlib.pyplot.show")
    @pytest.mark.skipif(not have_ffmpeg, reason='ffmpeg not available')
    def test_tree(self, mock_show, tmp):
        sample = [[30, 4000], [15, 5000], [20, 4500]]
        functional_data = [[12, 300], [15, 347], [14, 320]]
        tree = Tree(sample, functional_data,
                    bounds=[[10.0, 2500.0], [60.0, 6000.0]])
        tree.plot(flabel='Water level (m)')
        tree.f_hops(fname=os.path.join(tmp, 'tree.mp4'))

    def test_connectivity(self):
        connectivity = Kiviat3D.mesh_connectivity(6, 3)
        connectivity_t = np.array([[4, 0, 1, 3, 4],
                                   [4, 1, 2, 4, 5],
                                   [4, 2, 0, 5, 3]], dtype=int)
        npt.assert_equal(connectivity, connectivity_t)

        with pytest.raises(ValueError):
            Kiviat3D.mesh_connectivity(6, 4)

        connectivity = Kiviat3D.mesh_connectivity(8, 4)
        connectivity_t = np.array([[4, 0, 1, 4, 5],
                                   [4, 1, 2, 5, 6],
                                   [4, 2, 3, 6, 7],
                                   [4, 3, 0, 7, 4]], dtype=int)
        npt.assert_equal(connectivity, connectivity_t)

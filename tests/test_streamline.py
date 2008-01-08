"""Tests for the Streamline module.
"""
# Author: Prabhu Ramachandran <prabhu_r@users.sf.net>
# Copyright (c) 2005-2006,  Enthought, Inc.
# License: BSD Style.

# Standard library imports.
from os.path import join, abspath
from StringIO import StringIO
import copy
import numpy

# Enthought library imports.
from enthought.traits.api import TraitError

# Local imports.
from common import TestCase


class TestStreamline(TestCase):
    def make_data(self):
        """Trivial data -- creates an elementatry scalar field and a
        constant vector field along the 'x' axis."""        
        s = numpy.arange(0.0, 10.0, 0.01)
        s = numpy.reshape(s, (10,10,10))
        s = numpy.transpose(s)

        v = numpy.zeros(3000, 'd')
        v[::3] = 1.0
        v = numpy.reshape(v, (10,10,10,3))
        return s, v


    def test(self):        
        ############################################################
        # Imports.
        script = self.script
        from enthought.mayavi.sources.array_source import ArraySource
        from enthought.mayavi.modules.outline import Outline
        from enthought.mayavi.modules.streamline import Streamline
        
        ############################################################
        # Create a new scene and set up the visualization.
        s = self.new_scene()

        d = ArraySource()
        sc, vec = self.make_data()
        d.scalar_data = sc
        d.vector_data = vec
        d.image_data.origin = (-5, -5, -5)

        script.add_source(d)

        # Create an outline for the data.
        o = Outline()
        script.add_module(o)
        # View the data.
        st = Streamline()
        script.add_module(st)
        widget = st.seed.widget
        widget.set(radius=1.0, center=(-4.0, -4.0, -4.0),
                   theta_resolution=4, phi_resolution=4)

        st = Streamline(streamline_type='ribbon')
        seed = st.seed
        seed.widget = seed.widget_list[1]
        script.add_module(st)
        seed.widget.set(point1=(-5.0, -4.5, -4.0), point2=(-5.0, -4.5, 4.0))
        st.ribbon_filter.width = 0.25

        st = Streamline(streamline_type='tube')
        seed = st.seed
        seed.widget = seed.widget_list[2]
        script.add_module(st)
        seed.widget.set(center=(-5.0, 1.5, -2.5))
        st.tube_filter.radius = 0.15

        st = Streamline(streamline_type='tube')
        seed = st.seed
        seed.widget = seed.widget_list[3]
        script.add_module(st)
        seed.widget.position=(-5.0, 3.75, 3.75)
        st.tube_filter.radius = 0.2

        # Set the scene to a suitable view.
        s.scene.z_plus_view()
        c = s.scene.camera
        c.azimuth(-30)
        c.elevation(30)
        s.render()

        # Now compare the image.
        self.compare_image(s, 'images/test_streamline.png')

        ############################################################
        # Test if the modules respond correctly when the components
        # are changed.

        tf = st.tube_filter
        st.tube_filter = tf.__class__()
        st.tube_filter = tf
        st.ribbon_filter = st.ribbon_filter.__class__()
        seed = st.seed
        st.seed = seed.__class__()
        st.seed = seed
        st.actor = st.actor.__class__()
        tracer = st.stream_tracer
        st.stream_tracer = tracer.__class__()
        st.stream_tracer = tracer

        s.render()
        # Now compare the image.
        self.compare_image(s, 'images/test_streamline.png')
        s.render()

        ############################################################
        # Test if saving a visualization and restoring it works.

        bg = s.scene.background
        # Save visualization.
        f = StringIO()
        f.name = abspath('test.mv2') # We simulate a file.
        script.save_visualization(f)
        f.seek(0) # So we can read this saved data.

        # Remove existing scene.
        engine = script.engine
        engine.close_scene(s)

        # Load visualization
        script.load_visualization(f)
        s = engine.current_scene

        # Set the scene to a suitable view.
        s.scene.z_plus_view()
        c = s.scene.camera
        c.azimuth(-30)
        c.elevation(30)
        s.render()
        s.scene.background = bg

        # Now compare the image.
        self.compare_image(s, 'images/test_streamline.png')

        ############################################################
        # Test if the MayaVi2 visualization can be deepcopied.

        # Pop the source object.
        sources = s.children
        s.children = []
        # Add it back to see if that works without error.
        s.children.extend(sources)

        s.scene.reset_zoom()
        # Now compare the image.
        self.compare_image(s, 'images/test_streamline.png')

        # Now deepcopy the source and replace the existing one with
        # the copy.  This basically simulates cutting/copying the
        # object from the UI via the right-click menu on the tree
        # view, and pasting the copy back.
        sources1 = copy.deepcopy(sources)
        s.children[:] = sources
        s.scene.reset_zoom()
        self.compare_image(s, 'images/test_streamline.png')
        
        # If we have come this far, we are golden!
        

if __name__ == "__main__":
    t = TestStreamline()
    t.run()

"""Run: python -m unittest sv.test_profiles. No model download required."""
import unittest
from . import profiles, storyboard, comp4k

class ProfileTests(unittest.TestCase):
    def tearDown(self): profiles.configure({})
    def test_default_remains_4k60(self):
        self.assertEqual(profiles.get({}),dict(width=2160,height=3840,fps=60))
        self.assertEqual(storyboard.total_sec({'source':{'n_src':7268}}),7268/60)
    def test_1080p30_clock_and_reset(self):
        sb={'source':{'n_src':90},'hold':.5,'output_profile':dict(width=1080,height=1920,fps=30)}
        self.assertEqual(storyboard.total_frames(sb),105)
        self.assertEqual(storyboard.total_sec(sb),3.5)
        profiles.configure(sb)
        self.assertEqual(comp4k.FPS,30)
        self.assertIn('scale=2160:3840',comp4k.TONEMAP)
        profiles.configure({})
        self.assertEqual(comp4k.TONEMAP,comp4k._profile_original[1])
    def test_unsupported_profile_fails(self):
        with self.assertRaises(ValueError):profiles.get({'output_profile':dict(width=720,height=1280,fps=30)})
        with self.assertRaises(ValueError):profiles.get({'output_profile':dict(width=1080,height=1920,fps=30.0)})

if __name__=='__main__':unittest.main()

from bbme.reference.globalml import quadkeys


def test_quadkeys_match_bing_tile_system():
    # Bing Maps tile system reference: tile (x=3, y=5) at level 3 has quadkey 213.
    assert quadkeys(-20.0, -55.7, -20.0, -55.7, 3) == {"213"}


def test_quadkeys_cover_a_box_spanning_tiles():
    keys = quadkeys(-98.6, 29.3, -98.4, 29.6, 9)
    assert len(keys) >= 1 and all(len(k) == 9 for k in keys)
    assert quadkeys(-180, -85, 180, 85, 1) == {"0", "1", "2", "3"}

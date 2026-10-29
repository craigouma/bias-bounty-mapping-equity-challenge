import io
from unittest import mock

from bbme.analysis.external import counties

LIST = (
    b"STATE|STATEFP|COUNTYFP|COUNTYNS|COUNTYNAME|CLASSFP|FUNCSTAT\n"
    b"OK|40|113|01101844|Osage County|H1|A\n"
)


def test_county_names_keep_leading_zero_fips(tmp_path):
    url = "https://example.org/national_county2020.txt"
    with mock.patch.object(counties.urllib.request, "urlopen", return_value=io.BytesIO(LIST)):
        out = counties.county_names(url, tmp_path)
    assert out.to_dict("records") == [{"county_fips": "40113", "county_name": "Osage County, OK"}]

"""Adversarial controls for source identity, image bytes and epoch claims."""
import copy
import json
import unittest
from tools.cgeo44_browser_photoindex import DIMENSIONS, JPEG_SIZE, LABEL, MANIFEST, SOURCE_URL, verify_manifest, verify_response

class TestCGEO44(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = json.loads(MANIFEST.read_text(encoding="utf-8"))

    def invalid(self, group, key, value):
        doc = copy.deepcopy(self.m)
        doc[group][key] = value
        with self.assertRaises(ValueError):
            verify_manifest(doc)

    def test_original(self): self.assertEqual(verify_manifest(self.m), "CGEO44_OFFLINE_CONTRACT_PASS")
    def test_wrong_folder(self): self.invalid("source","selected_folder_label",LABEL.replace("1850","0335"))
    def test_wrong_url(self): self.invalid("source","url",SOURCE_URL.replace("1850","1851"))
    def test_wrong_node(self): self.invalid("source","selected_node","1")
    def test_wrong_sha(self): self.invalid("acquisition","jpeg_sha256","0"*64)
    def test_wrong_dimensions(self): self.invalid("acquisition","image_dimensions_pixels",[800,801])
    def test_single_session(self): self.invalid("acquisition","repeat_count",1)
    def test_1963_claim(self): self.invalid("printed_metadata","survey_1963_proven",True)
    def test_frame_date_claim(self): self.invalid("printed_metadata","frame_specific_capture_dates","1963-11-08")
    def test_event_coordinate_claim(self): self.invalid("interpretation","event_reentry_position",[-37.7,-11.7])
    def test_center_claim(self): self.invalid("interpretation","historic_center_conde_1963_geometry",[0,0])
    def test_orbital_claim(self): self.invalid("interpretation","orbital_constraint_activated",True)
    def test_frame_not_index(self): self.invalid("interpretation","individual_original_aerial_frames_acquired",True)

    def state(self):
        return {"folder":LABEL,"selected_value":"680","hidden_pag":"680",
                "img_src":"cache/123/I0000680-0-0-004350-004355-003740-003744.JPG","loaded":True}

    def test_fallback_0335(self):
        state=self.state();state["folder"]="0335 Projeto USAF";state["selected_value"]="1"
        with self.assertRaisesRegex(ValueError,"Telerik folder/node"):
            verify_response(self.m,state,"https://acervo.sgb.gov.br/DocReader/"+state["img_src"],b"\xff\xd8\xff",DIMENSIONS,200,"image/jpeg")

    def test_wrong_host(self):
        state=self.state()
        with self.assertRaises(ValueError):
            verify_response(self.m,state,"https://example.org/DocReader/"+state["img_src"],b"\xff\xd8\xff",DIMENSIONS,200,"image/jpeg")

    def test_wrong_page(self):
        state=self.state();state["hidden_pag"]="1"
        with self.assertRaises(ValueError):
            verify_response(self.m,state,"https://acervo.sgb.gov.br/DocReader/"+state["img_src"],b"\xff\xd8\xff",DIMENSIONS,200,"image/jpeg")

    def test_wrong_digest_with_correct_length(self):
        state=self.state()
        with self.assertRaisesRegex(ValueError,"JPEG digest mismatch"):
            verify_response(self.m,state,"https://acervo.sgb.gov.br/DocReader/"+state["img_src"],
                            b"\xff\xd8\xff"+b"z"*(JPEG_SIZE-3),DIMENSIONS,200,"image/jpeg")

    def test_http_error(self):
        state=self.state()
        with self.assertRaisesRegex(ValueError,"HTTP response"):
            verify_response(self.m,state,"https://acervo.sgb.gov.br/DocReader/"+state["img_src"],b"\xff\xd8\xff",DIMENSIONS,403,"image/jpeg")

if __name__=="__main__": unittest.main()

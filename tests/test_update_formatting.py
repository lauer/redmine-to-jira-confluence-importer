import unittest
import types
from helpers import settings

class TestUpdateFormatting(unittest.TestCase):

    def setUp(self):
        # Create empty global dicts like settings.init() normally would
        settings.yaml_vars = {
            "redmine_server": "https://redmine.example.com",
            "redmine_project_id": 1,
        }

        # Create a dummy arg_vars object
        settings.arg_vars = types.SimpleNamespace(
            wiki=False,
            all=False
        )

    def test_pre_code_replacement(self):
        """
        Test replacement of <pre> and <code>
        """
        desc = "<pre><code class=\"ruby\">puts 'test'</code></pre>"
        result = settings.update_formatting(desc)
        self.assertNotIn("{noformat}", result)
        self.assertNotIn("<pre>", result)
        self.assertNotIn("</pre>", result)
        self.assertIn("<code", result)

    def test_pre_replacement(self):
        """
        Test replacement of <pre> where its not code
        """
        desc = "<pre>{testing}</pre>"
        result = settings.update_formatting(desc)
        self.assertIn("{noformat}", result)
        self.assertNotIn("<pre>", result)
        self.assertNotIn("</pre>", result)


    def test_inline_code(self):
        """
        Test @inline@ → {{inline}}
        """
        desc = "This is @code@ inside text"
        result = settings.update_formatting(desc)
        self.assertEqual(result, "This is {{code}} inside text")

    def test_pbi_links(self):
        """
        Test PBI reference #123 → link to redmine
        """
        desc = "Fix in ticket #123"
        result = settings.update_formatting(desc)
        self.assertIn("[#123|https://redmine.example.com/issues/123]", result)

    def test_wiki_formatting_enabled(self):
        """
        Test wiki-only formatting when arg_vars.wiki = True
        """
        settings.arg_vars.wiki = True
        desc = "{{>toc}} ||Test||"
        result = settings.update_formatting(desc)
        self.assertIn("{toc}", result)
        self.assertIn("| |", result)  # Empty table cell mapping

    def test_code_language_conversion(self):
        """
        Test <code class="python"> → {code:language=python}
        """
        desc = '<code class="python">print("x")</code>'
        settings.arg_vars.wiki = True
        result = settings.update_formatting(desc)
        self.assertIn("{code:language=python}", result)

    def test_background_cleanup(self):
        """
        Remove {background:...} attributes
        """
        settings.arg_vars.wiki = True
        desc = "{background:red} Text {background-color:blue}"
        result = settings.update_formatting(desc)
        self.assertNotIn("background:red", result)
        self.assertNotIn("background-color:blue", result)

    def test_drawio_attach_to_image(self):
        """
        Testing replace drawio code to images
        """
        desc = "foo \n {{drawio_attach(drawing.png)}} bar"
        result = settings.update_formatting(desc)
        self.assertNotIn("drawio", result)
        self.assertIn("!drawing.png!", result)

if __name__ == '__main__':
    unittest.main()
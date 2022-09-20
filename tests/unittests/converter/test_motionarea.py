import unittest
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from converter.motionarea import MotionArea


class TestMotionArea(unittest.TestCase):
    @patch("subprocess.check_output")
    def test_shebang_looks_as_expected(self, mock_subprocess):
        # Arrange
        python_path = "/bin/python"
        expected_shebang = "#!/bin/env /bin/python \n"
        mock_subprocess.return_value = python_path.encode("UTF-8")
        stream = StringIO()
        motionarea = MotionArea(Path("/tmp"))
        # Act
        motionarea.write_shebang(stream)
        stream.seek(0)  # Change the stream position to start of the stream
        content = stream.read()
        # Assert
        self.assertEqual(content, expected_shebang)

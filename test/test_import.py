import os
import asyncio
import importlib.util
import sys
import unittest
from dotenv import load_dotenv


class TestCustomModuleImport(unittest.TestCase):
    def test_custom_module_import(self):
        load_dotenv(".env.example",override=True)
        path = os.getenv("LOCAL_PATH")
        self.assertIsNotNone(path,"Unable to retrieve env")

        module_path = str(path + '/services/embedding.py')
        module_name = 'embedding'

        self.assertTrue(os.path.exists(module_path),f"File Not Found: {module_path}")

        spec = importlib.util.spec_from_file_location(module_name,module_path)
        self.assertIsNotNone(spec,"Could Not Create Module Spec")

        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        try:
            spec.loader.exec_module(module)
        except Exception as e:
            self.fail(f"Failed to import:{module_name} at {module_path}: e")






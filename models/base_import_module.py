import os
import base64
from io import BytesIO
import logging
from odoo import api, fields, models
import zipfile
import shutil

_logger = logging.getLogger(__name__)

class CustomImportModule(models.TransientModel):
    """ Import Module """
    _inherit = "base.import.module"

    def import_module(self):
        self.ensure_one()

        # Directory to save the extracted files
        target_dir = "/var/lib/odoo/imported_modules"  # Change this to your desired path in the container
        
        # Ensure the directory exists
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)

        # Attempt to decode the module_file and log the file name if possible
        try:
            module_content = base64.decodebytes(self.module_file)
            fp = BytesIO(module_content)
            
            # Check if it's a ZIP file and retrieve its contents
            with zipfile.ZipFile(fp, 'r') as zip_ref:
                file_list = zip_ref.namelist()
                _logger.info("ZIP file contains: %s", file_list)
                
                # Extract each file/folder from the ZIP and save to the target directory
                for file_name in file_list:
                    extracted_path = os.path.join(target_dir, file_name)
                    
                    # Ensure the directory structure exists in the target location
                    extracted_dir = os.path.dirname(extracted_path)
                    if not os.path.exists(extracted_dir):
                        os.makedirs(extracted_dir)
                    
                    # Extract the file to the target directory
                    with zip_ref.open(file_name) as extracted_file, open(extracted_path, 'wb') as out_file:
                        shutil.copyfileobj(extracted_file, out_file)

                _logger.info("Files successfully extracted to: %s", target_dir)
        except Exception as e:
            _logger.error("Failed to process module_file: %s", e)

        # Call the original import_module and log the context
        res = super(CustomImportModule, self).import_module()
        _logger.info("Import Module Result Context: %s", self.env.context)
        
        return res

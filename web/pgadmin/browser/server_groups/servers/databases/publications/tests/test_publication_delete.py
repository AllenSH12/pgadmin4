##########################################################################
#
# pgAdmin 4 - PostgreSQL Tools
#
# Copyright (C) 2013 - 2025, The pgAdmin Development Team
# This software is released under the PostgreSQL Licence
#
##########################################################################

import uuid
from unittest.mock import patch
from pgadmin.browser.server_groups.servers.databases.schemas.tests import \
    utils as schema_utils
from pgadmin.browser.server_groups.servers.databases.tests import utils as \
    database_utils
from pgadmin.utils.route import BaseTestGenerator
from regression import parent_node_dict
from regression.python_test_utils import test_utils as utils
from . import utils as publication_utils


class PublicationDeleteTestCase(BaseTestGenerator):
    """This class will delete publication."""
    scenarios = utils.generate_scenarios('delete_publication',
                                         publication_utils.test_cases)

    def setUp(self):
        super().setUp()
        self.db_name = parent_node_dict["database"][-1]["db_name"]
        schema_info = parent_node_dict["schema"][-1]
        self.server_id = schema_info["server_id"]
        self.db_id = schema_info["db_id"]
        self.server_version = schema_info["server_version"]
        if self.server_version < 99999:
            self.skipTest(
                "Logical replication is not supported "
                "for server version less than 10"

            )
        db_con = database_utils.connect_database(self, utils.SERVER_GROUP,
                                                 self.server_id, self.db_id)
        if not db_con['data']["connected"]:
            raise Exception(
                "Could not connect to database to delete publication.")
        self.schema_id = schema_info["schema_id"]
        self.schema_name = schema_info["schema_name"]

        schema_response = schema_utils.verify_schemas(self.server,
                                                      self.db_name,
                                                      self.schema_name)
        if not schema_response:
            raise Exception("Could not find the schema to delete publication.")
        self.publication_name = "test_publication_delete_%s" % (
            str(uuid.uuid4())[1:8])

        self.publication_id = \
            publication_utils.create_publication(self)

    def delete_publication(self):
        return self.tester.delete(
            self.url + str(utils.SERVER_GROUP) + '/' +
            str(self.server_id) + '/' + str(self.db_id) +
            '/' + str(self.publication_id),
            follow_redirects=True)

    def runTest(self):
        """This function will delete publication"""
        publication_response = publication_utils. \
            verify_publication(self.server,
                               self.db_name,
                               self.publication_name)
        if not publication_response:
            raise Exception("Could not find the publication to delete.")

        if self.is_positive_test:
            if hasattr(self, "invalid_publication_id"):
                self.publication_id = 9999
            response = self.delete_publication()
        else:
            with patch(self.mock_data["function_name"],
                       return_value=eval(self.mock_data["return_value"])):
                response = self.delete_publication()

        self.assertEqual(response.status_code,
                         self.expected_data["status_code"])

    def tearDown(self):
        # Disconnect the database
        if not self.is_positive_test or hasattr(self,
                                                'invalid_publication_id'):
            publication_utils.delete_publication(self.server, self.db_name,
                                                 self.publication_name)
        database_utils.disconnect_database(self, self.server_id, self.db_id)

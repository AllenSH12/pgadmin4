##########################################################################
#
# pgAdmin 4 - PostgreSQL Tools
#
# Copyright (C) 2013 - 2025, The pgAdmin Development Team
# This software is released under the PostgreSQL Licence
#
##########################################################################


import json
import uuid

from pgadmin.utils import server_utils
from regression import trigger_funcs_utils as fts_config_funcs_utils
from pgadmin.browser.server_groups.servers.databases.schemas.tests import \
    utils as schema_utils
from pgadmin.browser.server_groups.servers.databases.schemas \
    .fts_configurations.tests import utils as fts_config_utils
from pgadmin.browser.server_groups.servers.databases.tests import \
    utils as database_utils
from pgadmin.utils.route import BaseTestGenerator
from regression import parent_node_dict
from regression.python_test_utils import test_utils as utils
from . import utils as fts_configurations_utils


class FTSConfigurationDependencyDependentTestCase(BaseTestGenerator):
    """ This class will get the dependency and  dependents FTS configuration
    under test schema. """

    scenarios = utils.generate_scenarios(
        'dependency_dependent_fts_configurations',
        fts_configurations_utils.test_cases
    )

    def setUp(self):
        self.schema_data = parent_node_dict['schema'][-1]
        self.server_id = self.schema_data['server_id']
        self.db_id = self.schema_data['db_id']
        self.schema_name = self.schema_data['schema_name']
        self.schema_id = self.schema_data['schema_id']
        self.extension_name = "postgres_fdw"
        self.db_name = parent_node_dict["database"][-1]["db_name"]
        self.db_user = self.server["username"]
        self.func_name = "fts_configuration_func_%s" % str(uuid.uuid4())[1:8]
        self.fts_configuration_name = "fts_configuration_delete_%s" % (
            str(uuid.uuid4())[1:8])
        server_con = server_utils.connect_server(self, self.server_id)
        if not server_con["info"] == "Server connected.":
            raise Exception("Could not connect to server to add resource "
                            "groups.")
        server_version = 0
        if "type" in server_con["data"]:
            if server_con["data"]["version"] < 90500:
                message = "FTS Configuration are not supported by PG9.4 " \
                          "and PPAS9.4 and below."
                self.skipTest(message)
        self.function_info = fts_config_funcs_utils.create_trigger_function(
            self.server, self.db_name, self.schema_name, self.func_name,
            server_version)
        self.fts_configuration_id = fts_configurations_utils. \
            create_fts_configuration(
                self.server, self.db_name, self.schema_name,
                self.fts_configuration_name)

    def runTest(self):
        """ This function will add new FTS configuration under test schema. """

        db_con = database_utils.connect_database(self,
                                                 utils.SERVER_GROUP,
                                                 self.server_id,
                                                 self.db_id)

        if not db_con["info"] == "Database connected.":
            raise Exception("Could not connect to database.")

        schema_response = schema_utils.verify_schemas(self.server,
                                                      self.db_name,
                                                      self.schema_name)
        if not schema_response:
            raise Exception("Could not find the schema.")

        fts_conf_response = fts_configurations_utils.verify_fts_configuration(
            self.server, self.db_name, self.fts_configuration_name
        )

        if not fts_conf_response:
            raise Exception("Could not find the FTS Configuration.")

        if self.is_positive_test:
            response = self.get_dependency_dependent()
            actual_response_code = response.status_code
            expected_response_code = self.expected_data['status_code']
        self.assertEqual(actual_response_code, expected_response_code)

    def get_dependency_dependent(self):
        """
        This function returns the fts configuration dependency and dependent
        :return: fts configuration dependency and dependent
        """
        return self.tester.get(
            self.url + str(utils.SERVER_GROUP) + '/' +
            str(self.server_id) + '/' +
            str(self.db_id) + '/' +
            str(self.schema_id) + '/' +
            str(self.fts_configuration_id),
            follow_redirects=True)

    def tearDown(self):
        """This function delete the fts_config and disconnect the test
        database."""
        fts_config_utils.delete_fts_configurations(self.server, self.db_name,
                                                   self.schema_name,
                                                   self.fts_configuration_name)
        database_utils.disconnect_database(self, self.server_id,
                                           self.db_id)

import pytest
from unittest.mock import Mock
from fastmcp.server.openapi import OpenAPITool
from fastmcp.server.openapi.routing import HTTPRoute

from solace_event_broker_monitor_mcp.server import customize_components


class TestCustomizeComponents:

    def test_does_not_modify_non_tool_components(self):
        route = Mock(spec=HTTPRoute)
        resource = Mock()
        resource.description = "Original description"

        customize_components(route, resource)

        assert resource.description == "Original description"

    def test_removes_attribute_table(self):
        """Test removal of attribute table and everything after it"""
        route = Mock(spec=HTTPRoute)
        tool = Mock(spec=OpenAPITool)
        tool.description = (
            "Get a list of Message VPN objects.\n\n"
            "Message VPNs allow for the segregation of topic space.\n\n"
            "Attribute|Identifying|Deprecated\n"
            ":---|:---:|:---:\n"
            "authenticationOauthDefaultProviderName||x\n"
            "bridgingTlsServerCertEnforceTrustedCommonNameEnabled||x"
        )
        tool.parameters = {"properties": {}}

        customize_components(route, tool)

        assert "Attribute|" not in tool.description
        assert "Message VPNs allow for the segregation of topic space." in tool.description
        assert tool.description.endswith("Message VPNs allow for the segregation of topic space.")

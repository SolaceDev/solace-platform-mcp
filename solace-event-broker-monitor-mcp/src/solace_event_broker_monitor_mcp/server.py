import httpx
import json
import logging
import os
import sys
from typing import Any
import warnings

# Suppress FastMCP parser warnings before importing
logging.basicConfig(level=logging.INFO)
logging.getLogger("fastmcp").setLevel(logging.ERROR)

from fastmcp import FastMCP
from fastmcp.server.openapi import (
    RouteMap,
    MCPType,
    OpenAPITool,
    OpenAPIResource,
    OpenAPIResourceTemplate
)
from fastmcp.server.openapi.routing import HTTPRoute

logger = logging.getLogger(__name__)


def resolve_parameter_refs(spec: dict) -> dict:
    """Resolve $ref references to parameters in the OpenAPI spec."""
    # Get the shared parameters
    shared_params = spec.get("parameters", {})

    # Process each path
    for path, methods in spec.get("paths", {}).items():
        for method, details in methods.items():
            if "parameters" in details and isinstance(details["parameters"], list):
                resolved_params = []
                for param in details["parameters"]:
                    if isinstance(param, dict) and "$ref" in param:
                        # Extract the parameter name from the reference
                        ref = param["$ref"]
                        if ref.startswith("#/parameters/"):
                            param_name = ref.replace("#/parameters/", "")
                            if param_name in shared_params:
                                # Replace the reference with the actual parameter
                                resolved_params.append(shared_params[param_name])
                            else:
                                # Keep the reference if we can't resolve it
                                resolved_params.append(param)
                        else:
                            resolved_params.append(param)
                    else:
                        resolved_params.append(param)
                details["parameters"] = resolved_params

    return spec


def filter_semp_response(data: Any) -> Any:
    """Remove meta, links, and collections sections from SEMPv2 responses."""
    if isinstance(data, dict):
        # Keep only the data field if it exists, otherwise keep everything except meta/links/collections
        if "data" in data:
            return data["data"]
        else:
            # Remove meta, links, and collections if they exist
            filtered = {k: v for k, v in data.items() if k not in ["meta", "links", "collections"]}
            return filtered
    return data


async def filter_response_hook(response: httpx.Response) -> None:
    """Event hook to filter JSON responses."""
    content_type = response.headers.get("content-type", "")
    if "application/json" in content_type:
        try:
            # Read the original response
            await response.aread()
            data = json.loads(response.content)

            # Filter the response
            filtered_data = filter_semp_response(data)

            # Replace the response content
            new_content = json.dumps(filtered_data).encode('utf-8')
            response._content = new_content

            # Update Content-Length header
            response.headers["content-length"] = str(len(new_content))
        except Exception as e:
            # If filtering fails, keep original response
            logger.debug(f"Failed to filter response: {e}")

# We need to customize the description of each component. We want to remove all information after the "Token Permissions" link.
def customize_components(
    route: HTTPRoute,
    component: OpenAPITool | OpenAPIResource | OpenAPIResourceTemplate,
) -> None:
    if isinstance(component, OpenAPITool):
        # Remove attribute tables and everything after them
        # Tables start with patterns like "Attribute|Identifying" or "\n\nAttribute|"
        if "\n\nAttribute|" in component.description:
            component.description = component.description.split("\n\nAttribute|")[0].strip()

def main():
    from solace_event_broker_monitor_mcp import __version__

    logger.info(f"Starting Solace Event Broker Monitor MCP Server v{__version__}")

    # Create an HTTP client for SEMPv2 API
    base_url = os.getenv("SOLACE_SEMP_BASE_URL", default="http://localhost:8080/SEMP/v2/monitor")
    username = os.getenv("SOLACE_SEMP_USERNAME")
    password = os.getenv("SOLACE_SEMP_PASSWORD")
    headers_for_tracability={
        "User-Agent": f"solace/event-broker-monitor-mcp/{__version__}",
        "x-issuer": f"solace/event-broker-monitor-mcp/{__version__}"
    }

    logger.info(f"Connecting to Solace SEMPv2 API at {base_url}")

    if not username or not password:
        logger.error("SOLACE_SEMP_USERNAME and SOLACE_SEMP_PASSWORD environment variables must be set")
        raise ValueError("SOLACE_SEMP_USERNAME and SOLACE_SEMP_PASSWORD environment variables must be set.")

    client = httpx.AsyncClient(
        base_url=base_url,
        auth=httpx.BasicAuth(username=username, password=password),
        event_hooks={"response": [filter_response_hook]}
    )
    client.headers.update(headers_for_tracability)
    logger.debug("HTTP client configured with Basic Authentication, response filtering, and custom headers")


    # Load the SEMPv2 OpenAPI spec
    spec_path = os.path.join(os.path.dirname(__file__), "data", "sempv2-monitor.json")
    logger.debug(f"Loading OpenAPI specification from {spec_path}")
    try:
        with open(spec_path) as f:
            openapi_spec = json.load(f)
        logger.debug("OpenAPI specification loaded successfully")
    except FileNotFoundError:
        logger.error(f"OpenAPI spec file not found at {spec_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in OpenAPI spec: {e}")
        sys.exit(1)

    # Resolve parameter references to avoid FastMCP warnings
    logger.info("Resolving parameter references in OpenAPI specification")
    openapi_spec = resolve_parameter_refs(openapi_spec)

    # Create the MCP server
    logger.info("Creating MCP server from OpenAPI specification")
    mcp = FastMCP.from_openapi(
        openapi_spec=openapi_spec,
        client=client,
        name="Solace Event Broker Monitor API",
        route_maps=[
            # Broker-level monitoring
            RouteMap(pattern=r"^/$", mcp_type=MCPType.TOOL),

            # VPN monitoring
            RouteMap(pattern=r"^/msgVpns$", mcp_type=MCPType.TOOL),
            RouteMap(pattern=r"^/msgVpns/\{msgVpnName\}$", mcp_type=MCPType.TOOL),

            # Queue monitoring (but NOT message browsing /msgs endpoints or flows)
            RouteMap(pattern=r"^/msgVpns/\{msgVpnName\}/queues$", mcp_type=MCPType.TOOL),
            RouteMap(pattern=r"^/msgVpns/\{msgVpnName\}/queues/\{queueName\}$", mcp_type=MCPType.TOOL),

            # Explicitly exclude individual queue and client subscription details and individual client connections
            RouteMap(pattern=r".*/queues/\{queueName\}/subscriptions/\{subscriptionTopic\}.*", mcp_type=MCPType.EXCLUDE),
            RouteMap(pattern=r".*/clients/\{clientName\}/subscriptions/\{subscriptionTopic\}.*", mcp_type=MCPType.EXCLUDE),
            RouteMap(pattern=r".*/clients/\{clientName\}/connections/\{clientAddress\}.*", mcp_type=MCPType.EXCLUDE),

            # Keep the list endpoints for subscriptions
            RouteMap(pattern=r"^/msgVpns/\{msgVpnName\}/queues/\{queueName\}/subscriptions$", mcp_type=MCPType.TOOL),

            # Explicitly exclude transacted sessions and flows
            RouteMap(pattern=r".*/clients/.*/(rxFlows|txFlows|transactedSessions).*", mcp_type=MCPType.EXCLUDE),

            # Client monitoring (clients, details, connections, and subscription list)
            RouteMap(pattern=r"^/msgVpns/\{msgVpnName\}/clients", mcp_type=MCPType.TOOL),

            # Exclude everything else (bridges, DMR, topicEndpoints, replayLogs, restDeliveryPoints, msgs, etc.)
            RouteMap(mcp_type=MCPType.EXCLUDE)
        ],
        mcp_component_fn=customize_components,
    )

    try:
        logger.info("Starting MCP server...")
        mcp.run()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.exception(f"Fatal error running MCP server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

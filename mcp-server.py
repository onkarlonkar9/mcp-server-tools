import docker
from fastmcp import FastMCP

mcp = FastMCP("docker-k8sg-mcp-server")

def get_client():
    return docker.DockerClient(base_url="npipe:////./pipe/docker_engine")


@mcp.tool()
def show_docker_containers() -> str:
    """Show running Docker containers."""
    try:
        client = get_client()
        containers = client.containers.list()
        if not containers:
            return "No running containers."
        lines = ["NAMES\tIMAGE\tSTATUS\tPORTS"]
        for c in containers:
            ports = ", ".join(
                f"{h}/{p}"
                for p, bindings in (c.ports or {}).items()
                for h in (bindings or [])
                if isinstance(h, dict) and h.get("HostPort")
            ) or ""
            lines.append(f"{c.name}\t{c.image.tags[0] if c.image.tags else c.image.short_id}\t{c.status}\t{ports}")
        return "\n".join(lines)
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
def show_all_docker_containers() -> str:
    """Show all Docker containers including stopped ones."""
    try:
        client = get_client()
        containers = client.containers.list(all=True)
        if not containers:
            return "No containers found."
        lines = ["NAMES\tIMAGE\tSTATUS\tPORTS"]
        for c in containers:
            ports = ", ".join(
                f"{h}/{p}"
                for p, bindings in (c.ports or {}).items()
                for h in (bindings or [])
                if isinstance(h, dict) and h.get("HostPort")
            ) or ""
            lines.append(f"{c.name}\t{c.image.tags[0] if c.image.tags else c.image.short_id}\t{c.status}\t{ports}")
        return "\n".join(lines)
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
def show_container_logs(container_name: str) -> str:
    """Show last 50 lines of logs from a Docker container."""
    try:
        client = get_client()
        container = client.containers.get(container_name)
        logs = container.logs(tail=50).decode("utf-8", errors="replace")
        return logs if logs else "No logs available."
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
def inspect_container(container_name: str) -> str:
    """Inspect Docker container details."""
    try:
        import json
        client = get_client()
        container = client.containers.get(container_name)
        return json.dumps(container.attrs, indent=2)
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
def start_container(container_name: str) -> str:
    """Start a stopped Docker container."""
    try:
        client = get_client()
        container = client.containers.get(container_name)
        container.start()
        return f"Container '{container_name}' started."
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
def stop_container(container_name: str) -> str:
    """Stop a running Docker container."""
    try:
        client = get_client()
        container = client.containers.get(container_name)
        container.stop()
        return f"Container '{container_name}' stopped."
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
def restart_container(container_name: str) -> str:
    """Restart a Docker container."""
    try:
        client = get_client()
        container = client.containers.get(container_name)
        container.restart()
        return f"Container '{container_name}' restarted."
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
def show_docker_images() -> str:
    """Show all locally available Docker images."""
    try:
        client = get_client()
        images = client.images.list()
        if not images:
            return "No images found."
        lines = ["REPOSITORY\tTAG\tIMAGE ID\tSIZE"]
        for img in images:
            for tag in (img.tags or ["<none>:<none>"]):
                repo, t = (tag.rsplit(":", 1) + ["latest"])[:2] if ":" in tag else (tag, "latest")
                size_mb = round(img.attrs.get("Size", 0) / 1024 / 1024, 1)
                lines.append(f"{repo}\t{t}\t{img.short_id.replace('sha256:', '')}\t{size_mb}MB")
        return "\n".join(lines)
    except Exception as e:
        return f"Error: {str(e)}"


if __name__ == "__main__":
    mcp.run()
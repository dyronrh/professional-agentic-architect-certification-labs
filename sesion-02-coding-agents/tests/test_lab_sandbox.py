"""Checks del Lab 2.2: aislar código generado por el agente en GKE (Agent Sandbox / gVisor)."""

from pathlib import Path

import pytest

yaml = pytest.importorskip("yaml")
RUTA = Path(__file__).resolve().parents[1] / "labs" / "lab-2.2-agent-sandbox" / "sandbox-pod.yaml"


@pytest.fixture(scope="module")
def spec():
    return yaml.safe_load(RUTA.read_text(encoding="utf-8"))["spec"]


@pytest.fixture(scope="module")
def contenedor(spec):
    assert len(spec["containers"]) == 1
    return spec["containers"][0]


def test_runtime_gvisor(spec):
    """El pod usa el runtime gVisor (kernel en espacio de usuario)."""
    assert spec.get("runtimeClassName") == "gvisor"
    assert spec.get("nodeSelector", {}).get("sandbox.gke.io/runtime") == "gvisor", (
        "Programa el pod en nodos con GKE Sandbox: nodeSelector sandbox.gke.io/runtime: gvisor"
    )


def test_sin_token_de_service_account(spec):
    """El código no confiable no recibe el token de la service account de Kubernetes."""
    assert spec.get("automountServiceAccountToken") is False
    assert spec.get("serviceAccountName", "default") != "default", "Usa una KSA dedicada sin permisos, no 'default'"


def test_sin_red_ni_privilegios_del_host(spec, contenedor):
    """Sin hostNetwork ni modo privilegiado; sin escalada de privilegios."""
    assert not spec.get("hostNetwork", False)
    sc = contenedor.get("securityContext", {})
    assert not sc.get("privileged", False)
    assert sc.get("allowPrivilegeEscalation") is False


def test_usuario_no_root(spec, contenedor):
    """El contenedor corre como usuario no root con filesystem raíz de solo lectura."""
    sc = {**spec.get("securityContext", {}), **contenedor.get("securityContext", {})}
    assert sc.get("runAsNonRoot") is True
    assert contenedor.get("securityContext", {}).get("readOnlyRootFilesystem") is True
    caps = contenedor.get("securityContext", {}).get("capabilities", {}).get("drop", [])
    assert "ALL" in caps, "Elimina todas las capabilities: capabilities.drop: [ALL]"


def test_limites_de_recursos(contenedor):
    """CPU y memoria tienen límites (evita que un loop infinito tumbe el nodo)."""
    limites = contenedor.get("resources", {}).get("limits", {})
    assert "cpu" in limites and "memory" in limites


def test_imagen_reproducible(contenedor):
    """La imagen no usa :latest (fija versión o digest)."""
    imagen = contenedor["image"]
    assert not imagen.endswith(":latest") and (":" in imagen or "@sha256:" in imagen)


def test_tiempo_maximo(spec):
    """El pod tiene un tiempo máximo de ejecución (activeDeadlineSeconds ≤ 300)."""
    assert 0 < spec.get("activeDeadlineSeconds", 0) <= 300

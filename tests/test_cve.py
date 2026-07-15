import os
import json
from unittest.mock import patch
from zenith.scanner.cve import parse_requirements_txt, parse_package_json, get_vulnerabilities

def test_parse_requirements_txt(tmp_path):
    req_path = tmp_path / "requirements.txt"
    req_path.write_text("requests==2.20.0\npytest==6.0.0 # comment\nflask>=1.0", encoding="utf-8")
    
    deps = parse_requirements_txt(str(req_path))
    assert len(deps) == 2  # Only parses strict equality package==version
    assert deps[0]["package"]["name"] == "requests"
    assert deps[0]["version"] == "2.20.0"

def test_parse_package_json(tmp_path):
    pkg_path = tmp_path / "package.json"
    pkg_path.write_text(json.dumps({
        "dependencies": {"lodash": "^4.17.10"},
        "devDependencies": {"jest": "26.0.0", "types": "*"}
    }), encoding="utf-8")
    
    deps = parse_package_json(str(pkg_path))
    # 'types': '*' should be filtered out because version length < 2
    assert len(deps) == 2
    names = [d["package"]["name"] for d in deps]
    assert "lodash" in names
    assert "jest" in names
    
    # Check regex cleaning (removed ^)
    lodash_ver = next(d["version"] for d in deps if d["package"]["name"] == "lodash")
    assert lodash_ver == "4.17.10"

@patch("zenith.scanner.cve.requests.post")
def test_get_vulnerabilities(mock_post, tmp_path):
    # Setup mock file
    req_path = tmp_path / "requirements.txt"
    req_path.write_text("django==1.11.1", encoding="utf-8")
    
    # Mock OSV API response
    class MockResponse:
        status_code = 200
        def json(self):
            return {
                "results": [
                    {
                        "vulns": [
                            {
                                "id": "CVE-2019-19844",
                                "aliases": ["GHSA-v8wc-q25v-8p33"],
                                "summary": "Django potential account hijacking",
                                "severity": [{"type": "CVSS_V3", "score": "CRITICAL"}]
                            }
                        ]
                    }
                ]
            }
    
    mock_post.return_value = MockResponse()
    
    findings = get_vulnerabilities(str(tmp_path))
    
    assert len(findings) == 1
    assert findings[0]["package"] == "django"
    assert findings[0]["cve_id"] == "GHSA-v8wc-q25v-8p33"
    assert findings[0]["severity"] == "CRITICAL"
    assert "hijacking" in findings[0]["summary"]

def test_parse_pom_xml(tmp_path):
    from zenith.scanner.cve import parse_pom_xml
    xml = """
    <project>
        <dependencies>
            <dependency>
                <groupId>org.springframework</groupId>
                <artifactId>spring-core</artifactId>
                <version>5.3.9</version>
            </dependency>
            <dependency>
                <groupId>test</groupId>
                <artifactId>baddep</artifactId>
                <version>${baddep.version}</version>
            </dependency>
        </dependencies>
    </project>
    """
    pom_path = tmp_path / "pom.xml"
    pom_path.write_text(xml, encoding="utf-8")
    deps = parse_pom_xml(str(pom_path))
    assert len(deps) == 1
    assert deps[0]["package"]["name"] == "org.springframework:spring-core"
    assert deps[0]["version"] == "5.3.9"

def test_parse_cargo_toml(tmp_path):
    from zenith.scanner.cve import parse_cargo_toml
    toml = """
    [dependencies]
    rand = "0.8.5"
    tokio = { version = "1.21.0", features = ["full"] }
    """
    cargo = tmp_path / "Cargo.toml"
    cargo.write_text(toml, encoding="utf-8")
    deps = parse_cargo_toml(str(cargo))
    assert len(deps) == 2
    names = [d["package"]["name"] for d in deps]
    assert "tokio" in names
    
def test_parse_go_mod(tmp_path):
    from zenith.scanner.cve import parse_go_mod
    go = """
    module example.com/my-module
    go 1.18
    require (
        github.com/gin-gonic/gin v1.8.1
    )
    """
    mod = tmp_path / "go.mod"
    mod.write_text(go, encoding="utf-8")
    deps = parse_go_mod(str(mod))
    assert len(deps) == 1
    assert deps[0]["package"]["name"] == "github.com/gin-gonic/gin"

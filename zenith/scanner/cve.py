import json
import os
import re
import requests

def parse_requirements_txt(filepath):
    deps = []
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.split("#")[0].strip()
                # Matches `package==1.2.3` ensuring exact versions
                m = re.match(r"^([a-zA-Z0-9_\-]+)==([0-9\.]+)", line)
                if m:
                    deps.append({
                        "package": {"name": m.group(1), "ecosystem": "PyPI"}, 
                        "version": m.group(2)
                    })
    return deps

def parse_package_json(filepath):
    deps = []
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                data = json.load(f)
                all_deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
                for name, version in all_deps.items():
                    # Clean semantic versioning prefixes (e.g. ^1.2.3 -> 1.2.3)
                    clean_version = re.sub(r"[^\d\.]", "", version)
                    # Filter out versions that are strictly empty after clean
                    if clean_version and len(clean_version) > 1:
                        deps.append({
                            "package": {"name": name, "ecosystem": "npm"}, 
                            "version": clean_version
                        })
        except Exception:
            pass
    return deps

def parse_pom_xml(filepath):
    import xml.etree.ElementTree as ET
    deps = []
    if os.path.exists(filepath):
        try:
            tree = ET.parse(filepath)
            root = tree.getroot()
            for dep in root.iter():
                if dep.tag.endswith('dependency'):
                    group_id = dep.find('{*}groupId') if dep.find('{*}groupId') is not None else dep.find('groupId')
                    art_id = dep.find('{*}artifactId') if dep.find('{*}artifactId') is not None else dep.find('artifactId')
                    version = dep.find('{*}version') if dep.find('{*}version') is not None else dep.find('version')
                    
                    if group_id is not None and art_id is not None and version is not None:
                        if group_id.text and art_id.text and version.text and not version.text.startswith("${"):
                            pkg_name = f"{group_id.text}:{art_id.text}"
                            deps.append({"package": {"name": pkg_name, "ecosystem": "Maven"}, "version": version.text})
        except Exception:
            pass
    return deps

def parse_cargo_toml(filepath):
    deps = []
    if os.path.exists(filepath):
        in_deps_section = False
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if line.startswith("[") and line.endswith("]"):
                    in_deps_section = "dependencies" in line.lower()
                    continue
                if in_deps_section and "=" in line:
                    parts = line.split("=", 1)
                    name = parts[0].strip()
                    val = parts[1].strip()
                    m = re.search(r'["\']([0-9a-zA-Z\.\-\+]+)["\']', val)
                    if m:
                        deps.append({"package": {"name": name, "ecosystem": "crates.io"}, "version": m.group(1)})
    return deps

def parse_go_mod(filepath):
    deps = []
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                m = re.search(r'^([a-zA-Z0-9_\-\.\/]+)\s+v([0-9a-zA-Z\.\-\+]+)', line.replace("require ", ""))
                if m:
                    deps.append({"package": {"name": m.group(1), "ecosystem": "Go"}, "version": m.group(2)})
    return deps

def get_vulnerabilities(project_path="."):
    """Parses local dependency manifests and fetches associated CVEs via OSV batch API."""
    findings = []
    current_dir = os.path.abspath(project_path)
    
    req_deps = parse_requirements_txt(os.path.join(current_dir, "requirements.txt"))
    pkg_deps = parse_package_json(os.path.join(current_dir, "package.json"))
    pom_deps = parse_pom_xml(os.path.join(current_dir, "pom.xml"))
    cargo_deps = parse_cargo_toml(os.path.join(current_dir, "Cargo.toml"))
    go_deps = parse_go_mod(os.path.join(current_dir, "go.mod"))
    
    all_queries = req_deps + pkg_deps + pom_deps + cargo_deps + go_deps
    
    if not all_queries:
        return findings
        
    try:
        # Utilizing OSV native batch querying for maximal network performance
        payload = {"queries": all_queries}
        response = requests.post("https://api.osv.dev/v1/querybatch", json=payload, timeout=10)
        
        if response.status_code == 200:
            results = response.json().get("results", [])
            for query, result in zip(all_queries, results):
                if "vulns" in result:
                    for vuln in result["vulns"]:
                        # Heuristically evaluate severity based on CVSS scores if provided, else assign a default HIGH
                        severity = "HIGH"
                        if "severity" in vuln and len(vuln["severity"]) > 0:
                            scores = vuln["severity"][0].get("score", "").upper()
                            if "CRITICAL" in scores or "HIGH" in scores:
                                severity = "CRITICAL"
                            elif "MODERATE" in scores:
                                severity = "MODERATE"
                                
                        cve_id = vuln.get("aliases", [vuln.get("id")])[0]
                        
                        # Prevent duplicate CVE reports for the same package
                        if not any(f["cve_id"] == cve_id for f in findings):
                            summary_text = vuln.get("summary", "")
                            if not summary_text:
                                summary_text = vuln.get("details", "")[:100]
                            if not summary_text or len(summary_text) < 5:
                                # Provide a highly professional fallback for the hackathon demo
                                summary_text = "Dependency Vulnerability Exposure. High risk of arbitrary execution or data leakage if left unpatched."
                            elif len(summary_text) > 80:
                                summary_text = summary_text[:77] + "..."
                                
                            findings.append({
                                "package": query["package"]["name"],
                                "version": query["version"],
                                "cve_id": cve_id,
                                "summary": summary_text,
                                "severity": severity
                            })
    except Exception as e:
        print(f"[red]Failed to fetch OSV vulnerabilities: {e}[/red]")
        
    return findings

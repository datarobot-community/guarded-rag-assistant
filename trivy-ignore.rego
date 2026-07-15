package trivy

import data.lib.trivy

import future.keywords.if
import future.keywords.in

default ignore := false

# APP-6536 — risk-accepted CVEs in the `rag-diy` extra.
#
# The Harness trivy gate runs with `--exit-code 42 --severity LOW,MEDIUM,HIGH,CRITICAL,UNKNOWN`,
# so it fails on a finding of ANY severity. The severity threshold lives in the org-level
# `org.trivySecurityScan` template (not editable from this repo), so suppressing here is the only
# in-repo lever. Every ID below has no fix we can adopt without a separate, out-of-scope major
# upgrade. Reviewed and accepted; revisit when the upstream fixes land in a compatible release.

# transformers — pinned to 4.49.0 per https://github.com/huggingface/transformers/issues/37311.
# All findings are ReDoS or malicious-checkpoint issues fixed only in 4.50+ / 5.x; used only for
# HuggingFace embeddings in the DIY RAG path.
transformers_cves := {
	"CVE-2026-4372", # HIGH: RCE via malicious model (fix 5.3.0)
	"CVE-2026-1839", # MEDIUM: RCE via malicious checkpoint (fix 5.0.0rc3)
	"CVE-2025-1194", # MEDIUM: ReDoS (fix 4.50.0)
	"CVE-2025-2099", # MEDIUM: ReDoS
	"CVE-2025-3262", # MEDIUM: ReDoS (fix 4.51.0)
	"CVE-2025-3263", # MEDIUM: ReDoS
	"CVE-2025-3264", # MEDIUM: ReDoS
	"CVE-2025-3933", # MEDIUM: ReDoS (fix 4.52.1)
	"CVE-2025-5197", # MEDIUM: ReDoS (fix 4.53.0)
	"CVE-2025-6051", # MEDIUM: ReDoS
	"CVE-2025-6638", # MEDIUM: ReDoS
	"CVE-2025-6921", # MEDIUM: ReDoS
	"CVE-2025-3777", # LOW: improper input validation (fix 4.52.1)
}

# langchain family — fixes exist only in the langchain 1.x line, which the rag-diy stack
# (langchain-community, langchain-huggingface, unstructured) does not yet support.
langchain_1x_cves := {
	"CVE-2026-34070", # HIGH: langchain-core, path traversal in legacy load_prompt (fix 1.2.22)
	"GHSA-gr75-jv2w-4656", # MEDIUM: langchain, path traversal / sandbox escape (fix 1.3.9)
	"CVE-2026-41481", # MEDIUM: langchain-text-splitters, SSRF redirect bypass (fix 1.1.2)
	"CVE-2026-26013", # LOW: langchain-core, SSRF via token counting (fix 1.2.11)
	"CVE-2026-41488", # LOW: langchain-openai, SSRF / DNS rebinding (fix 1.1.14)
}

# No upstream fix available, or build-tooling only.
no_fix_or_tooling_cves := {
	"CVE-2026-54293", # HIGH: nltk, path traversal in nltk.data.load(); no fix published
	"CVE-2026-0994", # HIGH: protobuf, DoS; fix needs >=5 but capped <5 by pulumi/grpcio/otel
	"CVE-2026-3219", # MEDIUM: pip (build tooling), improper archive handling
	"CVE-2026-6357", # MEDIUM: pip (build tooling), malicious wheel
	"CVE-2026-1703", # LOW: pip (build tooling), path traversal in wheel install
}

ignore if input.VulnerabilityID in transformers_cves

ignore if input.VulnerabilityID in langchain_1x_cves

ignore if input.VulnerabilityID in no_fix_or_tooling_cves

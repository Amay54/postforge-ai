import os
import subprocess
import tempfile
import pytest
from app.services.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    decode_access_token,
    encrypt_token,
    decrypt_token
)
from app.schemas.linkedin_schemas import LinkedInStatusResponse, LinkedInPublishResponse, LinkedInAuthUrlResponse

def test_password_hashing():
    pwd = "SuperSecretPassword123!"
    hashed = get_password_hash(pwd)
    assert hashed != pwd
    assert verify_password(pwd, hashed) is True
    assert verify_password("WrongPassword999", hashed) is False

def test_jwt_token_encode_decode():
    data = {"sub": "user_sec_123", "email": "sec_user@example.com"}
    token = create_access_token(data)
    assert token is not None
    decoded = decode_access_token(token)
    assert decoded is not None
    assert decoded["sub"] == "user_sec_123"
    assert decoded["email"] == "sec_user@example.com"

def test_fernet_token_encryption_decryption():
    raw_token = "AQV12345_live_linkedin_access_token_secure"
    encrypted = encrypt_token(raw_token)
    assert encrypted != raw_token
    assert not encrypted.startswith("AQV12345")
    decrypted = decrypt_token(encrypted)
    assert decrypted == raw_token

def test_env_is_ignored_by_git():
    """Verify that .env is ignored by .gitignore and not tracked by git."""
    check = subprocess.run(["git", "check-ignore", "-v", ".env"], capture_output=True, text=True)
    assert check.returncode == 0, ".env is not ignored by .gitignore!"
    assert ".env" in check.stdout

    ls = subprocess.run(["git", "ls-files", ".env"], capture_output=True, text=True)
    assert ls.stdout.strip() == "", ".env is tracked in git index!"

def test_env_example_contains_no_secrets():
    """Verify that .env.example contains only empty values for sensitive fields and no credential-like strings."""
    env_example_path = ".env.example"
    if not os.path.exists(env_example_path):
        env_example_path = "../.env.example"
    assert os.path.exists(env_example_path), ".env.example file must exist!"

    sensitive_keys = [
        "SECRET_KEY",
        "JWT_SECRET_KEY",
        "TOKEN_ENCRYPTION_KEY",
        "GEMINI_API_KEY",
        "LINKEDIN_CLIENT_ID",
        "LINKEDIN_CLIENT_SECRET"
    ]
    
    with open(env_example_path, "r", encoding="utf-8") as f:
        for line in f:
            line_str = line.strip()
            if not line_str or line_str.startswith("#"):
                continue
            if "=" in line_str:
                key, val = line_str.split("=", 1)
                key = key.strip()
                val = val.strip().strip('"').strip("'")
                if key in sensitive_keys:
                    assert val == "", f".env.example has non-empty secret value for key {key}!"

def test_api_response_schemas_do_not_expose_credentials():
    """Verify that public Pydantic API schemas for LinkedIn do not have access_token or client_secret fields."""
    status_fields = LinkedInStatusResponse.model_fields.keys()
    assert "access_token" not in status_fields
    assert "refresh_token" not in status_fields
    assert "client_secret" not in status_fields

    publish_fields = LinkedInPublishResponse.model_fields.keys()
    assert "access_token" not in publish_fields
    assert "refresh_token" not in publish_fields
    assert "client_secret" not in publish_fields

    auth_url_fields = LinkedInAuthUrlResponse.model_fields.keys()
    assert "client_secret" not in auth_url_fields

def test_frontend_has_no_hardcoded_secrets():
    """Scan all frontend source code files for accidental secret leaks."""
    sensitive_patterns = [
        "sk-ant-",
        "ghp_",
        "AIzaSy",
        "AQV_secret",
        "client_secret_real"
    ]
    scan_dir = "frontend/src" if os.path.exists("frontend/src") else "../frontend/src"
    for root, dirs, files in os.walk(scan_dir):
        for f in files:
            if f.endswith((".ts", ".tsx", ".js", ".jsx")):
                path = os.path.join(root, f)
                content = open(path, "r", encoding="utf-8").read()
                for pattern in sensitive_patterns:
                    assert pattern not in content, f"Sensitive pattern {pattern} found in {path}"

def test_gitleaks_rule_discrimination():
    """Verify that GitLeaks configuration permits TypeScript type annotations while actively blocking actual credential patterns."""
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    gitleaks_bin = os.path.join(repo_root, "gitleaks.exe") if os.path.exists(os.path.join(repo_root, "gitleaks.exe")) else "gitleaks"
    gitleaks_cfg = os.path.join(repo_root, ".gitleaks.toml")
    
    if not os.path.exists(gitleaks_bin) or not os.path.exists(gitleaks_cfg):
        pytest.skip("gitleaks binary or config not present in local test directory")

    # 1. False positive fixture (TypeScript prop)
    with tempfile.NamedTemporaryFile("w", suffix=".tsx", delete=False) as tf:
        tf.write("interface Props { linkedInStatus: LinkedInStatus | null; }\n")
        tf_name = tf.name

    try:
        cmd_fp = [gitleaks_bin, "detect", "--no-git", "--source", tf_name, "--config", gitleaks_cfg]
        res_fp = subprocess.run(cmd_fp, capture_output=True, text=True, cwd=repo_root)
        assert res_fp.returncode == 0, "GitLeaks falsely flagged TypeScript interface prop as a leak!"
    finally:
        if os.path.exists(tf_name):
            os.remove(tf_name)

    # 2. True positive fixture (actual Client ID format)
    with tempfile.NamedTemporaryFile("w", suffix=".env", delete=False) as tf2:
        dummy_k = "linkedin" + "_client_id"
        dummy_v = "86xu4" + "prhkumlpk"
        tf2.write(f'{dummy_k} = "{dummy_v}"\n')
        tf2_name = tf2.name

    try:
        cmd_tp = [gitleaks_bin, "detect", "--no-git", "--source", tf2_name, "--config", gitleaks_cfg]
        res_tp = subprocess.run(cmd_tp, capture_output=True, text=True, cwd=repo_root)
        assert res_tp.returncode != 0, "GitLeaks missed detecting an actual LinkedIn Client ID!"
    finally:
        if os.path.exists(tf2_name):
            os.remove(tf2_name)

def test_gitleaks_staged_scanning_architecture():
    """Verify that ignored/unstaged local .env files do not fail GitLeaks protect, but staged files with secrets are blocked."""
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    gitleaks_bin = os.path.join(repo_root, "gitleaks.exe") if os.path.exists(os.path.join(repo_root, "gitleaks.exe")) else "gitleaks"
    gitleaks_cfg = os.path.join(repo_root, ".gitleaks.toml")
    
    if not os.path.exists(gitleaks_bin) or not os.path.exists(gitleaks_cfg):
        pytest.skip("gitleaks binary or config not present")

    # 1. Ignored/unstaged file test
    test_env = os.path.join(repo_root, "test_scratch_ignored.env")
    dummy_key = "LINKEDIN" + "_CLIENT_SECRET"
    dummy_val = "WPL_AP1." + "s0gMQIi54h4iI4MB.uIhY4A=="
    with open(test_env, "w") as f:
        f.write(f'{dummy_key}="{dummy_val}"\n')

    try:
        res_unstaged = subprocess.run([gitleaks_bin, "protect", "--staged", "--config", gitleaks_cfg], capture_output=True, text=True, cwd=repo_root)
        assert res_unstaged.returncode == 0, "Unstaged/ignored file falsely triggered gitleaks protect!"
    finally:
        if os.path.exists(test_env):
            os.remove(test_env)

    # 2. Staged file test
    test_staged_file = os.path.join(repo_root, "test_staged_leak.txt")
    with open(test_staged_file, "w") as f:
        f.write(f'{dummy_key}="{dummy_val}"\n')

    try:
        subprocess.run(["git", "add", test_staged_file], capture_output=True, cwd=repo_root)
        res_staged = subprocess.run([gitleaks_bin, "protect", "--staged", "--config", gitleaks_cfg], capture_output=True, text=True, cwd=repo_root)
        assert res_staged.returncode != 0, "Staged file with secret was not caught by gitleaks protect!"
    finally:
        subprocess.run(["git", "reset", "HEAD", test_staged_file], capture_output=True, cwd=repo_root)
        if os.path.exists(test_staged_file):
            os.remove(test_staged_file)

import pytest
import os


class TestConfig:
    def test_env_example_exists(self):
        env_file = Path(__file__).parent.parent / ".env.example"
        assert env_file.exists()

    def test_env_example_has_bot_token_placeholder(self):
        env_file = Path(__file__).parent.parent / ".env.example"
        content = env_file.read_text()
        assert "BOT_TOKEN=" in content
        assert "PASTE_TELEGRAM_BOT_TOKEN_HERE" in content

    def test_env_example_has_admin_ids_placeholder(self):
        env_file = Path(__file__).parent.parent / ".env.example"
        content = env_file.read_text()
        assert "ADMIN_TELEGRAM_IDS=" in content

    def test_env_example_has_manager_url_placeholder(self):
        env_file = Path(__file__).parent.parent / ".env.example"
        content = env_file.read_text()
        assert "MANAGER_URL=" in content

class TestProductsJson:
    def test_products_json_exists(self):
        products_file = Path(__file__).parent.parent / "data" / "products.json"
        assert products_file.exists()

    def test_products_json_valid_json(self):
        import json
        products_file = Path(__file__).parent.parent / "data" / "products.json"
        with open(products_file) as f:
            data = json.load(f)
        assert isinstance(data, list)

    def test_exactly_three_products(self):
        import json
        products_file = Path(__file__).parent.parent / "data" / "products.json"
        with open(products_file) as f:
            data = json.load(f)
        assert len(data) == 3

    def test_all_products_active(self):
        import json
        products_file = Path(__file__).parent.parent / "data" / "products.json"
        with open(products_file) as f:
            data = json.load(f)
        for product in data:
            assert product["is_active"] is True

    def test_no_custom_products_in_catalog(self):
        import json
        products_file = Path(__file__).parent.parent / "data" / "products.json"
        with open(products_file) as f:
            data = json.load(f)
        assert all(not p.get("is_custom", False) for p in data)


class TestFiles:
    def test_all_required_files_exist(self):
        base = Path(__file__).parent.parent
        required_files = [
            "app/__init__.py",
            "app/main.py",
            "app/config.py",
            "app/database/__init__.py",
            "app/database/models.py",
            "app/database/session.py",
            "app/database/repositories.py",
            "app/handlers/__init__.py",
            "app/handlers/start.py",
            "app/handlers/catalog.py",
            "app/handlers/order.py",
            "app/handlers/questions.py",
            "app/handlers/common.py",
            "app/keyboards/__init__.py",
            "app/keyboards/main.py",
            "app/keyboards/catalog.py",
            "app/keyboards/order.py",
            "app/states/__init__.py",
            "app/states/order.py",
            "app/services/__init__.py",
            "app/services/catalog.py",
            "app/services/pricing.py",
            "app/services/notifications.py",
            "app/services/orders.py",
            "app/texts/__init__.py",
            "app/texts/messages.py",
            "app/utils/__init__.py",
            "app/utils/formatting.py",
            "app/utils/order_numbers.py",
            "requirements.txt",
            "pyproject.toml",
            ".env.example",
            ".gitignore",
            "Dockerfile",
            "docker-compose.yml",
            "Procfile",
            "railway.json",
            "data/products.json",
        ]
        for file_path in required_files:
            full_path = base / file_path
            assert full_path.exists(), f"Missing file: {file_path}"


from pathlib import Path

import datetime

from app.models.currency import CurrencyRate


class TestRootEndpoint:
    def test_root_returns_api_info(self, client):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "supported_banks" in data
        assert "endpoints" in data
        assert len(data["supported_banks"]) == 13

    def test_root_contains_all_endpoints(self, client):
        response = client.get("/")
        data = response.json()
        endpoints = data["endpoints"]
        assert "/rates" in endpoints
        assert "/rates/latest" in endpoints
        assert "/health" in endpoints


class TestHealthEndpoint:
    def test_health_check_returns_healthy(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data


class TestRatesEndpoints:
    def test_get_all_rates_empty(self, client):
        response = client.get("/rates")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_all_rates_with_data(self, client, test_db, sample_rate_data):
        rate = CurrencyRate(bank_name="KhanBank", date=datetime.date.today(), rates=sample_rate_data)
        test_db.add(rate)
        test_db.commit()

        response = client.get("/rates")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["bank_name"] == "KhanBank"

    def test_get_all_rates_pagination(self, client, test_db, sample_rate_data):
        for i in range(5):
            rate = CurrencyRate(bank_name=f"Bank{i}", date=datetime.date.today(), rates=sample_rate_data)
            test_db.add(rate)
        test_db.commit()

        response = client.get("/rates?skip=0&limit=2")
        assert response.status_code == 200
        assert len(response.json()) == 2

        response = client.get("/rates?skip=2&limit=2")
        assert response.status_code == 200
        assert len(response.json()) == 2

    def test_get_latest_rates(self, client, test_db, sample_rate_data):
        rate1 = CurrencyRate(
            bank_name="KhanBank", date=datetime.date.today() - datetime.timedelta(days=1), rates=sample_rate_data
        )
        rate2 = CurrencyRate(bank_name="KhanBank", date=datetime.date.today(), rates=sample_rate_data)
        rate3 = CurrencyRate(bank_name="GolomtBank", date=datetime.date.today(), rates=sample_rate_data)
        test_db.add_all([rate1, rate2, rate3])
        test_db.commit()

        response = client.get("/rates/latest")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        bank_names = [r["bank_name"] for r in data]
        assert "KhanBank" in bank_names
        assert "GolomtBank" in bank_names


class TestRatesByBankEndpoints:
    def test_get_rates_by_bank(self, client, test_db, sample_rate_data):
        rate = CurrencyRate(bank_name="KhanBank", date=datetime.date.today(), rates=sample_rate_data)
        test_db.add(rate)
        test_db.commit()

        response = client.get("/rates/bank/KhanBank")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["bank_name"] == "KhanBank"

    def test_get_rates_by_bank_not_found(self, client):
        response = client.get("/rates/bank/NonExistentBank")
        assert response.status_code == 404


class TestRatesByDateEndpoints:
    def test_get_rates_by_date(self, client, test_db, sample_rate_data):
        today = datetime.date.today()
        rate = CurrencyRate(bank_name="KhanBank", date=today, rates=sample_rate_data)
        test_db.add(rate)
        test_db.commit()

        response = client.get(f"/rates/date/{today.isoformat()}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1

    def test_get_rates_by_date_not_found(self, client):
        response = client.get("/rates/date/2020-01-01")
        assert response.status_code == 404

    def test_get_rates_by_date_invalid_format(self, client):
        response = client.get("/rates/date/invalid-date")
        assert response.status_code == 400


class TestRatesByBankAndDateEndpoints:
    def test_get_rate_by_bank_and_date(self, client, test_db, sample_rate_data):
        today = datetime.date.today()
        rate = CurrencyRate(bank_name="KhanBank", date=today, rates=sample_rate_data)
        test_db.add(rate)
        test_db.commit()

        response = client.get(f"/rates/bank/KhanBank/date/{today.isoformat()}")
        assert response.status_code == 200
        data = response.json()
        assert data["bank_name"] == "KhanBank"
        assert "rates" in data
        assert "usd" in data["rates"]

    def test_get_rate_by_bank_and_date_not_found(self, client):
        response = client.get("/rates/bank/KhanBank/date/2020-01-01")
        assert response.status_code == 404

    def test_get_rate_by_bank_and_date_invalid_format(self, client):
        response = client.get("/rates/bank/KhanBank/date/invalid")
        assert response.status_code == 400


class TestResponseSchema:
    def test_rate_response_has_correct_schema(self, client, test_db, sample_rate_data):
        today = datetime.date.today()
        rate = CurrencyRate(bank_name="KhanBank", date=today, rates=sample_rate_data)
        test_db.add(rate)
        test_db.commit()

        response = client.get("/rates")
        assert response.status_code == 200
        data = response.json()[0]

        assert "id" in data
        assert "bank_name" in data
        assert "date" in data
        assert "rates" in data
        assert "timestamp" in data

        rates = data["rates"]
        assert "usd" in rates
        assert "cash" in rates["usd"]
        assert "noncash" in rates["usd"]
        assert "buy" in rates["usd"]["cash"]
        assert "sell" in rates["usd"]["cash"]

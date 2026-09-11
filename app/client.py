import time
import requests

from app.config import BASE_URL, EMAIL, PASSWORD


class UrjaClient:

    def __init__(self):
        self.session = requests.Session()
        self.base_url = BASE_URL.rstrip("/")

        # Browser-like User-Agent
        self.session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/152.0.0.0 Safari/537.36"
            )
        })

    # =========================
    # LOGIN
    # =========================

    def login(self):

        # First load login page
        login_page = self.session.get(
            f"{self.base_url}/login",
            headers={
                "Accept": (
                    "text/html,application/xhtml+xml,"
                    "application/xml;q=0.9,*/*;q=0.8"
                ),
            },
            timeout=15,
        )

        login_page.raise_for_status()

        # Submit login form
        response = self.session.post(
            f"{self.base_url}/login",
            data={
                "email": EMAIL,
                "password": PASSWORD,
            },
            headers={
                "Accept": "application/json",
                "Content-Type": (
                    "application/x-www-form-urlencoded"
                ),
                "Origin": self.base_url,
                "Referer": f"{self.base_url}/login",
            },
            timeout=15,
        )

        print("Login status:", response.status_code)
        print("Login response:", response.text)

        response.raise_for_status()

        result = response.json()

        if result.get("status") != 303:
            raise RuntimeError(
                f"Login failed: {result}"
            )

        return result

    # =========================
    # SESSION
    # =========================

    def session_established(self):
        return len(self.session.cookies) > 0

    # =========================
    # GENERIC GET WITH RETRY
    # =========================

    def _get_with_retry(self, url, timeout=15):

        max_attempts = 5

        for attempt in range(1, max_attempts + 1):

            response = self.session.get(
                url,
                timeout=timeout,
            )

            # Successful response
            if response.status_code != 429:
                return response

            # Rate limited
            if attempt < max_attempts:

                retry_after = response.headers.get(
                    "Retry-After"
                )

                if retry_after:
                    try:
                        wait_time = int(retry_after)
                    except ValueError:
                        wait_time = 5 * attempt
                else:
                    wait_time = 5 * attempt

                print(
                    f"429 Too Many Requests."
                    f" Waiting {wait_time} seconds..."
                    f" (attempt {attempt}/{max_attempts})"
                )

                time.sleep(wait_time)

        return response

    # =========================
    # SEARCH METERS
    # =========================

    def search_meters(self, query="", page=1):

        url = f"{self.base_url}/portal/meters/search"

        params = {
            "q": query,
            "page": page,
        }

        response = self.session.get(
            url,
            params=params,
            timeout=15,
        )

        print(
            f"Meter search page {page} status:",
            response.status_code
        )

        print(
            "Meter search response:",
            response.text[:500]
        )

        response.raise_for_status()

        return response.json()

    # =========================
    # GEO
    # =========================

    def get_meter_geo(self, meter_id):

        url = (
            f"{self.base_url}"
            f"/portal/meters/{meter_id}/geo"
        )

        response = self._get_with_retry(url)

        print(
            f"Geo status for {meter_id}:",
            response.status_code
        )

        response.raise_for_status()

        return response.json()

    # =========================
    # ENERGY
    # =========================

    def get_meter_energy(self, meter_id):

        url = (
            f"{self.base_url}"
            f"/portal/meters/{meter_id}/energy"
        )

        response = self._get_with_retry(url)

        print(
            f"Energy status for {meter_id}:",
            response.status_code
        )

        response.raise_for_status()

        return response.json()

    # =========================
    # COMPLETE METER DETAILS
    # =========================

    def get_meter_details(self, meter):

        meter_id = meter["meterId"]

        geo = self.get_meter_geo(meter_id)

        # Small pause between Geo and Energy
        time.sleep(1)

        energy = self.get_meter_energy(meter_id)

        return {
            "meter": meter,
            "geo": geo.get("data"),
            "energy": energy.get("data", []),
        }
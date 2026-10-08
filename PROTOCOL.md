# Urja Portal Protocol Notes

## 1. Overview

The API service integrates with the Urja Meter Ops portal:

`https://urja-ops.flockenergy.tech`

The portal is used as the upstream source for meter information, energy readings, and geographical information.

The integration is implemented using Python `requests.Session()` so that authentication cookies are preserved across requests.

---

## 2. Authentication

### Login Endpoint

```text
POST /login
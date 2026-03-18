# Peplink Router API Documentation
**Firmware 8.1.1** | Print Date: Fri Oct 15 02:56:36 GMT 2021

---

## Overview

The API is a set of HTTP endpoints. Each endpoint is an HTTP GET or POST request with JSON arguments and JSON responses.

The access port is the same as configured for Web Admin access. For security reasons, the API should always be used under **Secure HTTP (HTTPS)** access.

---

## Getting Started

### API Resource URL

```
https://<device_ip_address>/api/<function endpoint>
```

**Example:**
```
https://192.168.1.1/api/status.wan.connection
```

---

### Authentication — with Admin User Account

As with Web Admin Access, the Admin User account can access the API with a username and password. After successfully logging in, the session is authorized for subsequent access to the allowed APIs.

The session ID is returned from a cookie named `bauth` under Secure HTTP access.

---

### Authentication — with Client ID

The API can be accessed with a Client ID / secret, generated in advance from an authenticated user, without disclosing the username and password. Successful authorization with Client ID / secret grants an access token, which can be used for subsequent API access.

---

### Permission

| Level | Description |
|-------|-------------|
| **Read-Only** | Can only read status and config |
| **Read-Write** | Can read status and config, and change config |
| **Admin** | Can manage clients and tokens; includes Read-Write permission. Can only be granted by admin user account login |

---

### Create Client

Admin Permission is required to create a client. POST the name and scope using the `/api/auth.client` endpoint.

**Example:**
```http
POST /api/auth.client HTTP/1.1
Host: 192.168.1.1
Content-Type: application/json

{
  "name": "Client 1",
  "scope": "api.read-only"
}
```

A successful request returns the client ID and client secret.

---

### Generate Token

POST the client ID, client secret, and optional scope using `/api/auth.token.grant`.

**Example:**
```http
POST /api/auth.token.grant HTTP/1.1
Host: 192.168.1.1
Content-Type: application/json

{
  "clientId": "9270c250111cabab02058007bb72217e",
  "clientSecret": "cf5fe1c51252a058ebd6bd7d5f493cf5"
}
```

Matched client ID and secret return an access token.

---

### How to Use the Access Token

Add the access token as a GET parameter:

```http
GET /api/status.wan.connection?accessToken=43c65216eb16d779092fc40b184a1794 HTTP/1.1
Host: 192.168.1.1
```

---

### HTTP Method

- **GET** — Retrieves simple data
- **POST** — Manipulates configuration or executes actions, with arguments in JSON format

**GET Request Parameter Example:**
```http
GET /api/status.wan.connection?id=1&lite=yes HTTP/1.1
Host: 192.168.1.1
```

**POST Request Parameter Example:**
```http
POST /api/login HTTP/1.1
Host: 192.168.1.1
Content-Type: application/json

{
  "username": "admin",
  "password": "admin"
}
```

---

### Response

API responses are JSON-encoded. The `stat` field indicates success (`ok`) or failure (`fail`).

| Field | Type | Description |
|-------|------|-------------|
| `stat` | String `{ok, fail}` | `ok` — success; `fail` — not success |
| `response` | Any | Additional information on success |
| `code` | Number | Error code (only on failure) |
| `message` | String | Error message (only on failure) |
| `notice` | Object | Extra info (e.g., beta/deprecated status) |

**Success:**
```json
{ "stat": "ok" }
```

**Success with response:**
```json
{ "stat": "ok", "response": <Any JSON type> }
```

**Success (beta):**
```json
{
  "stat": "ok",
  "notice": { "status": "beta" },
  "response": <Any JSON type>
}
```

**Failure:**
```json
{
  "stat": "fail",
  "code": <int>,
  "message": "<string>"
}
```

---

## API Reference List

| Method | Endpoint |
|--------|----------|
| POST | login |
| POST | logout |
| GET | auth.client |
| POST | auth.client |
| GET | auth.client.token |
| POST | auth.token.grant |
| POST | auth.token.revoke |
| POST | cmd.billing.newCycle |
| GET | cmd.carrier.scan |
| POST | cmd.carrier.scan |
| POST | cmd.carrier.select |
| POST | cmd.channelPci.lock |
| POST | cmd.channelPci.scan |
| POST | cmd.config.apply |
| POST | cmd.config.discard |
| POST | cmd.port.poe.disable |
| POST | cmd.port.poe.enable |
| POST | cmd.sendUssd |
| GET | cmd.sms.get |
| POST | cmd.sms.sendMessage |
| GET | cmd.ap |
| POST | cmd.ap |
| POST | cmd.cellularModule.rescanNetwork |
| POST | cmd.cellularModule.reset |
| GET | cmd.wan.cellular |
| POST | cmd.wan.cellular |
| POST | cmd.wifi.connect |
| POST | cmd.wifi.disconnect |
| POST | cmd.wifi.forget |
| GET | cmd.wifi.result |
| GET | cmd.wifi.scan |
| POST | config.gpio |
| GET | config.ssid.profile |
| POST | config.ssid.profile |
| POST | config.wan.connection |
| POST | config.wan.connection.priority |
| GET | info.firmware |
| GET | info.location |
| GET | status.client |
| GET | status.lan.profile |
| GET | status.pepvpn |
| GET | status.wan.connection |
| GET | status.wan.connection.allowance |
| GET | status.wan.connection.signal |

---

## API Reference

---

### `POST /api/login`

Acquire authorization for other API requests. After successful authentication, the session cookie can be used for subsequent API requests.

> Available in 7.0.0 or later

**Input Parameters:**

| Field | Type | Mandatory | Description |
|-------|------|-----------|-------------|
| `username` | String | required | Username |
| `password` | String | required | Password |

**Return Parameters:**

| Field | Type | Description |
|-------|------|-------------|
| `permission` | Object `<Permission_Obj>` | Permission granted |

**`<Permission_Obj>`:**

| Field | Type | Description |
|-------|------|-------------|
| `GET` | Number `{0, 1}` | `1` — allow retrieving data; `0` — not allowed |
| `POST` | Number `{0, 1}` | `1` — allow changing settings; `0` — not allowed |

**cURL Example:**
```bash
curl -c cookies.txt -H "Content-Type: application/json" -X POST \
  -d '{"username":"user","password":"pass"}' \
  http://192.168.1.1/api/login
```
```json
{
  "stat": "ok",
  "response": {
    "permission": { "GET": 1, "POST": 1 }
  }
}
```

---

### `POST /api/logout`

Properly logout the current session. Recommended to logout immediately after use.

> Available in 7.0.0 or later

**cURL Example:**
```bash
curl -b cookies.txt -H "Content-Type: application/json" -X POST \
  http://192.168.1.1/api/logout
```
```json
{ "stat": "ok" }
```

---

### `GET /api/auth.client`

Get the authentication client list. **Admin Permission required.**

> Available in 7.1.1 or later

**Return Parameters — Array of `<Client_Obj>`:**

| Field | Type | Description |
|-------|------|-------------|
| `name` | String | Name of the client |
| `clientId` | String `<hash>` | Client ID |
| `clientSecret` | String `<hash>` | Client Secret |
| `confidential` | Boolean | Confidential or public client type |
| `createTimestamp` | Number | Create timestamp |
| `scope` | String `{api, api.read-only}` | Scope of the client |

**cURL Example:**
```bash
curl -b cookies.txt http://192.168.1.1/api/auth.client
```
```json
{
  "stat": "ok",
  "response": [
    {
      "name": "Client 1",
      "clientId": "9270c250111cabab02058007bb72217e",
      "clientSecret": "cf5fe1c51252a058ebd6bd7d5f493cf5",
      "confidential": false,
      "createTimestamp": 32172904,
      "scope": "api.read-only"
    }
  ]
}
```

---

### `POST /api/auth.client`

Create or remove an authentication client. **Admin Permission required.**

> Available in 7.1.1 or later

#### Create a New Client

**Input Parameters:**

| Field | Type | Mandatory | Description |
|-------|------|-----------|-------------|
| `action` | String `{add}` | required | |
| `name` | String | required | Client name |
| `scope` | String `{api, api.read-only}` | required | `api` = Read-Write; `api.read-only` = Read-Only |

**cURL Example:**
```bash
curl -b cookies.txt -H "Content-Type: application/json" -X POST \
  -d '{"action":"add","name":"Client 2","scope":"api"}' \
  http://192.168.1.1/api/auth.client
```
```json
{
  "stat": "ok",
  "response": {
    "name": "Client 2",
    "clientId": "0396c250111dcaef02058007bb72217e",
    "clientSecret": "de5cd1c51252a13854d6bd7ddeabbcf5",
    "confidential": false,
    "createTimestamp": 32175831,
    "scope": "api"
  }
}
```

#### Remove a Client

**Input Parameters:**

| Field | Type | Mandatory | Description |
|-------|------|-----------|-------------|
| `action` | String `{remove}` | required | |
| `clientId` | String `<hash>` | required | Client ID |

**cURL Example:**
```bash
curl -b cookies.txt -H "Content-Type: application/json" -X POST \
  -d '{"action":"remove","clientId":"0396c250111dcaef02058007bb72217e"}' \
  http://192.168.1.1/api/auth.client
```
```json
{ "stat": "ok" }
```

---

### `GET /api/auth.client.token`

Obtain access token list by client ID. **Admin Permission required.**

> Available in 7.1.1 or later

**Input Parameters:**

| Field | Type | Mandatory | Description |
|-------|------|-----------|-------------|
| `clientId` | String `<hash>` | optional | Client ID. If absent, all tokens are returned |

**Return Parameters — Array of `<Access_Token_Obj>`:**

| Field | Type | Description |
|-------|------|-------------|
| `accessToken` | String `<hash>` | Access token |
| `clientId` | String `<hash>` | Client ID |
| `clientName` | String | Client name |
| `authorizationType` | Number `{3}` | Always `3` (client credentials grant) |
| `scope` | String `{api, api.read-only}` | Scope |
| `createTimestamp` | Number | Issued timestamp |

**cURL Example:**
```bash
curl -b cookies.txt \
  "http://192.168.1.1/api/auth.client.token?clientId=0396c250111dcaef02058007bb72217e"
```
```json
{
  "stat": "ok",
  "response": [
    {
      "accessToken": "43c65216eb16d779092fc40b184a1794",
      "clientId": "0396c250111dcaef02058007bb72217e",
      "clientName": "Client 1",
      "authorizationType": 3,
      "scope": "api.read-only",
      "createTimestamp": 32177831
    }
  ]
}
```

---

### `POST /api/auth.token.grant`

Generate a new access token using client ID and secret.

> Available in 7.1.1 or later

**Input Parameters:**

| Field | Type | Mandatory | Description |
|-------|------|-----------|-------------|
| `clientId` | String `<hash>` | required | Client ID |
| `clientSecret` | String `<hash>` | required | Client Secret |
| `scope` | String `{api, api.read-only}` | optional | Token scope |

**Return Parameters:**

| Field | Type | Description |
|-------|------|-------------|
| `accessToken` | String `<hash>` | Access token |
| `authorizationType` | Number `{3}` | Always `3` |
| `scope` | String | Scope of the token |
| `expiresIn` | Number | Expires in seconds |

**cURL Example:**
```bash
curl -b cookies.txt -H "Content-Type: application/json" -X POST \
  -d '{"clientId":"0396c250111dcaef02058007bb72217e","clientSecret":"de5cd1c51252a13854d6bd7ddeabbcf5","scope":"api"}' \
  http://192.168.1.1/api/auth.token.grant
```
```json
{
  "stat": "ok",
  "response": {
    "accessToken": "43c65216eb16d779092fc40b184a1794",
    "authorizationType": 3,
    "scope": "api",
    "expiresIn": 172800
  }
}
```

---

### `POST /api/auth.token.revoke`

Revoke an access token. **Admin Permission or self-revoke only.**

> Available in 7.1.1 or later

**Input Parameters:**

| Field | Type | Mandatory | Description |
|-------|------|-----------|-------------|
| `accessToken` | String `<hash>` | required | Token to revoke |

**cURL Example:**
```bash
curl -b cookies.txt -H "Content-Type: application/json" -X POST \
  -d '{"accessToken":"0396c250111dcaef02058007bb72217e"}' \
  http://192.168.1.1/api/auth.token.revoke
```
```json
{ "stat": "ok" }
```

---

### `POST /api/cmd.billing.newCycle`

Start a new billing cycle by Connection ID and SIM ID.

> Available in 8.1.0 or later

**Input Parameters:**

| Field | Type | Mandatory | Description |
|-------|------|-----------|-------------|
| `connId` | Number `<conn_id>` | required | WAN Connection ID |
| `simId` | Number `[1, 2]` | optional | SIM ID (`1` = SIM A, `2` = SIM B). Always send `1` for single-SIM models |

**cURL Example:**
```bash
curl -b cookies.txt -H "Content-Type: application/json" -X POST \
  -d '{"connId":4,"simId":1}' \
  http://192.168.1.1/api/cmd.billing.newCycle
```
```json
{ "stat": "ok" }
```

---

### `GET /api/cmd.carrier.scan`

Obtain the result of discovered cellular networks. Returns fail if the WAN connection does not support carrier scan.

> Available in 8.0.1 or later

**Input Parameters:**

| Field | Type | Mandatory | Description |
|-------|------|-----------|-------------|
| `connId` | Number `<conn_id>` | required | WAN connection ID to scan |
| `reference` | String `{yes, no}` | required | Whether to include current carrier config |

**Return Parameters:**

| Field | Type | Description |
|-------|------|-------------|
| `scanStatus` | String `{scanning, done}` | Scanning status |
| `timestamp` | Number | Timestamp of the carrier list |
| `list` | Array of `<Scan_Carrier_Obj>` | Discovered carriers |
| `reference` | Object `<Reference_Obj>` | Current configuration |

**`<Scan_Carrier_Obj>`:**

| Field | Type | Description |
|-------|------|-------------|
| `name` | String | Carrier name |
| `mobileType` | String `{2G, 3G, LTE}` | |
| `mcc` | String (3 digits) | Mobile Country Code |
| `mnc` | String (2–3 digits) | Mobile Network Code |
| `pcs` | Number `[0, 1]` | |

**`<Reference_Obj>` → `<In_Use_SIM_Obj>`:**

| Field | Type | Description |
|-------|------|-------------|
| `simId` | Number `{1, 2}` | Active SIM ID |
| `selectedCarrier` | Object / NULL | Selected network (`null` if auto) |

**cURL Example:**
```bash
curl -b cookies.txt \
  "http://192.168.1.1/api/cmd.carrier.scan?connId=4&reference=yes"
```
```json
{
  "stat": "ok",
  "response": {
    "scanStatus": "scanning",
    "list": [
      { "name": ".csl", "mobileType": "LTE", "mcc": "454", "mnc": "0", "pcs": 0 },
      { "name": "SMT HK", "mobileType": "LTE", "mcc": "454", "mnc": "6", "pcs": 0 }
    ],
    "reference": {
      "activeSim": { "simId": 1, "cellularNetwork": null }
    }
  }
}
```

---

### `POST /api/cmd.carrier.scan`

Trigger and obtain cellular network scan results.

> Available in 8.1.0 or later

**Input Parameters:**

| Field | Type | Mandatory | Description |
|-------|------|-----------|-------------|
| `action` | String `{start}` | optional | Trigger scan |
| `connId` | Number `<conn_id>` | required | WAN connection ID |
| `reference` | String `{yes, no}` | optional | Include current carrier config |

Return parameters are the same as `GET /api/cmd.carrier.scan`.

**cURL Example:**
```bash
curl -b cookies.txt -H "Content-Type: application/json" -X POST \
  -d '{"action":"start","connId":"4","reference":"yes"}' \
  http://192.168.1.1/api/cmd.carrier.scan
```

---

### `POST /api/cmd.carrier.select`

Update the cellular network carrier selection.

> Available in 8.0.1 or later

**Input Parameters:**

| Field | Type | Mandatory | Description |
|-------|------|-----------|-------------|
| `connId` | Number `<conn_id>` | required | WAN connection ID |
| `simId` | Number `{1, 2}` | optional | SIM to update |
| `selectedCarrier` | Object `<Carrier_Obj>` | required | Carrier to select |

**`<Carrier_Obj>`:**

| Field | Type | Mandatory | Description |
|-------|------|-----------|-------------|
| `mcc` | String (3 digits) | required | |
| `mnc` | String (2–3 digits) | required | |
| `pcs` | Number `[0, 1]` | required | |
| `name` | String | optional | |

**cURL Example:**
```bash
curl -b cookies.txt -H "Content-Type: application/json" -X POST \
  -d '{"connId":4,"selectedCarrier":{"mcc":"345","mnc":"23","pcs":0}}' \
  http://192.168.1.1/api/cmd.carrier.select
```
```json
{ "stat": "ok" }
```

---

### `POST /api/cmd.channelPci.lock`

Lock the connected LTE network to a specific channel and PCI. Returns fail if not supported.

> Available in 8.1.1 or later

**Input Parameters:**

| Field | Type | Mandatory | Description |
|-------|------|-----------|-------------|
| `connId` | Number `<conn_id>` | required | WAN connection ID |
| `sim` | Array of `<SIM_Obj>` | required | SIM channel/PCI settings |

**`<SIM_Obj>`:**

| Field | Type | Mandatory | Description |
|-------|------|-----------|-------------|
| `id` | Number `<sim_id>` | required | `1` = SIM A, `2` = SIM B |
| `value` | Object / NULL `<CH_PCI_Obj>` | required | Channel/PCI to lock; `null` to clear |

**`<CH_PCI_Obj>`:**

| Field | Type | Mandatory | Description |
|-------|------|-----------|-------------|
| `channel` | Number `[0, 65535]` | required | Channel to lock |
| `pci` | Number `[0, 65535]` | optional | PCI to lock |

**cURL Example:**
```bash
curl -b cookies.txt -H "Content-Type: application/json" -X POST \
  -d '{"connId":4,"sim":[{"id":1,"value":{"channel":1350,"pci":77}}]}' \
  http://192.168.1.1/api/cmd.channelPci.lock
```
```json
{ "stat": "ok" }
```

---

### `POST /api/cmd.channelPci.scan`

Scan discovered LTE cellular channel/PCI information. Provide `action=start` to trigger a rescan.

> Available in 8.1.1 or later

**Input Parameters:**

| Field | Type | Mandatory | Description |
|-------|------|-----------|-------------|
| `action` | String `{start}` | optional | Trigger rescan |
| `connId` | Number `<conn_id>` | required | WAN connection ID |

**Return Parameters:**

| Field | Type | Description |
|-------|------|-------------|
| `scanStatus` | String `{scanning, done}` | |
| `timestamp` | Number | Timestamp of the list |
| `list` | Array of `<CH_PCI_Obj>` | Discovered channel/PCI entries |

**`<CH_PCI_Obj>`:**

| Field | Type | Description |
|-------|------|-------------|
| `pci` | Number | Physical-layer Cell Identity |
| `earfcn` | Number | E-UTRA Absolute Radio-Frequency Channel Number |
| `cellUtranId` | Number | Cell UTRAN ID |
| `plmn` | Array of `<PLMN_Obj>` | Public land mobile network info |

**`<PLMN_Obj>`:**

| Field | Type | Description |
|-------|------|-------------|
| `mcc` | String (3 digits) | Mobile Country Code |
| `mnc` | String (2–3 digits) | Mobile Network Code |

**cURL Example:**
```bash
curl -b cookies.txt -H "Content-Type: application/json" -X POST \
  -d '{"action":"start","connId":4}' \
  http://192.168.1.1/api/cmd.channelPci.scan
```
```json
{
  "stat": "ok",
  "response": {
    "scanStatus": "scanning",
    "timestamp": 1577836800,
    "list": [
      {
        "pci": 371,
        "earfcn": 3000,
        "cellUtranId": 23574039,
        "plmn": [{ "mcc": "454", "mnc": "00" }]
      }
    ]
  }
}
```

---

### `POST /api/cmd.config.apply`

Apply pending configuration changes.

> Available in 7.1.1 or later

**Return Parameters:**

| Field | Type | Description |
|-------|------|-------------|
| `warning` | String | Warning message, if any |

**cURL Example:**
```bash
curl -b cookies.txt -H "Content-Type: application/json" -X POST \
  http://192.168.1.1/api/cmd.config.apply
```
```json
{ "stat": "ok" }
```

---

### `POST /api/cmd.config.discard`

Discard pending configuration changes.

> Available in 7.1.1 or later

**cURL Example:**
```bash
curl -b cookies.txt -H "Content-Type: application/json" -X POST \
  http://192.168.1.1/api/cmd.config.discard
```
```json
{ "stat": "ok" }
```

---

### `POST /api/cmd.port.poe.disable`

Disable PoE on a port. Returns fail if the device or port does not support PoE.

> Available in 8.1.1 or later

**Input Parameters:**

| Field | Type | Mandatory | Description |
|-------|------|-----------|-------------|
| `port` | Number / Object / Array | required | Single port ID, `<Port_Obj>`, or array of either |

**`<Port_Obj>`:**

| Field | Type | Mandatory | Description |
|-------|------|-----------|-------------|
| `id` | Number | required | Port ID |
| `moduleType` | String | optional (mandatory for modular devices) | Module type |
| `moduleId` | Number | optional (mandatory for modular devices) | Module ID |

**cURL Example:**
```bash
curl -b cookies.txt -H "Content-Type: application/json" -X POST \
  -d '{"port":[2,{"id":1,"moduleType":"E8","moduleId":2}]}' \
  http://192.168.1.1/api/cmd.port.poe.disable
```
```json
{ "stat": "ok" }
```

---

### `POST /api/cmd.port.poe.enable`

Enable PoE on a port. Same parameters as `cmd.port.poe.disable`.

> Available in 8.1.1 or later

**cURL Example:**
```bash
curl -b cookies.txt -H "Content-Type: application/json" -X POST \
  -d '{"port":[2,{"id":1,"moduleType":"E8","moduleId":2}]}' \
  http://192.168.1.1/api/cmd.port.poe.enable
```
```json
{ "stat": "ok" }
```

---

### `POST /api/cmd.sendUssd`

Send a USSD code, if a SIM card is present.

> Available in 8.1.0 or later

**Input Parameters:**

| Field | Type | Mandatory | Description |
|-------|------|-----------|-------------|
| `connId` | Number `<conn_id>` | required | WAN connection ID |
| `simId` | Number `<sim_id>` | optional | SIM ID; defaults to active SIM |
| `ussd` | String `{1234567890*#}` | required | USSD code |

**cURL Example:**
```bash
curl -b cookies.txt -H "Content-Type: application/json" -X POST \
  -d '{"connId":2,"ussd":"*109#"}' \
  http://192.168.1.1/api/cmd.sendUssd
```
```json
{
  "stat": "ok",
  "response": { "message": "Request is sent successfully" }
}
```

---

### `GET /api/cmd.sms.get`

Fetch SMS messages from the active SIM for a given connection.

> Available in 8.1.0 or later

**Input Parameters:**

| Field | Type | Mandatory | Description |
|-------|------|-----------|-------------|
| `connId` | Number `<conn_id>` | required | WAN connection ID |

**Return Parameters:**

| Field | Type | Description |
|-------|------|-------------|
| `connId` | Number | Connection ID |
| `simId` | Number `{1, 2}` | SIM ID |
| `sms` | Array of `<SMS_Obj>` | List of SMS messages |

**`<SMS_Obj>`:**

| Field | Type | Description |
|-------|------|-------------|
| `sender` | String | Sender |
| `message` | Array of `<Message_Obj>` | Messages from this sender |

**`<Message_Obj>`:**

| Field | Type | Description |
|-------|------|-------------|
| `id` | Number | Message ID |
| `date` | String | Date string |
| `timestamp` | Number | Unix timestamp |
| `length` | Number | Content length |
| `content` | String | SMS content |

**cURL Example:**
```bash
curl -b cookies.txt "http://192.168.1.1/api/cmd.sms.get?connId=6"
```
```json
{
  "stat": "ok",
  "response": {
    "connId": 6,
    "simId": 1,
    "sms": [
      {
        "sender": "988",
        "message": [
          { "id": 1, "date": "Feb 17 13:55", "timestamp": 1581774925, "length": "50", "message": "The is the 1st line SMS,\nand this is the 2nd line." }
        ]
      },
      {
        "sender": "+81325359875",
        "message": [
          { "id": 2, "date": "Feb 05 01:55", "timestamp": 1580867113, "length": "24", "message": "Multipart message part 1" },
          { "id": 6, "date": "Feb 05 01:55", "timestamp": 1580867113, "length": "24", "message": "Multipart message part 2" }
        ]
      }
    ]
  }
}
```

---

### `POST /api/cmd.sms.sendMessage`

Send an SMS message, if a SIM card is present.

> Available in 8.0.0 or later

**Input Parameters:**

| Field | Type | Mandatory | Description |
|-------|------|-----------|-------------|
| `connId` | Number `<conn_id>` | optional | WAN connection ID |
| `address` | String | required | Target address (must begin with `+`, followed by 2–15 digits; first digit cannot be `0`) |
| `content` | String | optional | SMS content |

**cURL Example:**
```bash
curl -b cookies.txt -H "Content-Type: application/json" -X POST \
  -d '{"address":"+85235984335","content":"SMS Content"}' \
  http://192.168.1.1/api/cmd.sms.sendMessage
```
```json
{ "stat": "ok" }
```

---

### `GET /api/cmd.ap` *(alpha)*

Returns the status of the device Access Point.

> Available in 7.0.2 or later

**Return Parameters:**

| Field | Type | Description |
|-------|------|-------------|
| `support` | Boolean | Whether the device supports AP |
| `enable` | Boolean | Whether AP is currently on |
| `wanDependent` | Boolean | *(Experimental)* Whether "Turn off AP when no Internet" is enabled |

**cURL Example:**
```bash
curl -b cookies.txt http://192.168.1.1/api/cmd.ap
```
```json
{
  "stat": "ok",
  "response": { "support": true, "enable": true, "wanDependent": true }
}
```

---

### `POST /api/cmd.ap` *(alpha)*

Switch the device Access Point on or off.

> Available in 7.0.2 or later

**Input Parameters:**

| Field | Type | Mandatory | Description |
|-------|------|-----------|-------------|
| `enable` | Boolean | required | `true` to turn on; `false` to turn off |

**cURL Example:**
```bash
curl -b cookies.txt -H "Content-Type: application/json" -X POST \
  -d '{"enable":true}' \
  http://192.168.1.1/api/cmd.ap
```
```json
{
  "stat": "ok",
  "response": { "support": true, "enable": true, "wanDependent": true }
}
```

---

### `POST /api/cmd.cellularModule.rescanNetwork`

Rescan the network for a cellular WAN connection.

> Available in 8.0.0 or later

**Input Parameters:**

| Field | Type | Mandatory | Description |
|-------|------|-----------|-------------|
| `connId` | Number `<conn_id>` | required | WAN connection ID |

**cURL Example:**
```bash
curl -b cookies.txt -H "Content-Type: application/json" -X POST \
  -d '{"connId":"4"}' \
  http://192.168.1.1/api/cmd.cellularModule.rescanNetwork
```
```json
{ "stat": "ok" }
```

---

### `POST /api/cmd.cellularModule.reset`

Reset the cellular module for a WAN connection.

> Available in 8.0.0 or later

**Input Parameters:**

| Field | Type | Mandatory | Description |
|-------|------|-----------|-------------|
| `connId` | Number `<conn_id>` | required | WAN connection ID |

**cURL Example:**
```bash
curl -b cookies.txt -H "Content-Type: application/json" -X POST \
  -d '{"connId":"4"}' \
  http://192.168.1.1/api/cmd.cellularModule.reset
```
```json
{ "stat": "ok" }
```

---

### `GET /api/cmd.wan.cellular`

Get enabled SIM and preferred SIM settings for a cellular WAN.

> Available in 8.0.0 or later

**Input Parameters:**

| Field | Type | Mandatory | Description |
|-------|------|-----------|-------------|
| `connId` | Number `<conn_id>` | required | WAN connection ID |

**Return Parameters:**

| Field | Type | Description |
|-------|------|-------------|
| `enabledSim` | Array of `{1, 2}` | SIMs in use |
| `preferredSim` | Number / NULL `{1, 2}` | Preferred SIM slot |

**cURL Example:**
```bash
curl -b cookies.txt "http://192.168.1.1/api/cmd.wan.cellular?connId=4"
```
```json
{
  "stat": "ok",
  "response": { "enabledSim": [1, 2], "preferredSim": 1 }
}
```

---

### `POST /api/cmd.wan.cellular`

Change the enabled SIM and preferred SIM for a cellular WAN.

> Available in 8.0.0 or later

**Input Parameters:**

| Field | Type | Mandatory | Description |
|-------|------|-----------|-------------|
| `connId` | Number `<conn_id>` | required | WAN connection ID |
| `enabledSim` | Array of `{1, 2}` | optional | SIMs to enable |
| `preferredSim` | Number / NULL `{1, 2}` | optional | Preferred SIM |

**cURL Example:**
```bash
curl -b cookies.txt -H "Content-Type: application/json" -X POST \
  -d '{"connId":4,"enabledSim":[1,2],"preferredSim":1}' \
  http://192.168.1.1/api/cmd.wan.cellular
```
```json
{ "stat": "ok" }
```

---

### `POST /api/cmd.wifi.connect`

Connect to a Wi-Fi SSID. If no stored profile exists, additional credentials are required.

> Available in 7.1.1 or later

**Input Parameters:**

| Field | Type | Mandatory | Description |
|-------|------|-----------|-------------|
| `connId` | Number `<conn_id>` | required | Wi-Fi WAN connection ID |
| `ssid` | String | required | SSID to connect |
| `securityPolicy` | String `{open, wep, wpa-eap, wpa-psk, 8021x}` | required | Security policy |
| `key` | String | optional | Key for WEP/WPA-PSK |
| `loginId` | String | optional | Login ID for EAP |
| `password` | String | optional | Password for EAP |
| `eapMethod` | String `{TTLS, PEAP}` | optional | EAP method |
| `eapPhase2` | String `{CHAP, MSCHAP, MSCHAPV2, PAP}` | optional | EAP phase 2 |
| `eapAuthenticationId` | String `{anonymous, credentials}` | optional | EAP outer identity |
| `preferredBssid` | String `<mac>` | optional | Preferred BSSID |

**cURL Example:**
```bash
curl -b cookies.txt -H "Content-Type: application/json" -X POST \
  -d '{"connId":1,"ssid":"Main SSID"}' \
  http://192.168.1.1/api/cmd.wifi.connect
```
```json
{ "stat": "ok" }
```

---

### `POST /api/cmd.wifi.disconnect`

Disconnect from a Wi-Fi SSID.

> Available in 7.1.1 or later

**Input Parameters:**

| Field | Type | Mandatory | Description |
|-------|------|-----------|-------------|
| `connId` | Number `<conn_id>` | required | Wi-Fi WAN connection ID |
| `ssid` | String | optional | SSID to disconnect; omit to disconnect current |

**cURL Example:**
```bash
curl -b cookies.txt -H "Content-Type: application/json" -X POST \
  -d '{"connId":1,"ssid":"Main SSID"}' \
  http://192.168.1.1/api/cmd.wifi.disconnect
```
```json
{ "stat": "ok" }
```

---

### `POST /api/cmd.wifi.forget`

Remove an SSID profile and disconnect if currently connected.

> Available in 7.1.1 or later

**Input Parameters:**

| Field | Type | Mandatory | Description |
|-------|------|-----------|-------------|
| `connId` | Number `<conn_id>` | required | Wi-Fi WAN connection ID |
| `ssid` | String | required | SSID to forget |
| `securityPolicy` | String `{open, wep, wpa-eap, wpa-psk, 8021x}` | required | Security policy |

**cURL Example:**
```bash
curl -b cookies.txt -H "Content-Type: application/json" -X POST \
  -d '{"connId":1,"ssid":"Main SSID","securityPolicy":"wpa-psk"}' \
  http://192.168.1.1/api/cmd.wifi.forget
```
```json
{ "stat": "ok" }
```

---

### `GET /api/cmd.wifi.result`

Get the last known Wi-Fi connection result.

> Available in 7.1.1 or later

**Input Parameters:**

| Field | Type | Mandatory | Description |
|-------|------|-----------|-------------|
| `connId` | Number `<conn_id>` | required | Wi-Fi WAN connection ID |

**Return Parameters:**

| Field | Type | Description |
|-------|------|-------------|
| `timestamp` | Number | Timestamp of last result |
| `result` | String `{CONNECTED, TIMEOUT, PSK_AUTH_FAIL, EAP_AUTH_FAIL, AP_NOT_FOUND, UNKNOWN_FAIL}` | Connection result |
| `bssid` | String `<mac>` | BSSID of connected AP |
| `ssid` | String | SSID of connected AP |
| `securityPolicy` | String | Security policy |
| `message` | String | Additional status info |

**cURL Example:**
```bash
curl -b cookies.txt "http://192.168.1.1/api/cmd.wifi.result?connId=1"
```
```json
{
  "stat": "ok",
  "response": {
    "result": "CONNECTED",
    "timestamp": 1529899328,
    "ssid": "Main SSID",
    "bssid": "A2:E5:B8:55:89:DF",
    "securityPolicy": "wpa-psk",
    "message": "connected to Main SSID (A2:E5:B8:55:89:DF)"
  }
}
```

---

### `GET /api/cmd.wifi.scan`

Discover nearby Wi-Fi access points.

> Available in 7.1.1 or later

**Input Parameters:**

| Field | Type | Mandatory | Description |
|-------|------|-----------|-------------|
| `connId` | Number `<conn_id>` | required | Wi-Fi WAN connection ID |
| `infoType` | String `{status, config}` | optional | Additional info to include |
| `sortBy` | String `{name, security, signal, channel}` | optional | Sort field |
| `sortOrder` | String `{asc, desc}` | optional | Sort order |

**Return Parameters — Array of `<Wifi_Obj>`:**

| Field | Type | Description |
|-------|------|-------------|
| `ssid` | String | SSID |
| `bssid` | String `<mac>` | BSSID |
| `signal` | Number | Signal in dBm *(deprecated in 8.1.0)* |
| `signalStrength` | Number | Signal in dBm *(introduced in 8.1.0)* |
| `signalLevel` | Number `[0, 5]` | Signal level *(introduced in 8.1.0)* |
| `channel` | Number | Channel |
| `securityPolicy` | String | Security policy |
| `status` | Object `<Status_Obj>` | Status info |
| `config` | Object `<Config_Obj>` | Config info |

**`<Status_Obj>`:** `inUse` (Boolean), `connected` (Boolean)

**`<Config_Obj>`:** `profileId` (Number), `automatic` (Boolean)

**cURL Example:**
```bash
curl -b cookies.txt "http://192.168.1.1/api/cmd.wifi.scan?connId=1&infoType=status"
```
```json
{
  "stat": "ok",
  "response": [
    {
      "ssid": "Main SSID",
      "bssid": "A2:E5:B8:55:89:DF",
      "signal": -68,
      "channel": 10,
      "securityPolicy": "wpa-psk",
      "status": { "inUse": true, "connected": true }
    }
  ]
}
```

---

### `POST /api/config.gpio` *(beta)*

Get and update GPIO configuration. Returns the updated config. Passing an empty `list` returns current config without making changes.

> Available in 8.1.1 or later

**Input Parameters:**

| Field | Type | Mandatory | Description |
|-------|------|-----------|-------------|
| `list` | Array of `<GPIO_Obj>` | optional | GPIO configs to update |
| `reference` | Boolean | optional | Include GPIO reference |

**`<GPIO_Obj>` (input):**

| Field | Type | Mandatory | Description |
|-------|------|-----------|-------------|
| `id` | Number | required | GPIO ID |
| `enable` | Boolean | optional | Enable GPIO |
| `type` | String `{digital_input, digital_output, analog_input}` | optional | GPIO type |
| `mode` | String | optional | Mode depends on type (see below) |
| `delay` | Number `[1, 3600]` | optional | Delay (input types only) |

**Mode values by type:**
- `digital_input`: `{input_sensing, ignition_sensing}`
- `digital_output`: `{wan_status}`
- `analog_input`: `{input_sensing, voltage_measurement, analog_testing}`

**cURL Example:**
```bash
curl -b cookies.txt -H "Content-Type: application/json" -X POST \
  -d '{"list":[{"id":1,"enable":true,"type":"digital_output","mode":"toggle_high"},{"id":2,"enable":true,"type":"digital_input","mode":"input_sensing","delay":3}]}' \
  http://192.168.1.1/api/config.gpio
```
```json
{
  "stat": "ok",
  "response": {
    "1": { "enable": true, "type": "digital_output", "mode": "toggle_high" },
    "2": { "enable": true, "type": "digital_input", "mode": "input_sensing", "delay": 3 },
    "order": [1, 2]
  }
}
```

---

### `GET /api/config.ssid.profile`

Get SSID profile information.

> Available in 7.1.1 or later

**Input Parameters:**

| Field | Type | Mandatory | Description |
|-------|------|-----------|-------------|
| `id` | Array of `<ssid_profile_id>` | optional | Profile IDs to list; omit to return all |

**Return Parameters — `<SSID_Profile_Obj>`:**

| Field | Type | Description |
|-------|------|-------------|
| `name` | String | SSID |
| `enable` | Boolean | Profile enabled |
| `vlanId` | Number | VLAN ID (absent if using LAN) |
| `captivePortal` | Boolean | Captive portal enabled |
| `incontrolManaged` | Boolean | Managed by InControl |
| `broadcast` | Boolean | SSID broadcast |
| `security` | Object `<SSID_Security_Obj>` | Security settings |

**`<SSID_Security_Obj>`:** `policy` (`WPA2 Personal` / `WPA/WPA2 Personal`), `wpa2Personal` / `wpaWpa2Personal` (`<WPA2_Personal_Obj>`)

**`<WPA2_Personal_Obj>`:** `fastTransition` (Boolean), `key` (String)

**cURL Example:**
```bash
curl -b cookies.txt "http://192.168.1.1/api/config.ssid.profile?id=1&id=2"
```
```json
{
  "stat": "ok",
  "response": {
    "1": {
      "name": "Main SSID", "enable": true, "captivePortal": true, "incontrolManaged": false,
      "broadcast": true, "security": { "policy": "WPA2 Personal", "wpa2Personal": { "fastTransition": true, "key": "pas53or2" } }
    },
    "2": {
      "name": "Guest SSID", "enable": true, "captivePortal": true, "incontrolManaged": false,
      "broadcast": true, "vlanId": 1, "security": { "policy": "WPA2 Personal", "wpa2Personal": { "fastTransition": false, "key": "pass3ord" } }
    },
    "order": [1, 2]
  }
}
```

---

### `POST /api/config.ssid.profile`

Update an SSID profile. Only provided fields are modified.

> Available in 7.1.1 or later

**Input Parameters:**

| Field | Type | Mandatory | Description |
|-------|------|-----------|-------------|
| `action` | String `{update}` | required | |
| `id` | Number | required | Profile ID to update |
| `name` | String | optional | SSID |
| `enable` | Boolean | optional | Enable/disable |
| `vlanId` | Number | optional | VLAN ID |
| `broadcast` | Boolean | optional | Broadcast SSID |
| `security` | Object | optional | Security settings |

**cURL Example:**
```bash
curl -b cookies.txt -H "Content-Type: application/json" -X POST \
  -d '{"action":"update","id":"1","enable":true,"security":{"wpa2Personal":{"key":"thisIsNewPassword"}}}' \
  http://192.168.1.1/api/config.ssid.profile
```
```json
{
  "stat": "ok",
  "response": {
    "1": {
      "name": "Main SSID", "enable": true, "captivePortal": true, "incontrolManaged": false,
      "broadcast": true, "security": { "policy": "WPA2 Personal", "wpa2Personal": { "fastTransition": true, "key": "thisIsNewPassword" } }
    },
    "order": [1]
  }
}
```

---

### `POST /api/config.wan.connection` *(beta)*

Update WAN connection settings. Only provided fields are modified.

> Available in firmware 8 or later

**Input Parameters:**

| Field | Type | Mandatory | Description |
|-------|------|-----------|-------------|
| `action` | String `{update}` | required | |
| `list` | Array of `<WAN_Config_Obj>` | required | WAN connections to update |

**`<WAN_Config_Obj>`** (key fields):

| Field | Type | Description |
|-------|------|-------------|
| `id` | Number `<conn_id>` | WAN connection ID |
| `name` | String | Connection name |
| `enable` | Boolean | Enable/disable |
| `schedule` | Number / NULL | Schedule ID; `null` to disable |
| `connection` | Object `<Connection_Obj>` | Connection settings |
| `modem` | Object `<Modem_Obj>` | Modem settings (modem type only) |
| `cellular` | Object `<Cellular_Obj>` | Cellular settings |
| `wifi` | Object `<Wifi_Obj>` | Wi-Fi WAN settings |
| `physical` | Object `<Physical_Obj>` | Physical settings |
| `healthcheck` | Object `<Healthcheck_Obj>` | Health check settings |
| `bandwidthAllowanceMonitor` | Object | Bandwidth monitor |
| `multipleIp` | Array of `<ipv4>` | Additional IPs |
| `ddns` | Object `<DDNS_Obj>` | DDNS settings |

**Connection Method Types** (`connection.method.type`):
`staticIp`, `dhcp`, `pppoe`, `l2tp`, `gre`, `openvpn`

**Healthcheck Methods** (`healthcheck.method.type`):
`ping`, `nslookup`, `http`, `smartcheck`, `openvpn`

**cURL Example:**
```bash
curl -b cookies.txt -H "Content-Type: application/json" -X POST \
  -d '{"action":"update","list":[{"id":1,"enable":true}]}' \
  http://192.168.1.1/api/config.wan.connection
```

---

### `POST /api/config.wan.connection.priority`

Change the priority of WAN connections.

> Available in 7.1.1 or later

**Input Parameters:**

| Field | Type | Mandatory | Description |
|-------|------|-----------|-------------|
| `instantActive` | Boolean | optional | Apply immediately if `true`; otherwise pending |
| `list` | Array of `<WAN_Config_Priority_Obj>` | optional | Priority updates |

**`<WAN_Config_Priority_Obj>` (input):**

| Field | Type | Mandatory | Description |
|-------|------|-----------|-------------|
| `connId` | Number | required | WAN connection ID |
| `priority` | Number | optional | Priority |
| `enable` | Boolean | optional | Enable/disable |

**cURL Example:**
```bash
curl -b cookies.txt -H "Content-Type: application/json" -X POST \
  -d '{"instantActive":true,"list":[{"connId":1,"priority":1},{"connId":2,"priority":2}]}' \
  http://192.168.1.1/api/config.wan.connection.priority
```
```json
{
  "stat": "ok",
  "response": {
    "1": { "name": "WAN 1", "priority": 1, "enable": true },
    "2": { "name": "WAN 2", "priority": 2, "enable": true },
    "order": [1, 2]
  }
}
```

---

### `GET /api/info.firmware`

Retrieve firmware information. Can be called before login (returns current firmware version only).

> Available in 7.1.1 or later

**Return Parameters:**

| Field | Type | Description |
|-------|------|-------------|
| `order` | Array | Firmware IDs in order |
| `<fw_id>` | Object `<Firmware_Obj>` | Firmware info |

**`<Firmware_Obj>`:**

| Field | Type | Description |
|-------|------|-------------|
| `version` | String | Firmware version |
| `bootable` | Boolean | Bootable or not |
| `inUse` | Boolean | Currently running |

**cURL Example:**
```bash
curl -b cookies.txt http://192.168.1.1/api/info.firmware
```
```json
{
  "stat": "ok",
  "response": {
    "1": { "version": "7.0.3 build 2765", "bootable": true, "inUse": false },
    "2": { "version": "7.1.0 build 2860", "bootable": true, "inUse": true },
    "order": [1, 2]
  }
}
```

---

### `GET /api/info.location`

Get GPS data and location information.

> Available in 8.0.1 or later

**Return Parameters:**

| Field | Type | Description |
|-------|------|-------------|
| `gps` | Boolean | GPS signal valid |
| `location` | Object `<GPS_Location_Obj>` | Location data |

**`<GPS_Location_Obj>`:**

| Field | Type | Description |
|-------|------|-------------|
| `latitude` | Number | |
| `longitude` | Number | |
| `altitude` | Number | |
| `speed` | Number | |
| `heading` | Number | |
| `pdop` | Number | Position Dilution Of Precision |
| `hdop` | Number | Horizontal Dilution Of Precision |
| `vdop` | Number | Vertical Dilution Of Precision |
| `timestamp` | Number | Unix timestamp |

**cURL Example:**
```bash
curl -b cookies.txt http://192.168.1.1/api/info.location
```
```json
{
  "stat": "ok",
  "response": {
    "gps": true,
    "location": {
      "latitude": 22.340134, "longitude": 114.152588, "altitude": 55.1,
      "speed": 0.026751, "heading": 356.887,
      "pdop": 1.3, "hdop": 1, "vdop": 0.8,
      "timestamp": 1311972720
    }
  }
}
```

---

### `GET /api/status.client`

Retrieve connected client details including name, MAC, IP, signal, and more.

> Available in 8.0.1 or later

**Input Parameters:**

| Field | Type | Mandatory | Description |
|-------|------|-----------|-------------|
| `vlanId` | Number | optional | Filter by VLAN ID |
| `activeOnly` | String `{yes, no}` | optional | Filter by active/inactive |
| `connectionType` | Array `{ethernet, wireless, pptp, stroute, l2tp, openvpn, pepvpn, other}` | optional | Filter by type |
| `size` | Number `[1, 10000000]` | optional | Max clients to return (default: 1000) |
| `outputWeight` | String `{full, normal, lite}` | optional | Controls fields returned |
| `infoType` | Array | optional | Override `outputWeight` with specific fields |

**Return Parameters — `<Client_Obj>`:**

| Field | Type | Description |
|-------|------|-------------|
| `ip` | String | IP address |
| `connectionType` | String | Connection type |
| `lease` | Object `<Lease_Obj>` | Lease info (ethernet/wireless only) |
| `name` | String | Client name |
| `mac` | String `<mac>` | MAC address |
| `bssid` | String | BSSID (wireless only) |
| `vlanId` | Number | VLAN ID (absent for untagged LAN) |
| `essid` | String | SSID (wireless only) |
| `active` | Boolean | Active state |
| `signal` | Object `<Signal_Detail_Obj>` | Signal strength/level *(fw 8.1.0+)* |
| `speed` | Object `<Bandwidth_Obj>` | Speed info |

**cURL Example:**
```bash
curl -b cookies.txt "http://192.168.1.1/api/status.client?connectionType=ethernet&connectionType=wireless"
```

---

### `GET /api/status.lan.profile`

Get LAN/VLAN status.

> Available in 7.1.0 or later

**Input Parameters:**

| Field | Type | Mandatory | Description |
|-------|------|-----------|-------------|
| `id` | Array of `<lan_id>` | optional | LAN IDs to return; omit for all |

**Return Parameters — `<LAN_Status_Obj>`:**

| Field | Type | Description |
|-------|------|-------------|
| `name` | String | LAN/VLAN name |
| `vlanId` | Number `[1, 4094]` | VLAN ID (absent if no VLAN) |
| `ip` | String | IP address |
| `mask` | Number | Subnet mask |

**cURL Example:**
```bash
curl -b cookies.txt http://192.168.1.1/api/status.lan.profile
```
```json
{
  "stat": "ok",
  "response": {
    "0": { "ip": "10.6.1.231", "mask": 16 },
    "1": { "name": "Name 1", "ip": "10.6.1.231", "vlanId": 164, "mask": 16 },
    "order": [0, 1]
  }
}
```

---

### `GET /api/status.pepvpn` *(beta)*

Get PepVPN / SpeedFusion status.

> Available in 7.1.0 or later

**Input Parameters:**

| Field | Type | Mandatory | Description |
|-------|------|-----------|-------------|
| `infoType` | Array `{profile, peer, tunnel}` | optional | Information to retrieve |
| `lite` | String `{yes, no}` | optional | Return limited data if `yes` |
| `tunnelOption` | Array of `<peer_id>` | optional | Peer IDs for tunnel info |
| `start` | Number | optional | Start index for peer list |
| `size` | Number | optional | Number of peers to return |
| `searchPattern` | String | optional | Filter peers by string |
| `serialNumber` | String | optional | Filter by serial number |

**Return Parameters:**

| Field | Type | Description |
|-------|------|-------------|
| `profile` | Object `<Profile_Order_Obj>` | PepVPN profile info |
| `peer` | Array of `<Peer_Obj>` | Peer info |
| `tunnel` | Object `<Tunnel_Order_Obj>` | Tunnel stats (if requested) |

**Tunnel WAN States:**
`INVALID`, `WAN_DOWN`, `WAN_DISABLED`, `DETECTING`, `FAILURE`, `REMOTE_FAILURE`, `COLD`, `STANDBY`, `PSUSPD`, `D-SUSPD`, `USUSPD`, `P-ACTIV`, `D-ACTIV`, `U-ACTIV`, `ACTIVE`

**cURL Example:**
```bash
curl -b cookies.txt \
  "http://192.168.1.1/api/status.pepvpn?infoType=profile&infoType=peer&lite=yes&tunnelOption=1-1"
```

---

### `GET /api/status.wan.connection`

Get WAN connection status.

> Available in 8.0.0 or later

**Input Parameters:**

| Field | Type | Mandatory | Description |
|-------|------|-----------|-------------|
| `id` | Array of `<conn_id>` | optional | WAN IDs to return; omit for all |
| `lite` | String `{yes, no}` | optional | Return limited data if `yes` |

**Return Parameters — `<WAN_Status_Obj>`:**

| Field | Type | Description |
|-------|------|-------------|
| `name` | String | WAN name |
| `statusLed` | String `{empty, gray, red, yellow, green, flash}` | LED color |
| `asLan` | Boolean | WAN-as-LAN mode |
| `enable` | Boolean | Enabled state |
| `locked` | Boolean | Locked state |
| `scheduledOff` | Boolean | Scheduled off (appears only when applicable) |
| `message` | String | Status message |
| `uptime` | Number | Uptime in seconds |
| `type` | String | WAN type |
| `priority` | Number | Priority (absent if disabled) |
| `ip` | String | IP address |
| `mask` | Number | Subnet mask |
| `gateway` | String | Gateway |
| `method` | String `{dhcp, static}` | Connection method |
| `routingMode` | String `{NAT, IP Forwarding}` | Routing mode |
| `dns` | Array of `<ipv4>` | DNS servers |
| `mtu` | Number | MTU |
| `mac` | String | MAC address |
| `wireless` | Object `<Wifi_Obj>` | Wi-Fi details (Wi-Fi type only) |
| `modem` | Object `<Modem_Obj>` | Modem details (modem type only) |
| `cellular` | Object `<Gobi_Obj>` | Cellular details |
| `bandwidthAllowanceMonitor` | Object | Bandwidth monitor info |

**Signal Object (`<Signal_Obj>`) fields:**

| Field | Description |
|-------|-------------|
| `rssi` | Received Signal Strength Indicator |
| `sinr` | Signal to Interference plus Noise Ratio |
| `snr` | Signal-to-noise ratio |
| `ecio` | Energy to Interference Ratio |
| `rsrp` | Reference Signal Received Power |
| `rsrq` | Reference Signal Received Quality |
| `strength` | Wi-Fi signal strength |

**cURL Example:**
```bash
curl -b cookies.txt http://192.168.1.1/api/status.wan.connection
```

---

*Documentation sourced from the Peplink Router API Documentation for Firmware 8.1.1.*

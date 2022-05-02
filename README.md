# PHOTOBOOTH API

---
## ENDPOINT LIST

- `/api/generate-image`
    - **Usage:** Process and generate result image
    - **Request Method:** `POST`
    - **Request parameter:**

        | TYPE | PARAMETER | VALUES |
        |------|-----------|--------|
        |   BODY   |   tx_id        |  string      |
        |   BODY   |   frame_id        | string       |

        E.g.
        ```
        {
            "tx_id": "001122",
            "frame_id": 4
        }

        ```
    - **Response:**
        | TYPE | PARAMETER | VALUES |
        |------|-----------|--------|
        |   BODY   |   status_code        |  int      |
        |   BODY   |   message        | string       |
        |   BODY   |   result_dir   | list of string |
        |   BODY    | error | string |

        E.g.
        ```
        #ON SUCCESS
        {
            "status_code": 200,
            "message": "Success",
            "result_dir": [
                /path/to/result/dir-1,
                /path/to/result/dir-2,
                /path/to/result/dir-3
            ],
            "error": "null"
        }

        #ON FAILURE
        {
            "status_code": 503,
            "message": "Cannot process the image",
            "error": "Your python error message"
        }
        ```

- `/api/get-frame`
    - **Usage:** list available frame
    - **Request Method:** `GET`
    - **Request parameter:** None
    - **Response:**
        | TYPE | PARAMETER | VALUES |
        |------|-----------|--------|
        |   BODY   |   status_code        |  int      |
        |   BODY   |   message        | string       |
        |   BODY   |   frame_list   | list of string |

        E.g.
        ```
        {
            "status_code": 200,
            "message": "Success",
            "result_dir": [
                /path/to/result/frame-1,
                /path/to/result/frame-2,
                /path/to/result/frame-3
            ]
        }
        ```

- `/api/send-email`
    - **Usage:** Send final image and gif to email
    - **Request Method:** `POST`
    - **Request parameter:**

        | TYPE | PARAMETER | VALUES |
        |------|-----------|--------|
        |   BODY   |   tx_id        |  string      |
        |   BODY   |   effect        | string       |
        |   BODY   |   email        | string       |
        |   BODY   |   recipient_name        | string       |

        E.g.
        ```
        {
            "tx_id": "001122",
            "frame_id": "winter",
            "email": "gelargelur@gmail.com",
            "recipient_name": "Gelar"
        }

        ```
    - **Response:**
        | TYPE | PARAMETER | VALUES |
        |------|-----------|--------|
        |   BODY   |   status_code        |  int      |
        |   BODY   |   message        | string       |
        |   BODY    | error | string |

        E.g.
        ```
        #ON SUCCESS
        {
            "status_code": 200,
            "message": "Success",
            "error": "null"
        }

        #ON FAILURE
        {
            "status_code": 503,
            "message": "Failed to send email",
            "error": "Your python error message"
        }
        ```

- `/api/print-image`
    - **Usage:** Printe the chosen image
    - **Request Method:** `POST`
    - **Request parameter:**

        | TYPE | PARAMETER | VALUES |
        |------|-----------|--------|
        |   BODY   |   tx_id        |  string      |
        |   BODY   |   effect        | string       |

        E.g.
        ```
        {
            "tx_id": "001122",
            "frame_id": "winter",
        }

        ```
    - **Response:**
        | TYPE | PARAMETER | VALUES |
        |------|-----------|--------|
        |   BODY   |   status_code        |  int      |
        |   BODY   |   message        | string       |
        |   BODY    | error | string |

        E.g.
        ```
        #ON SUCCESS
        {
            "status_code": 200,
            "message": "Success",
            "error": "null"
        }

        #ON FAILURE
        {
            "status_code": 503,
            "message": "Failed to print email",
            "error": "Your python error message"
        }
        ```